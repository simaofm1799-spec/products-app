import pytest
from pydantic import ValidationError

from products import analytics, query as product_query
from products.analytics import build_analytics, rank_brands
from products.query import ProductListQuery, filter_products, sort_products


def product(brand, ratings, stock=20, **extra):
    return {
        "brand": brand,
        "category": "beauty",
        "reviews": [{"rating": rating} for rating in ratings],
        "stock": stock,
        "title": f"{brand}-{stock}",
        **extra,
    }


def test_brands_are_ranked_by_total_reviews_not_by_score():
    products = [
        product("Big", [3, 3, 3]),
        product("Big", [3, 3, 3]),  # 6 reviews, average 3.0
        product("Tiny", [5]),  # 1 review, average 5.0 (would win on a plain average)
        product("Mid", [4, 4, 4]),
    ]
    ranking = rank_brands(products)
    assert [entry["brand"] for entry in ranking] == ["Big", "Mid", "Tiny"]
    assert (ranking[0]["averageRating"], ranking[0]["productCount"], ranking[0]["reviewCount"]) == (3.0, 2, 6)


def test_ties_break_on_average_rating_then_name():
    products = [product("B", [4, 4]), product("A", [4, 4]), product("C", [5, 5])]
    assert [entry["brand"] for entry in rank_brands(products)] == ["C", "A", "B"]


def test_no_brand_is_left_out_and_no_reviews_is_not_invented():
    products = [product(None, [5, 5]), product("", [5]), product("Silent", [])]
    ranking = rank_brands(products)
    assert ranking == [
        {"averageRating": None, "brand": "Silent", "productCount": 1, "reviewCount": 0, "score": None}
    ]
    assert build_analytics(products)["summary"]["withoutBrand"] == 2


def test_score_is_the_documented_weighted_average():
    products = [product("A", [5, 5]), product("B", [1, 1, 1])]
    by_brand = {entry["brand"]: entry for entry in rank_brands(products)}
    global_average = (5 + 5 + 1 + 1 + 1) / 5
    expected = (2 * 5 + analytics.PRIOR_WEIGHT * global_average) / (2 + analytics.PRIOR_WEIGHT)
    assert by_brand["A"]["score"] == round(expected, 2)


PRODUCTS = [
    {"id": 1, "brand": "Acme", "category": "beauty", "price": 5, "stock": 0, "title": "Lipstick"},
    {"id": 2, "brand": "Acme", "category": "laptops", "price": 900, "stock": 10, "title": "Laptop"},
    {"id": 3, "brand": None, "category": "laptops", "price": 700, "stock": 11, "title": "Tablet"},
    {"id": 4, "brand": "Zed", "category": "beauty", "price": 8, "stock": 50, "title": "Mascara"},
]


def ids(query_args):
    return [item["id"] for item in filter_products(PRODUCTS, ProductListQuery(**query_args))]


def test_low_stock_filter_uses_the_threshold_inclusive(monkeypatch):
    assert ids({"lowStock": True}) == [1, 2]  # default 10: 0 and 10, not 11
    monkeypatch.setattr(product_query, "LOW_STOCK_THRESHOLD", 11)
    assert ids({"lowStock": True}) == [1, 2, 3]
    assert ids({"lowStock": False}) == [1, 2, 3, 4]  # false is "no filter"


def test_search_and_column_filters():
    assert ids({"q": "ACME"}) == [1, 2]
    assert ids({"q": "laptops"}) == [2, 3]
    assert ids({"title": "ip"}) == [1]
    assert ids({"category": "beauty", "stockMin": 1}) == [4]
    assert ids({"priceMax": 8, "priceMin": 6}) == [4]


def test_sorting_puts_missing_values_last_in_both_directions():
    ascending = [item["id"] for item in sort_products(PRODUCTS, "brand", "asc")]
    descending = [item["id"] for item in sort_products(PRODUCTS, "brand", "desc")]
    assert ascending == [2, 1, 4, 3]  # ties on brand: by title
    assert descending == [4, 1, 2, 3]
    assert [item["id"] for item in sort_products(PRODUCTS, "stock", "desc")] == [4, 3, 2, 1]


def test_unknown_parameters_and_sort_fields_are_rejected():
    with pytest.raises(ValidationError):
        ProductListQuery(colour="red")
    with pytest.raises(ValidationError):
        ProductListQuery(sortBy="description")
