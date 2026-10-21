import math

from warehouses.analytics import _LEAD_TIME_DAYS, _SERVICE_Z, _TARGET_DAYS, build_stock_report
from warehouses.service import WarehouseService


def _product(**overrides):
    base = {"id": 1, "title": "Widget", "stock": 0, "minimumOrderQuantity": 1}
    return {**base, **overrides}


def _expected_safety(sigma):
    return math.ceil(_SERVICE_Z * sigma * math.sqrt(_LEAD_TIME_DAYS))


def test_safety_stock_adds_buffer_on_top_of_mean_coverage():
    products = [_product(stock=0)]
    velocity = {1: 1.0}  # 1 unit/day → 30 over the target window

    without = build_stock_report(products, sales_velocity=velocity)["items"][0]
    with_var = build_stock_report(products, sales_velocity=velocity, demand_std={1: 2.0})["items"][0]

    assert without["safetyStock"] == 0
    assert without["suggestedOrder"] == _TARGET_DAYS  # 30, mean-only

    safety = _expected_safety(2.0)
    assert safety > 0
    assert with_var["safetyStock"] == safety
    assert with_var["suggestedOrder"] == _TARGET_DAYS + safety


def test_volatile_demand_gets_a_bigger_buffer_than_steady_demand():
    products = [_product(stock=0)]
    velocity = {1: 1.0}

    steady = build_stock_report(products, sales_velocity=velocity, demand_std={1: 0.5})["items"][0]
    volatile = build_stock_report(products, sales_velocity=velocity, demand_std={1: 5.0})["items"][0]

    # Same average demand, but the lumpier product must be ordered in larger quantity.
    assert volatile["suggestedOrder"] > steady["suggestedOrder"]


def test_zero_sigma_keeps_previous_mean_only_behaviour():
    products = [_product(stock=10)]
    velocity = {1: 1.0}

    item = build_stock_report(products, sales_velocity=velocity, demand_std={1: 0.0})["items"][0]
    assert item["safetyStock"] == 0
    assert item["suggestedOrder"] == _TARGET_DAYS - 10  # 30 projected − 10 in stock


def test_demand_std_captures_lumpiness_of_large_orders():
    service = WarehouseService()
    # One product sold in a few big lumps vs. another sold steadily — same total, different σ.
    service._sales = [
        {"status": "completed", "warehouseId": 1, "productId": 100, "date": "2025-10-01", "quantity": 30},
        {"status": "completed", "warehouseId": 1, "productId": 200, "date": "2025-10-01", "quantity": 10},
        {"status": "completed", "warehouseId": 1, "productId": 200, "date": "2025-10-02", "quantity": 10},
        {"status": "completed", "warehouseId": 1, "productId": 200, "date": "2025-10-03", "quantity": 10},
    ]
    stds = service._demand_std(1)
    assert stds[100] > stds[200] > 0


def test_demand_std_ignores_other_warehouses_and_non_completed():
    service = WarehouseService()
    service._sales = [
        {"status": "completed", "warehouseId": 2, "productId": 100, "date": "2025-10-01", "quantity": 30},
        {"status": "cancelled", "warehouseId": 1, "productId": 100, "date": "2025-10-01", "quantity": 30},
    ]
    # No completed local sales for warehouse 1 → product absent (no safety buffer).
    assert service._demand_std(1) == {}
