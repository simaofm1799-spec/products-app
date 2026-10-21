import { ref, watch } from 'vue'
import { normalizeColumns } from '../utils/columnConfig'

function buildDefaults(definitions) {
  return definitions.map((definition) => ({
    key: definition.key,
    pinned: false,
    visible: definition.visible ?? false,
  }))
}

function readSaved(storageKey) {
  let saved = null
  try {
    saved = JSON.parse(localStorage.getItem(storageKey))
  } catch {
    // no localStorage or invalid content: the defaults are used
  }
  return Array.isArray(saved) ? saved : []
}

// Keeps what was saved for the columns that still exist and adds the new ones at the end.
// Older saves used 'start' for pinned columns (and 'end', which no longer exists).
function mergeWithDefaults(saved, defaults) {
  const known = new Set(defaults.map((column) => column.key))
  const merged = []
  saved.forEach((entry) => {
    if (known.has(entry?.key) && !merged.some((column) => column.key === entry.key)) {
      merged.push({
        key: entry.key,
        pinned: entry.pinned === true || entry.pinned === 'start',
        visible: Boolean(entry.visible),
      })
    }
  })
  defaults.forEach((column) => {
    if (!merged.some((item) => item.key === column.key)) merged.push(column)
  })
  return normalizeColumns(merged)
}

// Column configuration (order, visibility, pinning) saved in localStorage under `storageKey`
export function useColumnConfig(storageKey, definitions) {
  const defaults = buildDefaults(definitions)
  const columns = ref(mergeWithDefaults(readSaved(storageKey), defaults))

  watch(
    columns,
    (value) => {
      try {
        localStorage.setItem(storageKey, JSON.stringify(value))
      } catch {
        // the configuration only lasts for this session
      }
    },
    { deep: true },
  )

  // Only keeps what belongs to the configuration (the dialog may add display fields, e.g. `label`)
  const setColumns = (value) => {
    columns.value = normalizeColumns(
      value.map((column) => ({
        key: column.key,
        pinned: Boolean(column.pinned),
        visible: column.visible,
      })),
    )
  }
  const reset = () => {
    columns.value = normalizeColumns(buildDefaults(definitions))
  }

  return { columns, reset, setColumns }
}
