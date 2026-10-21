import { BarElement, CategoryScale, Chart, LinearScale, Tooltip } from 'chart.js'
import ChartDataLabels from 'chartjs-plugin-datalabels'
import { computed, ref } from 'vue'
import { Bar } from 'vue-chartjs'
import { useI18n } from 'vue-i18n'
import { useTheme } from 'vuetify'

// Horizontal bar chart (Chart.js): one bar per value, longest first, with the count at the end
// of each bar and the share of the total in the tooltip. Only the biggest ones show at first;
// "show all" opens the rest (the chart scrolls). `items` is [{ count, label }] already sorted;
// `color` is a Vuetify theme colour.
Chart.register(BarElement, CategoryScale, LinearScale, Tooltip)

const ROW_HEIGHT = 28

function useDistributionChart(props) {
  const { n, t } = useI18n()
  const theme = useTheme()

  const showAll = ref(false)

  const canExpand = computed(() => props.items.length > props.visibleCount)
  const shownItems = computed(() =>
    showAll.value ? props.items : props.items.slice(0, props.visibleCount),
  )
  const share = (count) =>
    n(props.total ? count / props.total : 0, { maximumFractionDigits: 1, style: 'percent' })
  const chartHeight = computed(() => `${shownItems.value.length * ROW_HEIGHT + 16}px`)

  const chartData = computed(() => ({
    datasets: [
      {
        backgroundColor: theme.current.value.colors[props.color],
        barThickness: 14,
        borderRadius: 7,
        data: shownItems.value.map((item) => item.count),
      },
    ],
    labels: shownItems.value.map((item) => item.label),
  }))

  const chartOptions = computed(() => ({
    indexAxis: 'y',
    layout: { padding: { right: 28 } },
    maintainAspectRatio: false,
    plugins: {
      datalabels: {
        align: 'end',
        anchor: 'end',
        color: theme.current.value.colors['on-surface'],
        font: { weight: 600 },
      },
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: (context) =>
            t('stats.tooltip', {
              count: context.parsed.x,
              share: share(context.parsed.x),
            }),
        },
      },
    },
    responsive: true,
    scales: { x: { display: false }, y: { grid: { display: false }, border: { display: false } } },
  }))

  return { canExpand, chartData, chartHeight, chartOptions, showAll, t }
}

export default {
  components: { Bar },
  props: {
    color: { default: 'primary', type: String },
    error: { default: '', type: String },
    icon: { default: '', type: String },
    items: { required: true, type: Array },
    loading: { default: false, type: Boolean },
    title: { required: true, type: String },
    total: { default: 0, type: Number },
    visibleCount: { default: 10, type: Number },
  },
  emits: ['retry'],
  setup(props) {
    return { ...useDistributionChart(props), ChartDataLabels }
  },
}
