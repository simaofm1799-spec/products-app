import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useProductAnalytics } from '../../composables/useProductAnalytics'
import AnalyticsBarChart from '../../components/analytics-bar-chart/AnalyticsBarChart.vue'
import KpiCard from '../../components/kpi-card/KpiCard.vue'
import ServerTable from '../../components/server-table/ServerTable.vue'
import { productPath } from '../../utils/productUrl'
import { PRODUCT_COLUMNS } from './productsColumns'

function useProductsView() {
  const { n, t } = useI18n()
  const { analytics, error, load, loading } = useProductAnalytics()

  // DummyJSON prices are in dollars
  const money = (value) =>
    n(value, { currency: 'USD', maximumFractionDigits: 0, style: 'currency' })
  // "womens-watches" -> "Womens watches"
  const categoryName = (slug) =>
    slug.replace(/-/g, ' ').replace(/^./, (char) => char.toUpperCase())
  const availabilityColor = (status) => {
    const s = (status ?? '').toLowerCase()
    if (s === 'in stock') return 'success'
    if (s === 'low stock') return 'warning'
    if (s === 'out of stock') return 'error'
    return 'default'
  }

  // the threshold comes from the API (LOW_STOCK_THRESHOLD, 10 by default); the plain label shows until it arrives
  const lowStockLabel = computed(() =>
    analytics.value
      ? t('products.table.lowStockLimit', { threshold: analytics.value.lowStockThreshold })
      : t('products.table.lowStock'),
  )

  const summary = computed(() => analytics.value?.summary)
  const brands = computed(() => analytics.value?.brands ?? [])
  const categories = computed(() => analytics.value?.categories ?? [])
  // the categories with the biggest gap between the dearest and the cheapest product first
  const bySpread = computed(() =>
    [...categories.value].sort((first, second) => second.spread - first.spread),
  )
  const byStock = computed(() =>
    [...categories.value].sort((first, second) => second.stock - first.stock),
  )

  const brandsChart = computed(() => ({
    datasets: [
      {
        color: 'primary',
        data: brands.value.map((brand) => brand.reviewCount),
        label: t('products.brands.reviews'),
      },
    ],
    labels: brands.value.map((brand) => brand.brand),
  }))

  const availabilityChart = computed(() => ({
    datasets: [
      {
        color: 'success',
        data: categories.value.map((entry) => entry.available),
        label: t('products.availability.available'),
      },
      {
        color: 'error',
        data: categories.value.map((entry) => entry.outOfStock),
        label: t('products.availability.outOfStock'),
      },
    ],
    labels: categories.value.map((entry) => categoryName(entry.category)),
  }))

  const priceChart = computed(() => ({
    datasets: [
      {
        color: 'secondary',
        data: bySpread.value.map((entry) => [entry.minPrice, entry.maxPrice]),
        label: t('products.prices.range'),
      },
    ],
    labels: bySpread.value.map((entry) => categoryName(entry.category)),
  }))

  const stockChart = computed(() => ({
    datasets: [
      {
        color: 'info',
        data: byStock.value.map((entry) => entry.stock),
        label: t('products.stock.units'),
      },
    ],
    labels: byStock.value.map((entry) => categoryName(entry.category)),
  }))

  // a brand without reviews has no average rating and no score: nothing is shown instead of a made-up value
  const brandTooltip = (context) => {
    const brand = brands.value[context.dataIndex]
    const lines = [
      t('products.brands.tooltipReviews', { count: brand.reviewCount }),
      t('products.brands.tooltipProducts', { count: brand.productCount }),
    ]
    if (brand.averageRating === null) {
      lines.push(t('products.brands.tooltipNoRating'))
    } else {
      lines.push(
        t('products.brands.tooltipRating', {
          rating: n(brand.averageRating, { maximumFractionDigits: 2 }),
        }),
        t('products.brands.tooltipScore', {
          score: n(brand.score, { maximumFractionDigits: 2 }),
        }),
      )
    }
    return lines
  }
  const availabilityTooltip = (context) => `${context.dataset.label}: ${context.parsed.x}`
  const priceTooltip = (context) => {
    const entry = bySpread.value[context.dataIndex]
    return t('products.prices.tooltip', {
      max: money(entry.maxPrice),
      min: money(entry.minPrice),
      spread: money(entry.spread),
    })
  }
  const stockTooltip = (context) => t('products.stock.tooltip', { count: n(context.parsed.x) })

  const kpis = computed(() => [
    {
      color: 'primary',
      icon: 'mdi-package-variant-closed',
      label: t('products.kpis.products'),
      value: n(summary.value?.products ?? 0),
    },
    {
      color: 'secondary',
      icon: 'mdi-shape-outline',
      label: t('products.kpis.categories'),
      value: n(summary.value?.categories ?? 0),
    },
    {
      color: 'info',
      icon: 'mdi-warehouse',
      label: t('products.kpis.stock'),
      value: n(summary.value?.totalStock ?? 0),
    },
    {
      color: 'warning',
      hint: t('products.kpis.ratingHint'),
      icon: 'mdi-star-outline',
      label: t('products.kpis.rating'),
      value: n(summary.value?.averageRating ?? 0, { maximumFractionDigits: 2 }),
    },
    {
      color: 'error',
      hint: t('products.kpis.atRiskHint', {
        low: summary.value?.lowStock ?? 0,
        out: summary.value?.outOfStock ?? 0,
      }),
      icon: 'mdi-alert-outline',
      label: t('products.kpis.atRisk'),
      value: n((summary.value?.lowStock ?? 0) + (summary.value?.outOfStock ?? 0)),
    },
  ])

  return {
    analytics,
    availabilityChart,
    availabilityColor,
    availabilityTooltip,
    brands,
    brandsChart,
    brandTooltip,
    bySpread,
    byStock,
    categories,
    categoryName,
    error,
    kpis,
    load,
    loading,
    lowStockLabel,
    money,
    n,
    priceChart,
    priceTooltip,
    productPath,
    stockChart,
    stockTooltip,
    summary,
    t,
  }
}

export default {
  name: 'ProductsView',
  components: { AnalyticsBarChart, KpiCard, ServerTable },
  setup() {
    return { ...useProductsView(), PRODUCT_COLUMNS }
  },
}
