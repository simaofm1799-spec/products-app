import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

// Filter control for one table column. It does not keep state: `values` holds the current
// value of every filter (by API parameter) and each change is reported with `change`.
function useColumnFilter(props, emit) {
  const { t, te } = useI18n()

  const ariaLabel = computed(() => t('filters.by', { column: props.label }))

  const selectItems = computed(() =>
    (props.filter.options ?? []).map((value) => ({
      title:
        props.filter.labelGroup && te(`${props.filter.labelGroup}.${value}`)
          ? t(`${props.filter.labelGroup}.${value}`)
          : value,
      value,
    })),
  )

  const valueOf = (param) => props.values[param] ?? ''
  const change = (param, value) => emit('change', param, value ?? '')

  // Range: two API parameters (`<param>Min`, `<param>Max`) shown as one control. A slider handle
  // left at its end means "no limit" on that side, so the parameter is not sent.
  const minParam = computed(() => `${props.filter.param}Min`)
  const maxParam = computed(() => `${props.filter.param}Max`)

  const rangeValue = computed(() => [
    valueOf(minParam.value) === '' ? props.filter.min : Number(valueOf(minParam.value)),
    valueOf(maxParam.value) === '' ? props.filter.max : Number(valueOf(maxParam.value)),
  ])

  const rangeText = computed(() => {
    const low = valueOf(minParam.value)
    const high = valueOf(maxParam.value)
    let text = ''
    if (low !== '' && high !== '') text = `${low} – ${high}`
    else if (low !== '') text = `≥ ${low}`
    else if (high !== '') text = `≤ ${high}`
    return text
  })
  const hasRange = computed(() => rangeText.value !== '')

  function onRangeChange([low, high]) {
    change(minParam.value, low <= props.filter.min ? '' : low)
    change(maxParam.value, high >= props.filter.max ? '' : high)
  }

  function clearRange() {
    change(minParam.value, '')
    change(maxParam.value, '')
  }

  // The icon at the end of the range field clears the range when there is one; the click must
  // not also open the panel
  function onRangeIconClick(event) {
    if (hasRange.value) {
      event.stopPropagation()
      clearRange()
    }
  }

  return {
    ariaLabel,
    change,
    clearRange,
    hasRange,
    maxParam,
    minParam,
    onRangeChange,
    onRangeIconClick,
    rangeText,
    rangeValue,
    selectItems,
    valueOf,
  }
}

export default {
  props: {
    filter: { required: true, type: Object },
    label: { default: '', type: String },
    values: { required: true, type: Object },
  },
  emits: ['change'],
  setup(props, { emit }) {
    return useColumnFilter(props, emit)
  },
}
