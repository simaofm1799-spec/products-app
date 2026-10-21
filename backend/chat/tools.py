import inspect
import re
import types
from typing import Any, Callable, Literal, Union, get_args, get_origin

import pandas as pd


def _annotation_to_json(annotation) -> dict:
    if annotation is inspect.Parameter.empty:
        return {"type": "string"}

    origin = get_origin(annotation)
    args = get_args(annotation)

    # X | None  (Python 3.10+ UnionType) or Optional[X]
    is_union = (
        (hasattr(types, "UnionType") and isinstance(annotation, types.UnionType))
        or origin is Union
    )
    if is_union:
        non_none = [a for a in args if a is not type(None)]
        if non_none:
            return _annotation_to_json(non_none[0])

    # Literal["a", "b"] → enum
    if origin is Literal:
        return {"type": "string", "enum": list(args)}

    _MAP = {str: "string", int: "integer", float: "number", bool: "boolean"}
    if annotation in _MAP:
        return {"type": _MAP[annotation]}

    if origin is list:
        item = args[0] if args else str
        return {"type": "array", "items": _annotation_to_json(item)}

    return {"type": "string"}


def _parse_arg_docs(docstring: str) -> dict[str, str]:
    """Extract param descriptions from a Google-style Args: section."""
    result: dict[str, str] = {}
    if not docstring:
        return result
    in_args = False
    current: str | None = None
    for line in docstring.splitlines():
        if line.strip() == "Args:":
            in_args = True
            continue
        if not in_args:
            continue
        # New top-level section — stop
        if line and not line.startswith("    ") and line.strip():
            break
        m = re.match(r"    (\w+):\s*(.*)", line)
        if m:
            current = m.group(1)
            result[current] = m.group(2).strip()
        elif current and line.strip():
            result[current] += " " + line.strip()
    return result


def tool_schema(fn: Callable) -> dict:
    """Derive an OpenAI-format tool schema from a function's signature and docstring."""
    sig = inspect.signature(fn)
    doc = inspect.getdoc(fn) or ""
    description = re.split(r"\nArgs:", doc)[0].strip()
    param_docs = _parse_arg_docs(doc)

    properties: dict[str, dict] = {}
    for name, param in sig.parameters.items():
        schema = _annotation_to_json(param.annotation)
        if name in param_docs:
            schema["description"] = param_docs[name]
        properties[name] = schema

    return {
        "type": "function",
        "function": {
            "name": fn.__name__,
            "description": description,
            "parameters": {"type": "object", "properties": properties},
        },
    }


def _apply_filters(
    df: pd.DataFrame,
    params: dict[str, Any],
    users_df: pd.DataFrame,
    products_map: dict[int, dict],
) -> pd.DataFrame:
    filtered = df[df["status"] == "completed"].copy()

    needs_user_filter = any(key in params for key in ("min_age", "max_age", "gender"))
    if needs_user_filter:
        users = users_df.copy()
        if "min_age" in params:
            users = users[users["age"] >= params["min_age"]]
        if "max_age" in params:
            users = users[users["age"] <= params["max_age"]]
        if "gender" in params:
            users = users[users["gender"] == params["gender"]]
        filtered = filtered[filtered["userId"].isin(users["id"])]

    if "date_from" in params:
        filtered = filtered[filtered["date"] >= params["date_from"]]
    if "date_to" in params:
        filtered = filtered[filtered["date"] <= params["date_to"]]
    if "warehouse_id" in params:
        filtered = filtered[filtered["warehouseId"] == params["warehouse_id"]]
    if "category" in params:
        category_ids = {
            pid
            for pid, prod in products_map.items()
            if prod.get("category", "").lower() == params["category"].lower()
        }
        filtered = filtered[filtered["productId"].isin(category_ids)]

    return filtered


