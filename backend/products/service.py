import logging
from typing import Any

from common.dummyjson import DummyJsonResource, dummyjson
from products.analytics import build_analytics
from products.query import ProductListQuery, filter_products, sort_products

log = logging.getLogger("app.products")

# Only what the analytics and the products table need is requested to DummyJSON
ANALYTICS_FIELDS = "availabilityStatus,brand,category,minimumOrderQuantity,price,rating,reviews,sku,stock,thumbnail,title"


class ProductService(DummyJsonResource):
    path = "/products"
    list_key = "products"
    label = "Product"
    not_found_code = "PRODUCT_NOT_FOUND"

    async def _all_products(self) -> list[dict[str, Any]]:
        # GET /products?limit=0&select=...  (limit=0 returns every product)
        data = await dummyjson.request(
            "GET", self.path, params={"limit": 0, "select": ANALYTICS_FIELDS}
        )
        log.info("Products loaded from DummyJSON (%s)", len(data["products"]))
        return data["products"]

    async def list(self, query: ProductListQuery) -> dict[str, Any]:
        products = await self._all_products()
        matching = sort_products(filter_products(products, query), query.sortBy, query.order)
        return {
            "items": matching[query.skip : query.skip + query.limit],
            "limit": query.limit,
            "skip": query.skip,
            "total": len(matching),
        }

    async def analytics(self) -> dict[str, Any]:
        return build_analytics(await self._all_products())

    async def filters(self) -> dict[str, Any]:
        products = await self._all_products()
        _OTHER = ""
        categories = sorted({p.get("category") or _OTHER for p in products if p.get("category")})
        brands = sorted({p.get("brand") or _OTHER for p in products if p.get("brand")})
        has_no_cat = any(not p.get("category") for p in products)
        has_no_brand = any(not p.get("brand") for p in products)
        return {
            "categories": categories + (["__other__"] if has_no_cat else []),
            "brands": brands + (["__other__"] if has_no_brand else []),
        }


product_service = ProductService()
