import { onMounted, ref } from 'vue'
import { apiRequest } from '../api'
import { useAuth } from './useAuth'

// Loads the products analytics (`GET /api/products/analytics`):
// { brands, categories, lowStockProducts, lowStockThreshold, summary }
export function useProductAnalytics() {
  const { logout } = useAuth()
  const analytics = ref(null)
  const loading = ref(false)
  const error = ref('')

  async function load() {
    loading.value = true
    error.value = ''
    try {
      analytics.value = await apiRequest('/api/products/analytics', { auth: true })
    } catch (requestError) {
      if (requestError.status === 401) logout()
      else error.value = requestError.message
    } finally {
      loading.value = false
    }
  }

  onMounted(load)

  return { analytics, error, load, loading }
}
