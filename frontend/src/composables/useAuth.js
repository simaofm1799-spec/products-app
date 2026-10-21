import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { apiRequest, clearToken } from '../api'

// Shared state: the layout and the user menu all read the same user
const user = ref(null)
const loading = ref(false)
const error = ref('')

export function useAuth() {
  const router = useRouter()

  function logout() {
    clearToken()
    user.value = null
    error.value = ''
    router.push('/login')
  }

  async function loadUser() {
    loading.value = true
    error.value = ''
    try {
      user.value = await apiRequest('/api/me', { auth: true })
    } catch (requestError) {
      if (requestError.status === 401) logout()
      else error.value = requestError.message
    } finally {
      loading.value = false
    }
  }

  return { error, loading, loadUser, logout, user }
}
