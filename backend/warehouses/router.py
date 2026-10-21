from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from common.errors import ForbiddenError, NotFoundError
from common.schemas import ERROR_RESPONSES, NOT_FOUND_RESPONSE, Page
from common.security import get_current_user
from products.query import ProductListQuery
from warehouses.schemas import StockPatch, StockReport, WarehouseOut, WarehouseProductOut
from warehouses.service import warehouse_service

router = APIRouter(
    prefix="/api/warehouses",
    tags=["warehouses"],
    dependencies=[Depends(get_current_user)],
    responses={**ERROR_RESPONSES, **NOT_FOUND_RESPONSE},
)


def _check_access(
    warehouse_id: int = Path(ge=1, description="Warehouse id"),
    user: dict = Depends(get_current_user),
) -> dict:
    """Return the warehouse if the user is admin or is assigned to it; 403/404 otherwise."""
    warehouse = warehouse_service.by_id(warehouse_id)
    if warehouse is None:
        raise NotFoundError(
            f"Warehouse {warehouse_id} not found",
            code="WAREHOUSE_NOT_FOUND",
            params={"id": warehouse_id},
        )
    if user.get("role") != "admin" and warehouse["userId"] != int(user.get("sub", 0)):
        raise ForbiddenError()
    return warehouse


@router.get("", response_model=list[WarehouseOut], summary="List accessible warehouses")
async def list_warehouses(user: dict = Depends(get_current_user)) -> list[dict]:
    if user.get("role") == "admin":
        return warehouse_service.all()
    my = warehouse_service.by_user(int(user.get("sub", 0)))
    return [my] if my else []


@router.get(
    "/{warehouse_id}/products",
    response_model=Page[WarehouseProductOut],
    summary="List warehouse products with warehouse stock and sales",
)
async def list_warehouse_products(
    query: Annotated[ProductListQuery, Query()],
    warehouse: dict = Depends(_check_access),
) -> dict:
    return await warehouse_service.list_products(warehouse["id"], query)


@router.patch(
    "/{warehouse_id}/products/{product_id}",
    summary="Update product stock in a warehouse",
)
async def update_warehouse_stock(
    body: StockPatch,
    product_id: int = Path(ge=1, description="Product id"),
    warehouse: dict = Depends(_check_access),
) -> dict:
    warehouse_service.set_stock(warehouse["id"], product_id, body.stock)
    return {"ok": True, "warehouseId": warehouse["id"], "productId": product_id, "stock": body.stock}


@router.get(
    "/{warehouse_id}/stock-report",
    response_model=StockReport,
    summary="Warehouse stock reorder report",
)
async def warehouse_stock_report(warehouse: dict = Depends(_check_access)) -> dict:
    return await warehouse_service.stock_report(warehouse["id"])
