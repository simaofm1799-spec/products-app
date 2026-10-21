import { computed, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { apiRequest } from '../api'
import { useAuth } from './useAuth'
import { useColumnConfig } from './useColumnConfig'

const FILTER_DELAY = 400

// The API parameters a filter sends: a range sends `<param>Min` and `<param>Max`
export const filterParams = (filter) =>
  filter.type === 'range' ? [`${filter.param}Min`, `${filter.param}Max`] : [filter.param]

/**
 * State and logic of a table whose data is paged, sorted and filtered by the API.
 * It is what `ServerTable.vue` uses; use it directly only for a table with a different layout.
 *
 * `columns` are the column definitions:
 *   key       data key; also what is sent as `sortBy` ('address.state' for nested fields)
 *   labelKey  i18n key of the column title
 *   width     pixels; required, Vuetify uses it to place the pinned columns
 *   visible   shown by default (the user changes it in the table configuration dialog)
 *   sortable  `false` to disable sorting (default: sortable)
 *   value     optional function (item) => displayed value
 *   filter    optional, the filter in the row under the header (`param` is the API query parameter):
 *               { type: 'text', param }                      contains the text
 *               { type: 'select', param, options, labelGroup? }  one of `options` (labels: i18n `labelGroup.<option>`)
 *               { type: 'number', param }                    exact number
 *               { type: 'range', param, min, max, step? }    sends `<param>Min` / `<param>Max`
 *
 * The API (`endpoint`) receives `limit`, `skip`, `sortBy`, `order` and the filter parameters,
 * and answers `{ items, total }`.
 */
export function useServerTable({ columns, endpoint, itemsPerPage: pageSize = 10, storageKey }) {
  const { t } = useI18n()
  const { logout } = useAuth()

  const definitions = Object.fromEntries(columns.map((column) => [column.key, column]))

  const items = ref([])
  const total = ref(0)
  const loading = ref(false)
  const error = ref('')

  const page = ref(1)
  const itemsPerPage = ref(pageSize)
  const sortBy = ref([])

  // Column configuration: which columns are shown, in what order and which ones are pinned
  const {
    columns: columnConfig,
    reset: resetColumns,
    setColumns,
  } = useColumnConfig(storageKey, columns)

  const headers = computed(() =>
    columnConfig.value
      .filter((column) => column.visible)
      .map((column) => {
        const definition = definitions[column.key]
        return {
          // Vuetify needs a numeric `width` on pinned columns to place them
          ...(definition.fixedEnd
            ? { fixed: 'end', width: definition.width }
            : column.pinned && { fixed: 'start', width: definition.width }),
          ...(definition.value && { value: definition.value }),
          key: definition.key,
          minWidth: definition.width,
          sortable: definition.sortable ?? true,
          title: t(definition.labelKey),
        }
      }),
  )

  // the configuration dialog needs the label of each column
  const dialogColumns = computed(() =>
    columnConfig.value.map((column) => ({
      ...column,
      label: t(definitions[column.key].labelKey),
    })),
  )

  // Column filters. `filters` follows what the user types; `appliedFilters` is what is sent to the
  // API, a moment after the user stops typing. Keys are API query parameters ('name', 'ageMin'...).
  const filters = reactive({})
  const appliedFilters = ref({})
  const hasFilters = computed(() => Object.values(filters).some((value) => value !== ''))

  const onFilterChange = (param, value) => {
    filters[param] = value
  }
  const clearFilters = () => {
    Object.keys(filters).forEach((param) => {
      filters[param] = ''
    })
  }

  let filterTimer
  watch(filters, () => {
    clearTimeout(filterTimer)
    filterTimer = setTimeout(() => {
      appliedFilters.value = Object.fromEntries(
        Object.entries(filters).filter(([, value]) => value !== '' && value !== null),
      )
      page.value = 1
    }, FILTER_DELAY)
  })

  // Hiding a column drops its filter (it could not be seen or cleared) and, if the table
  // was sorted by that column, the sorting.
  watch(headers, (value) => {
    const visibleKeys = new Set(value.map((header) => header.key))
    const sortedKey = sortBy.value[0]?.key
    if (sortedKey && !visibleKeys.has(sortedKey)) sortBy.value = []
    columns
      .filter((column) => column.filter && !visibleKeys.has(column.key))
      .flatMap((column) => filterParams(column.filter))
      .forEach((param) => {
        if (filters[param] !== undefined && filters[param] !== '') filters[param] = ''
      })
  })

  let requestId = 0
  async function load() {
    const current = ++requestId
    loading.value = true
    error.value = ''

    const params = new URLSearchParams({
      limit: itemsPerPage.value,
      skip: (page.value - 1) * itemsPerPage.value,
    })
    Object.entries(appliedFilters.value).forEach(([param, value]) => params.set(param, value))
    if (sortBy.value[0]) {
      params.set('order', sortBy.value[0].order)
      params.set('sortBy', sortBy.value[0].key)
    }

    try {
      const data = await apiRequest(`${endpoint}?${params}`, { auth: true })
      // if a newer request is already in flight, this response is ignored
      if (current === requestId) {
        items.value = data.items
        total.value = data.total
      }
    } catch (requestError) {
      if (current === requestId) {
        if (requestError.status === 401) {
          logout()
        } else {
          items.value = []
          total.value = 0
          error.value = requestError.message
        }
      }
    } finally {
      if (current === requestId) loading.value = false
    }
  }

  watch([page, itemsPerPage, sortBy, appliedFilters], load, { immediate: true })

  return {
    clearFilters,
    definitions,
    dialogColumns,
    error,
    filters,
    hasFilters,
    headers,
    items,
    itemsPerPage,
    loading,
    onFilterChange,
    page,
    resetColumns,
    setColumns,
    sortBy,
    total,
  }
}
