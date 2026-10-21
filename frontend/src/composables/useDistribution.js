import { onMounted, ref } from 'vue'
import { apiRequest } from '../api'
import { useAuth } from './useAuth'

// Loads how many users there are per value of a field (`GET /api/users/distribution?by=<by>`):
// { by, total, items: [{ count, label }] }, most users first.
export function useDistribution(by) {
  const { logout } = useAuth()
  const items = ref([])
  const total = ref(0)
  const loading = ref(false)
  const error = ref('')

  async function load() {
    loading.value = true
    error.value = ''
    try {
      const data = await apiRequest(`/api/users/distribution?by=${by}`, { auth: true })
      items.value = data.items
      total.value = data.total
    } catch (requestError) {
      if (requestError.status === 401) logout()
      else error.value = requestError.message
    } finally {
      loading.value = false
    }
  }

  onMounted(load)

  return { error, items, load, loading, total }
}
