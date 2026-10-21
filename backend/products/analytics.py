from collections import defaultdict
from typing import Any

from common.config import LOW_STOCK_THRESHOLD

# Weight of the global average in a brand's score, counted in reviews (see `rank_brands`)
PRIOR_WEIGHT = 5


def _ratings(product: dict[str, Any]) -> list[int]:
    return [
        review["rating"]
        for review in product.get("reviews") or []
        if review.get("rating") is not None
    ]


def _average(values: list[float]) -> float:
    average = 0.0
    if values:
        average = sum(values) / len(values)
    return average


def rank_brands(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Brands ranked by the total number of reviews of their products, most reviews first
    (ties: higher average rating, then name). Products without a brand are left out.

    Per brand: `productCount`, `reviewCount` and `averageRating` (the mean of all its ratings).
    A brand whose products have no reviews is still listed, with `reviewCount` 0 and no
    `averageRating`/`score` (nothing is made up).

    `score` is a complementary indicator, NOT the ranking criterion: a plain average would let a
    brand with a single 5-star review beat one with fifty 4.8s, so the score is a weighted average
    in which the global average counts as `PRIOR_WEIGHT` extra reviews:

        score = (reviewCount * averageRating + PRIOR_WEIGHT * globalAverage) / (reviewCount + PRIOR_WEIGHT)

    Brands with few reviews are pulled towards the global average; with many, their own wins.
    """
    ratings_by_brand: dict[str, list[int]] = defaultdict(list)
    products_by_brand: dict[str, int] = defaultdict(int)
    for product in products:
        if product.get("brand"):
            products_by_brand[product["brand"]] += 1
            ratings_by_brand[product["brand"]].extend(_ratings(product))

    all_ratings = [rating for ratings in ratings_by_brand.values() for rating in ratings]
    global_average = _average(all_ratings)

    brands = []
    for brand, ratings in ratings_by_brand.items():
        count = len(ratings)
        average = None
        score = None
        if ratings:
            average = round(_average(ratings), 2)
            score = round(
                (count * _average(ratings) + PRIOR_WEIGHT * global_average) / (count + PRIOR_WEIGHT), 2
            )
        brands.append(
            {
                "averageRating": average,
                "brand": brand,
                "productCount": products_by_brand[brand],
                "reviewCount": count,
                "score": score,
            }
        )
    brands.sort(
        key=lambda entry: (-entry["reviewCount"], -(entry["averageRating"] or 0), entry["brand"].lower())
    )
    return brands


def summarize_categories(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Per category: products (available or not), price range and stock. Biggest category first."""
    products_by_category: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for product in products:
        if product.get("category"):
            products_by_category[product["category"]].append(product)

    categories = []
    for category, items in products_by_category.items():
        prices = [item["price"] for item in items if item.get("price") is not None]
        stocks = [item.get("stock") or 0 for item in items]
        min_price = min(prices, default=0)
        max_price = max(prices, default=0)
        available = sum(1 for stock in stocks if stock > 0)
        categories.append(
            {
                "available": available,
                "category": category,
                "lowStock": sum(1 for stock in stocks if 0 < stock <= LOW_STOCK_THRESHOLD),
                "maxPrice": max_price,
                "minPrice": min_price,
                "outOfStock": len(items) - available,
                "products": len(items),
                "spread": round(max_price - min_price, 2),
                "stock": sum(stocks),
            }
        )
    categories.sort(key=lambda entry: (-entry["products"], entry["category"].lower()))
    return categories


def low_stock_products(products: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Products that are out of stock or almost, the emptiest first."""
    at_risk = [
        {
            "id": product["id"],
            "category": product.get("category"),
            "stock": product.get("stock") or 0,
            "thumbnail": product.get("thumbnail"),
            "title": product.get("title"),
        }
        for product in products
        if (product.get("stock") or 0) <= LOW_STOCK_THRESHOLD
    ]
    at_risk.sort(key=lambda entry: (entry["stock"], (entry["title"] or "").lower()))
    return at_risk


def build_analytics(products: list[dict[str, Any]]) -> dict[str, Any]:
    categories = summarize_categories(products)
    at_risk = low_stock_products(products)
    all_ratings = [rating for product in products for rating in _ratings(product)]
    return {
        "brands": rank_brands(products),
        "categories": categories,
        "lowStockProducts": at_risk,
        "lowStockThreshold": LOW_STOCK_THRESHOLD,
        "summary": {
            "averageRating": round(_average(all_ratings), 2),
            "categories": len(categories),
            "lowStock": sum(1 for entry in at_risk if entry["stock"] > 0),
            "outOfStock": sum(1 for entry in at_risk if entry["stock"] == 0),
            "products": len(products),
            "totalStock": sum(product.get("stock") or 0 for product in products),
            "withoutBrand": sum(1 for product in products if not product.get("brand")),
        },
    }
