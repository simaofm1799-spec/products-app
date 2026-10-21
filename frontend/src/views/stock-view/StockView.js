import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { apiRequest } from '../../api'
import { useAuth } from '../../composables/useAuth'
import ServerTable from '../../components/server-table/ServerTable.vue'
import { makeStockColumns } from './stockColumns'

function useStockView() {
  const { n, t } = useI18n()
  const { logout, user } = useAuth()

  const isAdmin = computed(() => user.value?.role === 'admin')

  // ── Product filters (categories & brands) ─────────────────────────────────
  const productFilters = ref({ categories: [], brands: [] })
  const filtersReady = ref(false)

  async function loadProductFilters() {
    try {
      const data = await apiRequest('/api/products/filters', { auth: true })
      productFilters.value = { categories: data.categories, brands: data.brands }
    } catch {
      // non-critical — table still renders, filters degrade to text input
    } finally {
      filtersReady.value = true
    }
  }

  const stockColumns = computed(() => makeStockColumns(productFilters.value))

  // ── Warehouses ─────────────────────────────────────────────────────────────
  const warehouses = ref([])
  const warehousesLoading = ref(false)
  const warehousesError = ref('')
  const selectedWarehouseId = ref(null)

  const selectedWarehouse = computed(() =>
    warehouses.value.find((w) => w.id === selectedWarehouseId.value) ?? null,
  )

  const warehouseItems = computed(() =>
    warehouses.value.map((w) => ({
      title: `${w.name} — ${w.city}, ${w.state}`,
      value: w.id,
    })),
  )

  async function loadWarehouses() {
    warehousesLoading.value = true
    warehousesError.value = ''
    try {
      warehouses.value = await apiRequest('/api/warehouses', { auth: true })
      if (warehouses.value.length > 0) selectedWarehouseId.value = warehouses.value[0].id
    } catch (err) {
      if (err.status === 401) logout()
      else warehousesError.value = err.message
    } finally {
      warehousesLoading.value = false
    }
  }

  // ── Table ──────────────────────────────────────────────────────────────────
  const tableKey = ref(0)

  const tableEndpoint = computed(() =>
    selectedWarehouseId.value ? `/api/warehouses/${selectedWarehouseId.value}/products` : '',
  )

  function onWarehouseChange() {
    pendingOrders.value = new Map()
    tableKey.value++
  }

  // ── Pending orders ─────────────────────────────────────────────────────────
  // Map<productId, { qty, title, thumbnail, currentStock }>
  const pendingOrders = ref(new Map())

  const orderCount = computed(
    () => Array.from(pendingOrders.value.values()).filter((o) => o.qty > 0).length,
  )

  const orderItems = computed(() =>
    Array.from(pendingOrders.value.entries())
      .filter(([, o]) => o.qty > 0)
      .map(([id, o]) => ({
        id,
        title: o.title,
        thumbnail: o.thumbnail,
        currentStock: o.currentStock,
        qty: o.qty,
        newStock: o.currentStock + o.qty,
      })),
  )

  function getOrderQty(productId) {
    return pendingOrders.value.get(productId)?.qty ?? 0
  }

  function removeOrder(productId) {
    const newMap = new Map(pendingOrders.value)
    newMap.delete(productId)
    pendingOrders.value = newMap
    if (newMap.size === 0) confirmDialog.value = false
  }

  function setOrderQty(item, rawQty) {
    const qty = Math.max(0, Math.floor(Number(rawQty) || 0))
    const newMap = new Map(pendingOrders.value)
    if (qty > 0) {
      newMap.set(item.id, {
        qty,
        title: item.title,
        thumbnail: item.thumbnail,
        currentStock: item.stock ?? 0,
      })
    } else {
      newMap.delete(item.id)
    }
    pendingOrders.value = newMap
  }

  // ── Auto-suggest ───────────────────────────────────────────────────────────
  const autoSuggestLoading = ref(false)
  const autoSuggestError = ref('')
  const noOrderNeeded = ref(false)

  async function autoSuggest() {
    if (!selectedWarehouseId.value) return
    autoSuggestLoading.value = true
    autoSuggestError.value = ''
    noOrderNeeded.value = false
    try {
      const report = await apiRequest(
        `/api/warehouses/${selectedWarehouseId.value}/stock-report`,
        { auth: true },
      )
      const newMap = new Map(pendingOrders.value)
      let suggestedCount = 0
      for (const item of report.items) {
        if (item.suggestedOrder > 0) {
          suggestedCount++
          newMap.set(item.id, {
            qty: item.suggestedOrder,
            title: item.title,
            thumbnail: item.thumbnail,
            currentStock: item.currentStock,
          })
        }
      }
      pendingOrders.value = newMap
      // Nothing to reorder — tell the user instead of leaving the click with no feedback.
      if (suggestedCount === 0) noOrderNeeded.value = true
    } catch (err) {
      if (err.status === 401) logout()
      else autoSuggestError.value = err.message
    } finally {
      autoSuggestLoading.value = false
    }
  }

  // ── Confirm order ──────────────────────────────────────────────────────────
  const confirmDialog = ref(false)
  const confirmLoading = ref(false)
  const confirmError = ref('')

  async function confirmOrder() {
    if (!selectedWarehouseId.value || orderCount.value === 0) return
    confirmLoading.value = true
    confirmError.value = ''
    try {
      await Promise.all(
        orderItems.value.map((item) =>
          apiRequest(
            `/api/warehouses/${selectedWarehouseId.value}/products/${item.id}`,
            { auth: true, body: { stock: item.newStock }, method: 'PATCH' },
          ),
        ),
      )
      pendingOrders.value = new Map()
      confirmDialog.value = false
      snackbar.value = true
      tableKey.value++
    } catch (err) {
      confirmError.value = err.message
    } finally {
      confirmLoading.value = false
    }
  }

  // ── Individual stock edit ──────────────────────────────────────────────────
  const editDialog = ref(false)
  const editItem = ref(null)
  const editStock = ref(0)
  const editLoading = ref(false)
  const editError = ref('')
  const snackbar = ref(false)

  function openEditStock(item) {
    editItem.value = item
    editStock.value = item.stock ?? 0
    editError.value = ''
    editDialog.value = true
  }

  async function saveStock() {
    if (!editItem.value || !selectedWarehouseId.value) return
    editLoading.value = true
    editError.value = ''
    try {
      await apiRequest(
        `/api/warehouses/${selectedWarehouseId.value}/products/${editItem.value.id}`,
        { auth: true, body: { stock: editStock.value }, method: 'PATCH' },
      )
      editDialog.value = false
      snackbar.value = true
      tableKey.value++
    } catch (err) {
      editError.value = err.message
    } finally {
      editLoading.value = false
    }
  }

  // ── Helpers ────────────────────────────────────────────────────────────────
  const productPath = (product) => `/product/${encodeURIComponent(product.sku)}`

  const stockChipColor = (status) => {
    const s = (status ?? '').toLowerCase()
    if (s === 'in stock') return 'success'
    if (s === 'low stock') return 'warning'
    if (s === 'out of stock') return 'error'
    return 'default'
  }

  const money = (value) =>
    n(value, { currency: 'USD', maximumFractionDigits: 2, style: 'currency' })

  onMounted(() => { loadWarehouses(); loadProductFilters() })

  return {
    autoSuggest,
    autoSuggestError,
    autoSuggestLoading,
    confirmDialog,
    confirmError,
    confirmLoading,
    confirmOrder,
    editDialog,
    editError,
    editItem,
    editLoading,
    editStock,
    getOrderQty,
    isAdmin,
    removeOrder,
    money,
    n,
    noOrderNeeded,
    onWarehouseChange,
    openEditStock,
    orderCount,
    productPath,
    orderItems,
    saveStock,
    selectedWarehouse,
    selectedWarehouseId,
    setOrderQty,
    filtersReady,
    snackbar,
    stockColumns,
    stockChipColor,
    t,
    tableEndpoint,
    tableKey,
    warehouseItems,
    warehouses,
    warehousesError,
    warehousesLoading,
  }
}

export default {
  components: { ServerTable },
  setup() {
    return useStockView()
  },
}
