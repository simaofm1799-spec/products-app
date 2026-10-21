import { BarElement, CategoryScale, Chart, Legend, LinearScale, Tooltip } from 'chart.js'
import ChartDataLabels from 'chartjs-plugin-datalabels'
import { computed, ref } from 'vue'
import { Bar } from 'vue-chartjs'
import { useI18n } from 'vue-i18n'
import { useTheme } from 'vuetify'

// Card with a horizontal bar chart (Chart.js) for the analytics screens. The parent gives one
// label per row and one or more datasets (`{ color, data, label }`, `color` is a Vuetify theme
// colour), already sorted. Only the first rows show at first; "show all" opens the rest (the
// chart scrolls). A `data` entry can be a number or a `[from, to]` pair (floating bar).
// `formatLabel(value, context)` writes the text at the end of a bar (return '' to hide it);
// `formatTooltip(context)` writes each line of the tooltip.
Chart.register(BarElement, CategoryScale, Legend, LinearScale, Tooltip)

const ROW_HEIGHT = 28

function useAnalyticsBarChart(props) {
  const { t } = useI18n()
  const theme = useTheme()

  const showAll = ref(false)

  const canExpand = computed(() => props.labels.length > props.visibleCount)
  const rowCount = computed(() =>
    showAll.value ? props.labels.length : Math.min(props.labels.length, props.visibleCount),
  )
  const hasLegend = computed(() => props.datasets.length > 1)
  const chartHeight = computed(
    () => `${rowCount.value * ROW_HEIGHT + (hasLegend.value ? 48 : 16)}px`,
  )

  const chartData = computed(() => ({
    datasets: props.datasets.map((dataset) => ({
      backgroundColor: theme.current.value.colors[dataset.color],
      barThickness: 14,
      borderRadius: props.stacked ? 0 : 7,
      borderSkipped: false,
      data: dataset.data.slice(0, rowCount.value),
      label: dataset.label,
    })),
    labels: props.labels.slice(0, rowCount.value),
  }))

  const chartOptions = computed(() => {
    const onSurface = theme.current.value.colors['on-surface']
    const tooltip = props.formatTooltip ? { callbacks: { label: props.formatTooltip } } : {}
    return {
      indexAxis: 'y',
      layout: { padding: { right: props.stacked ? 0 : 56 } },
      maintainAspectRatio: false,
      plugins: {
        datalabels: {
          align: props.stacked ? 'center' : 'end',
          anchor: props.stacked ? 'center' : 'end',
          color: props.stacked ? '#fff' : onSurface,
          font: { size: 11, weight: 600 },
          formatter: (value, context) => props.formatLabel(value, context) || null,
        },
        legend: {
          display: hasLegend.value,
          labels: { boxHeight: 8, boxWidth: 8, color: onSurface, usePointStyle: true },
          position: 'top',
        },
        tooltip,
      },
      responsive: true,
      scales: {
        x: {
          border: { display: false },
          display: props.showAxis,
          grid: { color: 'rgba(128, 128, 128, 0.15)' },
          stacked: props.stacked,
          ticks: { color: onSurface },
        },
        y: { border: { display: false }, grid: { display: false }, stacked: props.stacked },
      },
    }
  })

  return { canExpand, chartData, chartHeight, chartOptions, showAll, t }
}

export default {
  components: { Bar },
  props: {
    color: { default: 'primary', type: String },
    datasets: { required: true, type: Array },
    error: { default: '', type: String },
    formatLabel: { default: (value) => String(value), type: Function },
    formatTooltip: { default: null, type: Function },
    icon: { default: '', type: String },
    labels: { required: true, type: Array },
    loading: { default: false, type: Boolean },
    showAxis: { default: false, type: Boolean },
    stacked: { default: false, type: Boolean },
    subtitle: { default: '', type: String },
    title: { required: true, type: String },
    visibleCount: { default: 10, type: Number },
  },
  emits: ['retry'],
  setup(props) {
    return { ...useAnalyticsBarChart(props), ChartDataLabels }
  },
}
