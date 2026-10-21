from typing import Any, Literal

import pandas as pd
from pydantic import BaseModel, Field


# ── Parameter schemas (used to generate OpenAI tool schemas via Pydantic) ─────

class _SalesFilters(BaseModel):
    category: str | None = Field(None, description="Filter by product category (case-insensitive).")
    date_from: str | None = Field(None, description="Start date inclusive (YYYY-MM-DD).")
    date_to: str | None = Field(None, description="End date inclusive (YYYY-MM-DD).")
    gender: Literal["male", "female"] | None = Field(None, description="Filter by buyer gender (male or female).")
    min_age: int | None = Field(None, description="Minimum buyer age (inclusive).")
    max_age: int | None = Field(None, description="Maximum buyer age (inclusive).")
    warehouse_id: int | None = Field(None, description="Filter by warehouse ID (1 to 20).")


class _TopProductsParams(_SalesFilters):
    limit: int = Field(5, description="Number of top products to return (default 5).")


class _RecentSalesParams(_SalesFilters):
    limit: int = Field(5, description="Number of recent sales to return (default 5).")


class _SalesOverviewParams(_SalesFilters):
    pass


class _SalesRevenueParams(_SalesFilters):
    pass


class _WarehouseStockParams(BaseModel):
    warehouse_id: int = Field(..., description="Numeric warehouse ID (1–20). Required.")
    product_name: str | None = Field(None, description="Filter by product name (partial match, case-insensitive). Omit to get all products.")
    product_id: int | None = Field(None, description="Filter by exact product ID. Omit to get all products.")
    limit: int = Field(10, description="Maximum number of products to return (default 10).")


class _LookupWarehousesParams(BaseModel):
    name: str | None = Field(None, description="Partial warehouse name to search for (case-insensitive).")
    city: str | None = Field(None, description="City name to search for (case-insensitive).")
    warehouse_id: int | None = Field(None, description="Exact warehouse ID if already known.")
    user_id: int | None = Field(None, description="ID of the responsible user — returns the warehouse(s) assigned to them.")


class _LookupUsersParams(BaseModel):
    user_ids: list[int] = Field(..., description="List of user IDs to look up.")


class _FindUsersParams(BaseModel):
    name: str = Field(..., description="Full or partial name (case-insensitive), matched against first and last name.")


class _UserPurchasesParams(BaseModel):
    user_id: int = Field(..., description="Numeric ID of the user.")
    limit: int = Field(10, description="Maximum number of purchases to return (default 10).")


class _TopWarehousesParams(BaseModel):
    limit: int = Field(5, description="Number of top warehouses to return (default 5).")


# ── Schema helper ──────────────────────────────────────────────────────────────

def _tool_schema(name: str, description: str, model: type[BaseModel]) -> dict:
    params = model.model_json_schema()
    params.pop("title", None)
    params.pop("$defs", None)
    return {
        "type": "function",
        "function": {"name": name, "description": description, "parameters": params},
    }


# ── Filter helper ──────────────────────────────────────────────────────────────

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


# ── Tools ──────────────────────────────────────────────────────────────────────

