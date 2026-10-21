export function makeStockColumns({ categories = [], brands = [] } = {}) {
  return [
    { key: 'image', labelKey: 'products.columns.image', sortable: false, visible: true, width: 72 },
    {
      filter: { param: 'title', type: 'text' },
      key: 'title',
      labelKey: 'products.columns.title',
      visible: true,
      width: 240,
    },
    {
      filter: { labelGroup: 'productFilters', options: brands, param: 'brand', type: 'select' },
      key: 'brand',
      labelKey: 'products.columns.brand',
      visible: true,
      width: 160,
    },
    {
      filter: { labelGroup: 'productFilters', options: categories, param: 'category', type: 'select' },
      key: 'category',
      labelKey: 'products.columns.category',
      visible: true,
      width: 180,
    },
    {
      filter: { max: 10000, min: 0, param: 'stock', type: 'range' },
      key: 'stock',
      labelKey: 'products.columns.stock',
      visible: true,
      width: 150,
    },
    {
      filter: {
        options: ['In Stock', 'Low Stock', 'Out of Stock'],
        param: 'availabilityStatus',
        type: 'select',
      },
      key: 'availabilityStatus',
      labelKey: 'products.columns.availabilityStatus',
      sortable: false,
      visible: true,
      width: 170,
    },
    {
      filter: { max: 25, min: 1, param: 'minimumOrderQuantity', step: 1, type: 'range' },
      key: 'minimumOrderQuantity',
      labelKey: 'products.columns.minOrder',
      visible: true,
      width: 160,
    },
    {
      filter: { max: 2000, min: 0, param: 'price', step: 10, type: 'range' },
      key: 'price',
      labelKey: 'products.columns.price',
      width: 150,
    },
    {
      filter: { param: 'sku', type: 'text' },
      key: 'sku',
      labelKey: 'products.columns.sku',
      width: 140,
    },
    {
      key: 'salesLast90Days',
      labelKey: 'stock.columns.sales90d',
      value: (item) => item.salesLast90Days != null ? String(item.salesLast90Days) : '—',
      visible: true,
      width: 180,
    },
    {
      fixedEnd: true,
      key: 'order',
      labelKey: 'stock.columns.order',
      sortable: false,
      visible: true,
      width: 150,
    },
  ]
}
