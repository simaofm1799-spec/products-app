import { useI18n } from 'vue-i18n'

// Card with the products that are out of stock or almost (`items` is [{ id, category, stock,
// thumbnail, title }], the emptiest first). The list scrolls inside the card.
function useLowStockList() {
  const { t } = useI18n()
  // out of stock = error colour, almost out = warning
  const stockColor = (stock) => (stock === 0 ? 'error' : 'warning')
  return { stockColor, t }
}

export default {
  props: {
    error: { default: '', type: String },
    items: { required: true, type: Array },
    loading: { default: false, type: Boolean },
    subtitle: { default: '', type: String },
    title: { required: true, type: String },
  },
  emits: ['retry'],
  setup() {
    return useLowStockList()
  },
}
