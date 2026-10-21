import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { apiRequest } from '../../api'

function useProductDetail() {
  const route = useRoute()
  const router = useRouter()
  const { n, t } = useI18n()

  const error = ref(null)
  const loading = ref(false)
  const product = ref(null)

  const breadcrumbItems = computed(() => [
    { title: t('product.breadcrumb'), to: '/products' },
    { disabled: true, title: product.value?.title ?? '…' },
  ])

  const images = computed(() => {
    let result = []
    if (product.value) {
      const imgs = (product.value.images ?? []).filter(Boolean)
      result = imgs.length ? imgs : product.value.thumbnail ? [product.value.thumbnail] : []
    }
    return result
  })

  const discountedPrice = computed(() => {
    let result = null
    if (product.value?.price) {
      const discount = product.value.discountPercentage
      result = discount ? product.value.price * (1 - discount / 100) : product.value.price
    }
    return result
  })

  const availabilityColor = computed(() => {
    const status = (product.value?.availabilityStatus ?? '').toLowerCase()
    let color = 'default'
    if (status === 'in stock') color = 'success'
    else if (status === 'low stock') color = 'warning'
    else if (status === 'out of stock') color = 'error'
    return color
  })

  const categoryLabel = (slug) =>
    (slug ?? '').replace(/-/g, ' ').replace(/^./, (char) => char.toUpperCase())

  const money = (value) => n(value, { currency: 'USD', maximumFractionDigits: 2, style: 'currency' })

  const reviewDate = (isoString) => (isoString ? new Date(isoString).toLocaleDateString() : '')

  async function load() {
    error.value = null
    loading.value = true
    product.value = null
    try {
      const sku = route.params.sku
      // Substring filter, so confirm an exact SKU match before fetching the full product.
      const { items } = await apiRequest(
        `/api/products?sku=${encodeURIComponent(sku)}&limit=100`,
        { auth: true },
      )
      const match = (items ?? []).find((item) => item.sku?.toLowerCase() === sku.toLowerCase())
      if (!match) throw new Error(t('product.notFound'))
      product.value = await apiRequest(`/api/products/${match.id}`, { auth: true })
    } catch (requestError) {
      error.value = requestError.message
    } finally {
      loading.value = false
    }
  }

  function goBack() {
    if (window.history.state?.back) {
      router.back()
    } else {
      router.push('/products')
    }
  }

  watch(() => route.params.sku, load)
  onMounted(load)

  return {
    availabilityColor,
    breadcrumbItems,
    categoryLabel,
    discountedPrice,
    error,
    goBack,
    images,
    load,
    loading,
    money,
    n,
    product,
    reviewDate,
    t,
  }
}

export default {
  setup() {
    return useProductDetail()
  },
}
