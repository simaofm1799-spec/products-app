// Pure helpers for a table column configuration.
// A configuration is an ordered list of `{ key, pinned, visible }`. Pinned columns always stay
// on the left, so the displayed order is: the pinned columns, then the others; inside each
// group the order of the list is kept.

export function normalizeColumns(columns) {
  return [
    ...columns.filter((column) => column.pinned),
    ...columns.filter((column) => !column.pinned),
  ]
}

export function setVisible(columns, key, visible) {
  return columns.map((column) => (column.key === key ? { ...column, visible } : column))
}

// The column goes to the end of the group it moves to
export function setPinned(columns, key, pinned) {
  const target = columns.find((column) => column.key === key)
  const others = columns.filter((column) => column.key !== key)
  return target ? normalizeColumns([...others, { ...target, pinned }]) : columns
}

// Moves `fromKey` to the position of `toKey`; only inside the same group (pinned or not)
export function reorderColumns(columns, fromKey, toKey) {
  const source = columns.find((column) => column.key === fromKey)
  const target = columns.find((column) => column.key === toKey)
  let result = columns
  if (source && target && fromKey !== toKey && Boolean(source.pinned) === Boolean(target.pinned)) {
    const others = columns.filter((column) => column.key !== fromKey)
    const targetIndex = others.findIndex((column) => column.key === toKey)
    const movesDown = columns.indexOf(source) < columns.indexOf(target)
    const insertAt = movesDown ? targetIndex + 1 : targetIndex
    result = [...others.slice(0, insertAt), source, ...others.slice(insertAt)]
  }
  return result
}