def make_tools(
    sales_df: pd.DataFrame,
    users_df: pd.DataFrame,
    products_map: dict[int, dict],
    warehouse_service=None,
    user_role: str = "admin",
    user_id: int | None = None,
) -> tuple[dict[str, Any], list[dict]]:
    """Return (tools_map, tool_schemas) for the OpenAI chat completions API."""

    _is_restricted = user_role == "user"

    # Warehouse assigned to this user — only relevant when role is "user"
    _user_warehouse_id: int | None = None
    if _is_restricted and warehouse_service and user_id:
        for w in warehouse_service.all():
            if w.get("userId") == user_id:
                _user_warehouse_id = w["id"]
                break

    def _params(**kwargs) -> dict[str, Any]:
        return {k: v for k, v in kwargs.items() if v is not None}

    def top_products(limit=5, category=None, date_from=None, date_to=None,
                     gender=None, min_age=None, max_age=None, warehouse_id=None):
        filtered = _apply_filters(
            sales_df,
            _params(category=category, date_from=date_from, date_to=date_to,
                    gender=gender, min_age=min_age, max_age=max_age, warehouse_id=warehouse_id),
            users_df, products_map,
        )
        top = (
            filtered.groupby("productId")["quantity"]
            .sum().sort_values(ascending=False).head(limit)
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

    def recent_sales(limit=5, category=None, date_from=None, date_to=None,
                     gender=None, min_age=None, max_age=None, warehouse_id=None):
        filtered = _apply_filters(
            sales_df,
            _params(category=category, date_from=date_from, date_to=date_to,
                    gender=gender, min_age=min_age, max_age=max_age, warehouse_id=warehouse_id),
            users_df, products_map,
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

    def sales_overview(category=None, date_from=None, date_to=None,
                       gender=None, min_age=None, max_age=None, warehouse_id=None):
        filtered = _apply_filters(
            sales_df,
            _params(category=category, date_from=date_from, date_to=date_to,
                    gender=gender, min_age=min_age, max_age=max_age, warehouse_id=warehouse_id),
            users_df, products_map,
        )
        categorized = filtered.copy()
        categorized["category"] = categorized["productId"].map(
            lambda pid: products_map.get(int(pid), {}).get("category", "Unknown")
        )
        top_cats = (
            categorized.groupby("category")["quantity"]
            .sum().sort_values(ascending=False).head(5)
        )
        return {
            "date_range": {
                "from": filtered["date"].min() if not filtered.empty else None,
                "to": filtered["date"].max() if not filtered.empty else None,
            },
            "top_categories": [
                {"category": cat, "total_sold": int(qty)} for cat, qty in top_cats.items()
            ],
            "total_orders": int(len(filtered)),
            "total_quantity_sold": int(filtered["quantity"].sum()) if not filtered.empty else 0,
        }

    def warehouse_stock(warehouse_id, product_name=None, product_id=None, limit=10):
        if warehouse_service is None:
            return [{"error": "Warehouse service unavailable."}]
        if _is_restricted and warehouse_id != _user_warehouse_id:
            return [{"error": "Access denied: you can only view stock for your own warehouse."}]
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

    def lookup_warehouses(name=None, city=None, warehouse_id=None, user_id=None):
        if warehouse_service is None:
            return [{"error": "Warehouse service unavailable."}]
        if _is_restricted:
            if _user_warehouse_id is None:
                return [{"error": "You have no warehouse assigned."}]
            return [w for w in warehouse_service.all() if w["id"] == _user_warehouse_id]
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

    def lookup_users(user_ids):
        if users_df.empty:
            return []
        result = []
        for uid in user_ids:
            row = users_df[users_df["id"] == uid]
            if not row.empty:
                result.append(row.iloc[0].dropna().to_dict())
        return result

    def find_users(name):
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

    def sales_revenue(category=None, date_from=None, date_to=None,
                      gender=None, min_age=None, max_age=None, warehouse_id=None):
        filtered = _apply_filters(
            sales_df,
            _params(category=category, date_from=date_from, date_to=date_to,
                    gender=gender, min_age=min_age, max_age=max_age, warehouse_id=warehouse_id),
            users_df, products_map,
        )
        total_revenue = 0.0
        category_revenue: dict[str, float] = {}
        for _, row in filtered.iterrows():
            prod = products_map.get(int(row["productId"]), {})
            price = prod.get("price") or 0.0
            revenue = price * int(row["quantity"])
            total_revenue += revenue
            cat = prod.get("category", "Unknown")
            category_revenue[cat] = category_revenue.get(cat, 0.0) + revenue
        top_cats = sorted(category_revenue.items(), key=lambda x: x[1], reverse=True)[:5]
        return {
            "total_revenue": round(total_revenue, 2),
            "total_orders": int(len(filtered)),
            "revenue_by_category": [
                {"category": cat, "revenue": round(rev, 2)} for cat, rev in top_cats
            ],
            "date_range": {
                "from": filtered["date"].min() if not filtered.empty else None,
                "to": filtered["date"].max() if not filtered.empty else None,
            },
        }

    def user_purchases(user_id, limit=10):
        filtered = sales_df[
            (sales_df["status"] == "completed") & (sales_df["userId"] == user_id)
        ]
        result = []
        for _, row in filtered.sort_values("date", ascending=False).head(limit).iterrows():
            prod = products_map.get(int(row["productId"]), {})
            price = prod.get("price") or 0.0
            qty = int(row["quantity"])
            result.append({
                "date": row["date"],
                "product": prod.get("title", f"Product {int(row['productId'])}"),
                "category": prod.get("category"),
                "quantity": qty,
                "unit_price": price,
                "total": round(price * qty, 2),
            })
        return result

    def top_warehouses(limit=5):
        if warehouse_service is None:
            return [{"error": "Warehouse service unavailable."}]
        if _is_restricted:
            return [{"error": "Access denied: warehouse rankings are only available to administrators."}]
        completed = sales_df[sales_df["status"] == "completed"]
        totals: dict[int, dict] = {}
        for _, row in completed.iterrows():
            wid = int(row["warehouseId"])
            prod = products_map.get(int(row["productId"]), {})
            price = prod.get("price") or 0.0
            qty = int(row["quantity"])
            if wid not in totals:
                totals[wid] = {"quantity": 0, "revenue": 0.0}
            totals[wid]["quantity"] += qty
            totals[wid]["revenue"] += price * qty
        warehouses_by_id = {w["id"]: w for w in warehouse_service.all()}
        ranked = sorted(totals.items(), key=lambda x: x[1]["quantity"], reverse=True)[:limit]
        return [
            {
                "warehouse_id": wid,
                "name": warehouses_by_id.get(wid, {}).get("name"),
                "city": warehouses_by_id.get(wid, {}).get("city"),
                "state": warehouses_by_id.get(wid, {}).get("state"),
                "total_sold": data["quantity"],
                "revenue": round(data["revenue"], 2),
            }
            for wid, data in ranked
        ]

    tools_map = {
        "top_products": top_products,
        "recent_sales": recent_sales,
        "sales_overview": sales_overview,
        "warehouse_stock": warehouse_stock,
        "lookup_warehouses": lookup_warehouses,
        "lookup_users": lookup_users,
        "find_users": find_users,
        "sales_revenue": sales_revenue,
        "user_purchases": user_purchases,
        "top_warehouses": top_warehouses,
    }

    tool_schemas = [
        _tool_schema("top_products",
            "Returns top products ranked by total quantity sold (best sellers). "
            "Use for questions about popular products, best sellers, or most sold items. "
            "Only apply the filters explicitly mentioned in the question.",
            _TopProductsParams),
        _tool_schema("recent_sales",
            "Returns the most recent individual sales transactions, sorted newest first. "
            "Use for questions about recent sales, the latest sale, or recent activity. "
            "Only apply the filters explicitly mentioned in the question.",
            _RecentSalesParams),
        _tool_schema("sales_overview",
            "Returns a high-level sales summary: total orders, total quantity, date range, and top categories. "
            "Use for general questions about overall sales performance or trends. "
            "Only apply the filters explicitly mentioned in the question.",
            _SalesOverviewParams),
        _tool_schema("warehouse_stock",
            "Returns stock levels for products in a specific warehouse, sorted by stock descending. "
            "Use for questions about inventory in a warehouse: which product has the most/least stock, "
            "or the stock level of a specific product in a given warehouse. "
            "Call lookup_warehouses first if you only have a warehouse name, not its numeric ID.",
            _WarehouseStockParams),
        _tool_schema("lookup_warehouses",
            "Returns warehouse details (id, name, city, state, userId) matching the search. "
            "The userId field is the user responsible for (assigned to) that warehouse. "
            "Use this to resolve a warehouse name or city to its numeric ID before querying stock. "
            "To find which warehouse a person is responsible for, first call find_users to get "
            "their user ID, then pass it here as user_id.",
            _LookupWarehousesParams),
        _tool_schema("lookup_users",
            "Returns profile information for a list of user IDs. "
            "Use this whenever you have a userId from any other tool result and need to know "
            "the user's name or other details.",
            _LookupUsersParams),
        _tool_schema("find_users",
            "Finds users whose name matches the search, returning their id and profile details. "
            "Use this to resolve a person's name to their user ID — for example before checking "
            "which warehouse a user is responsible for (pass the returned id to lookup_warehouses as user_id).",
            _FindUsersParams),
        _tool_schema("sales_revenue",
            "Returns total revenue and a breakdown by category, calculated as quantity × product price. "
            "Use for questions about money earned, revenue, income, or financial performance. "
            "Only apply the filters explicitly mentioned in the question.",
            _SalesRevenueParams),
        _tool_schema("user_purchases",
            "Returns the purchase history of a specific user, most recent first. "
            "Use for questions about what a specific user has bought, their spending, or order history. "
            "Call find_users first to resolve a name to a user_id if needed.",
            _UserPurchasesParams),
        _tool_schema("top_warehouses",
            "Returns warehouses ranked by total quantity sold, with revenue. "
            "Use for questions about which warehouse sells the most, warehouse performance comparisons, "
            "or overall warehouse rankings.",
            _TopWarehousesParams),
    ]

    return tools_map, tool_schemas
