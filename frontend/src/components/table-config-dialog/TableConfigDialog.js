import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { reorderColumns, setPinned, setVisible } from '../../utils/columnConfig'

// `columns` is the configuration plus a `label` for display: [{ key, label, pinned, visible }]
const GROUPS = [
  { id: 'pinned', pinned: true, titleKey: 'table.groupPinned' },
  { id: 'main', pinned: false, titleKey: 'table.groupMain' },
]

function useTableConfigDialog(props, emit) {
  const { t } = useI18n()

  // The pinned group only shows up when it has columns; the main one always does
  const groups = computed(() =>
    GROUPS.map((group) => ({
      ...group,
      items: props.columns.filter((column) => Boolean(column.pinned) === group.pinned),
    })).filter((group) => group.id === 'main' || group.items.length > 0),
  )

  const visibleCount = computed(() => props.columns.filter((column) => column.visible).length)

  const draggedKey = ref(null)
  const overKey = ref(null)

  const update = (columns) => emit('update:columns', columns)
  const isLastVisible = (column) => column.visible && visibleCount.value === 1

  function onDragStart(event, column) {
    draggedKey.value = column.key
    event.dataTransfer.effectAllowed = 'move'
    event.dataTransfer.setData('text/plain', column.key) // Firefox only starts the drag with data
  }

  function onDragOver(event, column) {
    const dragged = props.columns.find((item) => item.key === draggedKey.value)
    // only accepts a drop on a column of the same group
    if (dragged && Boolean(dragged.pinned) === Boolean(column.pinned)) {
      event.preventDefault()
      overKey.value = column.key
    }
  }

  function onDragEnd() {
    draggedKey.value = null
    overKey.value = null
  }

  function onDrop(column) {
    update(reorderColumns(props.columns, draggedKey.value, column.key))
    onDragEnd()
  }

  return { draggedKey, emit, groups, isLastVisible, onDragEnd, onDragOver, onDragStart, onDrop, overKey, setPinned, setVisible, t, update }
}

export default {
  props: {
    columns: { required: true, type: Array },
    modelValue: { default: false, type: Boolean },
  },
  emits: ['reset', 'update:columns', 'update:modelValue'],
  setup(props, { emit }) {
    return useTableConfigDialog(props, emit)
  },
}
