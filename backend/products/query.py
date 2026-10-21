from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from common.config import LOW_STOCK_THRESHOLD

# Fields the list can be sorted by (the same keys the frontend table uses for its columns)
SortField = Literal[
    "availabilityStatus", "brand", "category", "discountPercentage", "id",
    "minimumOrderQuantity", "price", "rating", "salesLast90Days", "sku", "stock", "title", "weight",
]

# query parameter -> product field it filters (contains the text, case-insensitive)
_TEXT_FILTERS = {
    "availabilityStatus": "availabilityStatus",
    "brand": "brand",
    "category": "category",
    "sku": "sku",
    "title": "title",
}
# fields the general search `q` looks into
_SEARCH_FIELDS = ("title", "brand", "category", "sku")


class ProductListQuery(BaseModel):
    """Query of `GET /api/products`: pagination, sorting, a general search and one optional filter
    per table column. When several filters are given, a product has to match all of them."""

    model_config = ConfigDict(extra="forbid")

    limit: int = Field(30, ge=1, le=100, description="Items per page")
    skip: int = Field(0, ge=0, description="Items to skip")
    order: Literal["asc", "desc"] = Field("asc", description="Sort direction")
    sortBy: SortField | None = Field(None, description="Field to sort by")

    q: str | None = Field(
        None, min_length=1, max_length=100, description="Search in title, brand, category and sku"
    )

    # contains the text (case-insensitive)
    availabilityStatus: str | None = Field(None, min_length=1, max_length=100)
    brand: str | None = Field(None, min_length=1, max_length=100)
    category: str | None = Field(None, min_length=1, max_length=100)
    sku: str | None = Field(None, min_length=1, max_length=100)
    title: str | None = Field(None, min_length=1, max_length=200)

    lowStock: bool | None = Field(
        None,
        description=f"true: only products with stock <= LOW_STOCK_THRESHOLD ({LOW_STOCK_THRESHOLD} "
        "by default), out of stock included",
    )

    discountPercentageMax: float | None = None
    discountPercentageMin: float | None = None
    minimumOrderQuantityMax: int | None = None
    minimumOrderQuantityMin: int | None = None
    priceMax: float | None = None
    priceMin: float | None = None
    ratingMax: float | None = None
    ratingMin: float | None = None
    stockMax: int | None = None
    stockMin: int | None = None
    weightMax: float | None = None
    weightMin: float | None = None


def _text(product: dict[str, Any], field: str) -> str:
    return str(product.get(field) or "").lower()


def _matches(product: dict[str, Any], query: ProductListQuery) -> bool:
    checks: list[bool] = []
    if query.q is not None:
        wanted = query.q.lower()
        checks.append(any(wanted in _text(product, field) for field in _SEARCH_FIELDS))
    for param, field in _TEXT_FILTERS.items():
        wanted = getattr(query, param)
        if wanted is not None:
            if wanted == "__other__":
                checks.append(not product.get(field))
            else:
                checks.append(wanted.lower() in _text(product, field))
    if query.lowStock:
        checks.append((product.get("stock") or 0) <= LOW_STOCK_THRESHOLD)
    for param in ("discountPercentage", "minimumOrderQuantity", "price", "rating", "stock", "weight"):
        value = product.get(param)
        minimum = getattr(query, f"{param}Min")
        maximum = getattr(query, f"{param}Max")
        if minimum is not None:
            checks.append(value is not None and value >= minimum)
        if maximum is not None:
            checks.append(value is not None and value <= maximum)
    return all(checks)


def filter_products(products: list[dict[str, Any]], query: ProductListQuery) -> list[dict[str, Any]]:
    return [product for product in products if _matches(product, query)]


def sort_products(
    products: list[dict[str, Any]], sort_by: str | None, order: str
) -> list[dict[str, Any]]:
    """Products without a value for the field always go last, whatever the direction."""
    result = products
    if sort_by is not None:

        def sort_key(product: dict[str, Any]) -> tuple:
            value = product.get(sort_by)
            normalized = value.lower() if isinstance(value, str) else value
            return (normalized, _text(product, "title"))

        with_value = [product for product in products if product.get(sort_by) is not None]
        without_value = [product for product in products if product.get(sort_by) is None]
        result = sorted(with_value, key=sort_key, reverse=order == "desc") + without_value
    return result
