import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { apiRequest, setToken } from '../../api'

function useLoginView() {
  const { t } = useI18n()
  const router = useRouter()

  const username = ref('')
  const password = ref('')
  const showPassword = ref(false)
  const error = ref('')
  const loading = ref(false)

  async function submit() {
    error.value = ''
    loading.value = true
    try {
      const data = await apiRequest('/api/login', {
        body: { password: password.value, username: username.value },
        method: 'POST',
      })
      setToken(data.access_token)
      router.push('/products')
    } catch (requestError) {
      error.value = requestError.message
    } finally {
      loading.value = false
    }
  }

  return { error, loading, password, showPassword, submit, t, username }
}

export default {
  setup() {
    return useLoginView()
  },
}
