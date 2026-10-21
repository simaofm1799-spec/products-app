import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useServerTable } from '../../composables/useServerTable'
import ColumnFilter from '../column-filter/ColumnFilter.vue'
import TableConfigDialog from '../table-config-dialog/TableConfigDialog.vue'

// A complete table for data that the API pages, sorts and filters: column filters under the
// header, a dialog to choose / order / pin the columns (saved in localStorage), loading and
// errors. See `useServerTable` for the column definitions and what the API has to answer.
// Cells are customised with the slots `item.<column key>`, and `actions` adds buttons next to
// the title (they receive `filters` and `onFilterChange`, to set a filter that has no column),
// and `leading` puts content (e.g. tabs) at the start of that row.
function useServerTableComponent(props, slots) {
  const { t } = useI18n()

  const table = useServerTable({
    columns: props.columns,
    endpoint: props.endpoint,
    itemsPerPage: props.itemsPerPage,
    storageKey: props.storageKey,
  })

  const configOpen = ref(false)
  // the `item.<key>` slots the page gives are passed on to the Vuetify table
  const cellSlots = computed(() => Object.keys(slots).filter((name) => name.startsWith('item.')))

  return { ...table, cellSlots, configOpen, t }
}

export default {
  components: { ColumnFilter, TableConfigDialog },
  props: {
    columns: { required: true, type: Array },
    endpoint: { required: true, type: String },
    itemsPerPage: { default: 10, type: Number },
    storageKey: { required: true, type: String },
    title: { default: '', type: String },
  },
  setup(props, { slots }) {
    return useServerTableComponent(props, slots)
  },
}
