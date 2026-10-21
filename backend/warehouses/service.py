import json
import math
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from common.config import LOW_STOCK_THRESHOLD
from products.query import filter_products, sort_products
from products.service import product_service
from warehouses.analytics import build_stock_report

_DATA_DIR = Path(__file__).parent.parent.parent / "data"
_WAREHOUSES_FILE = _DATA_DIR / "warehouses.json"
_SALES_FILE = _DATA_DIR / "sales.json"
_SALES_WINDOW_DAYS = 90

# Blending weights: local warehouse sales vs. average of all other warehouses
_LOCAL_WEIGHT = 0.7
_GLOBAL_WEIGHT = 0.3


def _load_warehouses() -> list[dict]:
    with _WAREHOUSES_FILE.open() as f:
        return json.load(f)


def _load_sales() -> list[dict]:
    with _SALES_FILE.open() as f:
        return json.load(f)["sales"]


class WarehouseService:
    def __init__(self) -> None:
        self._warehouses: list[dict] = _load_warehouses()
        self._sales: list[dict] = _load_sales()
        # warehouse_id → {product_id → quantity}; populated lazily on first write/read
        self._stock: dict[int, dict[int, int]] = {}

    @staticmethod
    def _initial_stock(warehouse_id: int, product_id: int) -> int:
        # Deterministic seed so every warehouse starts with varied but stable stock
        return (warehouse_id * 17 + product_id * 13) % 50

    def get_stock(self, warehouse_id: int, product_id: int) -> int:
        return self._stock.get(warehouse_id, {}).get(
            product_id, self._initial_stock(warehouse_id, product_id)
        )

    def set_stock(self, warehouse_id: int, product_id: int, quantity: int) -> None:
        if warehouse_id not in self._stock:
            self._stock[warehouse_id] = {}
        self._stock[warehouse_id][product_id] = quantity

    def all(self) -> list[dict]:
        return self._warehouses

    def by_user(self, user_id: int) -> dict | None:
        return next((w for w in self._warehouses if w["userId"] == user_id), None)

    def by_id(self, warehouse_id: int) -> dict | None:
        return next((w for w in self._warehouses if w["id"] == warehouse_id), None)

    def _inject_warehouse_fields(self, products: list[dict], warehouse_id: int) -> list[dict]:
        velocity = self._sales_velocity(warehouse_id)
        result = []
        for p in products:
            stock = self.get_stock(warehouse_id, p["id"])
            if stock == 0:
                availability = "Out of Stock"
            elif stock <= LOW_STOCK_THRESHOLD:
                availability = "Low Stock"
            else:
                availability = "In Stock"
            result.append({
                **p,
                "stock": stock,
                "availabilityStatus": availability,
                "salesLast90Days": round(velocity.get(p["id"], 0.0) * 90),
            })
        return result

    def _cutoff(self) -> str:
        completed = [s for s in self._sales if s.get("status") == "completed"]
        if not completed:
            return ""
        max_date = max(s["date"] for s in completed)
        return (date.fromisoformat(max_date) - timedelta(days=_SALES_WINDOW_DAYS)).isoformat()

    def _sales_velocity(self, warehouse_id: int) -> dict[int, float]:
        """Avg daily units sold per product for this specific warehouse (last 90 days of data)."""
        cutoff = self._cutoff()
        totals: dict[int, float] = defaultdict(float)
        for sale in self._sales:
            if (
                sale.get("status") == "completed"
                and sale.get("warehouseId") == warehouse_id
                and sale.get("date", "") >= cutoff
            ):
                totals[sale["productId"]] += sale.get("quantity", 0)
        return {pid: qty / _SALES_WINDOW_DAYS for pid, qty in totals.items()}

    def _demand_std(self, warehouse_id: int) -> dict[int, float]:
        """Std of daily demand per product for this warehouse over the sales window.

        Demand is bucketed per day (days with no sales count as 0), so the figure reflects the
        lumpiness of large, infrequent orders — the uncertainty the safety stock is sized against.
        Local only: products this warehouse has never sold get no entry (→ no safety buffer).
        """
        cutoff = self._cutoff()
        daily: dict[int, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        for sale in self._sales:
            if (
                sale.get("status") == "completed"
                and sale.get("warehouseId") == warehouse_id
                and sale.get("date", "") >= cutoff
            ):
                daily[sale["productId"]][sale["date"]] += sale.get("quantity", 0)
        result: dict[int, float] = {}
        for pid, per_day in daily.items():
            mean = sum(per_day.values()) / _SALES_WINDOW_DAYS
            mean_sq = sum(qty * qty for qty in per_day.values()) / _SALES_WINDOW_DAYS
            result[pid] = math.sqrt(max(mean_sq - mean * mean, 0.0))
        return result

    def _other_warehouses_velocity(self, exclude_warehouse_id: int) -> dict[int, float]:
        """Per-warehouse avg daily sales across all warehouses except the given one.

        Dividing by the number of other warehouses normalises the signal so a product that
        sells 20 units split across 19 warehouses counts the same as one that sells 20 units
        in a single warehouse — it reflects the typical per-warehouse demand, not total volume.
        """
        cutoff = self._cutoff()
        totals: dict[int, float] = defaultdict(float)
        for sale in self._sales:
            if (
                sale.get("status") == "completed"
                and sale.get("warehouseId") != exclude_warehouse_id
                and sale.get("date", "") >= cutoff
            ):
                totals[sale["productId"]] += sale.get("quantity", 0)
        num_other = max(len(self._warehouses) - 1, 1)
        return {pid: qty / _SALES_WINDOW_DAYS / num_other for pid, qty in totals.items()}

    def _blended_velocity(self, warehouse_id: int) -> dict[int, float]:
        """Weighted blend: local sales count more than the cross-warehouse average.

        Products with no sales anywhere get velocity 0 — no demand signal, no order suggested.
        """
        local = self._sales_velocity(warehouse_id)
        other = self._other_warehouses_velocity(warehouse_id)
        all_pids = set(local) | set(other)
        return {
            pid: _LOCAL_WEIGHT * local.get(pid, 0.0) + _GLOBAL_WEIGHT * other.get(pid, 0.0)
            for pid in all_pids
        }

    async def list_products(self, warehouse_id: int, query: Any) -> dict[str, Any]:
        products = self._inject_warehouse_fields(await product_service._all_products(), warehouse_id)
        matching = sort_products(filter_products(products, query), query.sortBy, query.order)
        return {
            "items": matching[query.skip : query.skip + query.limit],
            "limit": query.limit,
            "skip": query.skip,
            "total": len(matching),
        }

    async def stock_report(self, warehouse_id: int) -> dict[str, Any]:
        products = self._inject_warehouse_fields(await product_service._all_products(), warehouse_id)
        return build_stock_report(
            products,
            sales_velocity=self._blended_velocity(warehouse_id),
            demand_std=self._demand_std(warehouse_id),
        )


warehouse_service = WarehouseService()
