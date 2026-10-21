// Every column the products table can show. The format of a column (and of its filter) is described
// in `composables/useServerTable.js`.
// The API filters, sorts and pages (`GET /api/products`).
export const PRODUCT_COLUMNS = [
  {
    key: 'image',
    labelKey: 'products.columns.image',
    sortable: false,
    visible: true,
    width: 72,
  },
  {
    filter: { param: 'title', type: 'text' },
    key: 'title',
    labelKey: 'products.columns.title',
    visible: true,
    width: 240,
  },
  {
    filter: { param: 'brand', type: 'text' },
    key: 'brand',
    labelKey: 'products.columns.brand',
    visible: true,
    width: 160,
  },
  {
    filter: { param: 'category', type: 'text' },
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
    filter: { max: 100000, min: 0, param: 'price', step: 10, type: 'range' },
    key: 'price',
    labelKey: 'products.columns.price',
    visible: true,
    width: 150,
  },
  {
    filter: { max: 5, min: 0, param: 'rating', step: 0.5, type: 'range' },
    key: 'rating',
    labelKey: 'products.columns.rating',
    visible: true,
    width: 120,
  },
  {
    filter: { param: 'sku', type: 'text' },
    key: 'sku',
    labelKey: 'products.columns.sku',
    width: 140,
  },
  {
    filter: {
      max: 30,
      min: 0,
      param: 'discountPercentage',
      step: 1,
      type: 'range',
    },
    key: 'discountPercentage',
    labelKey: 'products.columns.discount',
    value: (p) =>
      p.discountPercentage != null
        ? `${Math.round(p.discountPercentage)}%`
        : '—',
    width: 140,
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
    width: 170,
  },
  {
    filter: {
      max: 25,
      min: 1,
      param: 'minimumOrderQuantity',
      step: 1,
      type: 'range',
    },
    key: 'minimumOrderQuantity',
    labelKey: 'products.columns.minOrder',
    width: 160,
  },
  {
    filter: { max: 50, min: 0, param: 'weight', step: 1, type: 'range' },
    key: 'weight',
    labelKey: 'products.columns.weight',
    value: (p) => (p.weight != null ? `${p.weight} kg` : '—'),
    width: 120,
  },
]
