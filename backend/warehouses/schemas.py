from typing import Literal

from pydantic import BaseModel

from products.schemas import ProductOut


class WarehouseOut(BaseModel):
    id: int
    name: str
    city: str
    state: str
    lat: float
    lon: float
    userId: int


class WarehouseProductOut(ProductOut):
    salesLast90Days: int = 0


class StockPatch(BaseModel):
    stock: int


class StockReportItem(BaseModel):
    id: int
    title: str | None = None
    sku: str | None = None
    thumbnail: str | None = None
    category: str | None = None
    currentStock: int
    avgDailySales: float
    salesLast90Days: float
    projectedDemand30d: int
    daysUntilStockout: int | None = None
    safetyStock: int = 0
    suggestedOrder: int
    urgency: Literal["critical", "warning", "ok"]


class StockReport(BaseModel):
    items: list[StockReportItem]
    criticalCount: int
    warningCount: int
    totalSuggestedOrder: int
