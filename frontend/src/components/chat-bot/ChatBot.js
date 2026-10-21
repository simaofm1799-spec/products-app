import { nextTick, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { apiRequest } from '../../api'

function useChatBot() {
  const { t } = useI18n()
  const open = ref(false)
  const input = ref('')
  const loading = ref(false)
  const messages = ref([])
  const messagesRef = ref(null)

  async function scrollToBottom() {
    await nextTick()
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  }

  async function send() {
    const question = input.value.trim()
    if (!question || loading.value) return

    const history = [...messages.value]
    messages.value.push({ role: 'user', text: question })
    input.value = ''
    loading.value = true
    await scrollToBottom()

    try {
      const data = await apiRequest('/api/chat', { auth: true, body: { question, history }, method: 'POST' })
      messages.value.push({ role: 'assistant', text: data.answer })
    } catch {
      messages.value.push({ role: 'assistant', text: t('chat.error') })
    } finally {
      loading.value = false
      await scrollToBottom()
    }
  }

  function renderMarkdown(text) {
    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/\*\*(.+?)\*\*/gs, '<strong>$1</strong>')
      .replace(/\*([^*\n]+?)\*/g, '<em>$1</em>')
  }

  function clearHistory() {
    messages.value = []
  }

  return { clearHistory, input, loading, messages, messagesRef, open, renderMarkdown, send, t }
}

export default {
  setup() {
    return useChatBot()
  },
}
