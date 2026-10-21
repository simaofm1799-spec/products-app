from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response, status

from common.schemas import ERROR_RESPONSES, NOT_FOUND_RESPONSE, Page
from common.security import get_current_user, require_creator, require_deleter, require_editor
from products.query import ProductListQuery
from products.schemas import ProductAnalytics, ProductCreate, ProductOut, ProductUpdate
from products.service import product_service

router = APIRouter(
    prefix="/api/products",
    tags=["products"],
    dependencies=[Depends(get_current_user)],
    responses=ERROR_RESPONSES,
)

ProductId = Path(ge=1, description="Product id")


@router.get("", response_model=Page[ProductOut], summary="List products")
async def list_products(query: Annotated[ProductListQuery, Query()]):
    return await product_service.list(query)


# declared before "/{product_id}" so that "analytics" is not read as a product id
@router.get("/filters", summary="Available filter values for category and brand")
async def product_filters():
    return await product_service.filters()


@router.get("/analytics", response_model=ProductAnalytics, summary="Products analytics")
async def products_analytics():
    return await product_service.analytics()


@router.get("/{product_id}", response_model=ProductOut, responses=NOT_FOUND_RESPONSE, summary="Get product")
async def get_product(product_id: int = ProductId):
    return await product_service.get(product_id)


@router.post(
    "",
    response_model=ProductOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_creator)],
    summary="Create product",
)
async def create_product(body: ProductCreate):
    return await product_service.create(body.model_dump(exclude_unset=True))


@router.put(
    "/{product_id}",
    response_model=ProductOut,
    dependencies=[Depends(require_editor)],
    responses=NOT_FOUND_RESPONSE,
    summary="Update product",
)
@router.patch(
    "/{product_id}",
    response_model=ProductOut,
    dependencies=[Depends(require_editor)],
    responses=NOT_FOUND_RESPONSE,
    include_in_schema=False,
)
async def update_product(body: ProductUpdate, product_id: int = ProductId):
    return await product_service.update(product_id, body.model_dump(exclude_unset=True))


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_deleter)],
    responses=NOT_FOUND_RESPONSE,
    summary="Delete product",
)
async def delete_product(product_id: int = ProductId):
    await product_service.delete(product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