def make_tools(
    sales_df: pd.DataFrame,
    users_df: pd.DataFrame,
    products_map: dict[int, dict],
    warehouse_service=None,
) -> list:
    """Return the list of tool callables passed to the OpenAI SDK as tool schemas."""

    def _params(**kwargs) -> dict[str, Any]:
        return {k: v for k, v in kwargs.items() if v is not None}

    def top_products(
        limit: int = 5,
        category: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        gender: Literal["male", "female"] | None = None,
        min_age: int | None = None,
        max_age: int | None = None,
        warehouse_id: int | None = None,
    ) -> list[dict]:
        """Returns top products ranked by total quantity sold (best sellers).

        Use for questions about popular products, best sellers, or most sold items.
        Only apply the filters explicitly mentioned in the question.

        Args:
            limit: Number of top products to return (default 5).
            category: Filter by product category (case-insensitive).
            date_from: Start date inclusive (YYYY-MM-DD).
            date_to: End date inclusive (YYYY-MM-DD).
            gender: Filter by buyer gender (male or female).
            min_age: Minimum buyer age (inclusive).
            max_age: Maximum buyer age (inclusive).
            warehouse_id: Filter by warehouse ID (1 to 20).
        """
        filtered = _apply_filters(
            sales_df,
            _params(category=category, date_from=date_from, date_to=date_to,
                    gender=gender, min_age=min_age, max_age=max_age, warehouse_id=warehouse_id),
            users_df,
            products_map,
        )
        top = (
            filtered.groupby("productId")["quantity"]
            .sum()
            .sort_values(ascending=False)
            .head(limit)
        )
        return [
            {
                "category": products_map.get(int(pid), {}).get("category", "Unknown"),
                "product_id": int(pid),
                "title": products_map.get(int(pid), {}).get("title", f"Product {pid}"),
                "total_sold": int(qty),
            }
            for pid, qty in top.items()
        ]

    def recent_sales(
        limit: int = 5,
        category: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        gender: Literal["male", "female"] | None = None,
        min_age: int | None = None,
        max_age: int | None = None,
        warehouse_id: int | None = None,
    ) -> list[dict]:
        """Returns the most recent individual sales transactions, sorted newest first.

        Use for questions about recent sales, the latest sale, or recent activity.
        Only apply the filters explicitly mentioned in the question.

        Args:
            limit: Number of recent sales to return (default 5).
            category: Filter by product category (case-insensitive).
            date_from: Start date inclusive (YYYY-MM-DD).
            date_to: End date inclusive (YYYY-MM-DD).
            gender: Filter by buyer gender (male or female).
            min_age: Minimum buyer age (inclusive).
            max_age: Maximum buyer age (inclusive).
            warehouse_id: Filter by warehouse ID (1 to 20).
        """
        filtered = _apply_filters(
            sales_df,
            _params(category=category, date_from=date_from, date_to=date_to,
                    gender=gender, min_age=min_age, max_age=max_age, warehouse_id=warehouse_id),
            users_df,
            products_map,
        )
        users_by_id = {}
        if not users_df.empty:
            for _, u in users_df.iterrows():
                users_by_id[int(u["id"])] = u.dropna().to_dict()

        result = []
        for _, row in filtered.sort_values("date", ascending=False).head(limit).iterrows():
            prod = products_map.get(int(row["productId"]), {})
            user = users_by_id.get(int(row["userId"]), {})
            result.append({
                **{k: (int(v) if hasattr(v, "item") else v) for k, v in row.items()},
                "product": prod,
                "buyer": user,
            })
        return result

    def sales_overview(
        category: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        gender: Literal["male", "female"] | None = None,
        min_age: int | None = None,
        max_age: int | None = None,
        warehouse_id: int | None = None,
    ) -> dict:
        """Returns a high-level sales summary: total orders, total quantity, date range, and top categories.

        Use for general questions about overall sales performance or trends.
        Only apply the filters explicitly mentioned in the question.

        Args:
            category: Filter by product category (case-insensitive).
            date_from: Start date inclusive (YYYY-MM-DD).
            date_to: End date inclusive (YYYY-MM-DD).
            gender: Filter by buyer gender (male or female).
            min_age: Minimum buyer age (inclusive).
            max_age: Maximum buyer age (inclusive).
            warehouse_id: Filter by warehouse ID (1 to 20).
        """
        filtered = _apply_filters(
            sales_df,
            _params(category=category, date_from=date_from, date_to=date_to,
                    gender=gender, min_age=min_age, max_age=max_age, warehouse_id=warehouse_id),
            users_df,
            products_map,
        )
        total_orders = int(len(filtered))
        total_quantity = int(filtered["quantity"].sum()) if not filtered.empty else 0
        categorized = filtered.copy()
        categorized["category"] = categorized["productId"].map(
            lambda pid: products_map.get(int(pid), {}).get("category", "Unknown")
        )
        top_cats = (
            categorized.groupby("category")["quantity"]
            .sum()
            .sort_values(ascending=False)
            .head(5)
        )
        return {
            "date_range": {
                "from": filtered["date"].min() if not filtered.empty else None,
                "to": filtered["date"].max() if not filtered.empty else None,
            },
            "top_categories": [
                {"category": cat, "total_sold": int(qty)} for cat, qty in top_cats.items()
            ],
            "total_orders": total_orders,
            "total_quantity_sold": total_quantity,
        }

    def warehouse_stock(
        warehouse_id: int,
        product_name: str | None = None,
        product_id: int | None = None,
        limit: int = 10,
    ) -> list[dict]:
        """Returns stock levels for products in a specific warehouse, sorted by stock descending.

        Use for questions about inventory in a warehouse: which product has the most/least stock,
        or the stock level of a specific product in a given warehouse.
        Call lookup_warehouses first if you only have a warehouse name, not its numeric ID.

        Args:
            warehouse_id: Numeric warehouse ID (1–20). Required.
            product_name: Filter by product name (partial match, case-insensitive). Omit to get all products.
            product_id: Filter by exact product ID. Omit to get all products.
            limit: Maximum number of products to return (default 10).
        """
        if warehouse_service is None:
            return [{"error": "Warehouse service unavailable."}]

        if product_id is not None:
            candidates = [products_map[product_id]] if product_id in products_map else []
        elif product_name:
            q = product_name.lower()
            candidates = [p for p in products_map.values() if q in p.get("title", "").lower()]
        else:
            candidates = list(products_map.values())

        if not candidates:
            return [{"error": f"No product found matching '{product_name or product_id}'."}]

        return sorted(
            [
                {
                    "product_id": p["id"],
                    "product_name": p.get("title"),
                    "category": p.get("category"),
                    "stock": warehouse_service.get_stock(warehouse_id, p["id"]),
                }
                for p in candidates
            ],
            key=lambda x: x["stock"],
            reverse=True,
        )[:limit]

    def lookup_warehouses(
        name: str | None = None,
        city: str | None = None,
        warehouse_id: int | None = None,
        user_id: int | None = None,
    ) -> list[dict]:
        """Returns warehouse details (id, name, city, state, userId) matching the search.

        The userId field is the user responsible for (assigned to) that warehouse.
        Use this to resolve a warehouse name or city to its numeric ID before querying stock.
        Also useful when the user mentions a city or region instead of a warehouse name.
        To find which warehouse a person is responsible for, first call find_users to get
        their user ID, then pass it here as user_id.

        Args:
            name: Partial warehouse name to search for (case-insensitive).
            city: City name to search for (case-insensitive).
            warehouse_id: Exact warehouse ID if already known.
            user_id: ID of the responsible user — returns the warehouse(s) assigned to them.
        """
        if warehouse_service is None:
            return [{"error": "Warehouse service unavailable."}]
        warehouses = warehouse_service.all()
        if warehouse_id is not None:
            return [w for w in warehouses if w["id"] == warehouse_id]
        results = warehouses
        if user_id is not None:
            results = [w for w in results if w.get("userId") == user_id]
        if name:
            q = name.lower()
            results = [w for w in results if q in w.get("name", "").lower()]
        if city:
            q = city.lower()
            results = [w for w in results if q in w.get("city", "").lower()]
        return results

    def lookup_users(user_ids: list[int]) -> list[dict]:
        """Returns profile information for a list of user IDs.

        Use this whenever you have a userId from any other tool result and need to know
        the user's name or other details.

        Args:
            user_ids: List of user IDs to look up.
        """
        if users_df.empty:
            return []
        result = []
        for uid in user_ids:
            row = users_df[users_df["id"] == uid]
            if not row.empty:
                result.append(row.iloc[0].dropna().to_dict())
        return result

    def find_users(name: str) -> list[dict]:
        """Finds users whose name matches the search, returning their id and profile details.

        Use this to resolve a person's name to their user ID — for example before checking
        which warehouse a user is responsible for (pass the returned id to lookup_warehouses
        as user_id).

        Args:
            name: Full or partial name (case-insensitive), matched against first and last name.
        """
        if users_df.empty:
            return []
        query = name.lower().strip()
        result = []
        for _, user in users_df.iterrows():
            first = str(user.get("firstName", "") or "")
            last = str(user.get("lastName", "") or "")
            full = f"{first} {last}".strip().lower()
            if query in full or query in first.lower() or query in last.lower():
                result.append(user.dropna().to_dict())
        return result

    return [
        top_products, recent_sales, sales_overview, warehouse_stock,
        lookup_warehouses, lookup_users, find_users,
    ]
