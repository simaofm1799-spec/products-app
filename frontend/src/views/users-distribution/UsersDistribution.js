import { useI18n } from 'vue-i18n'
import DistributionChart from '../../components/distribution-chart/DistributionChart.vue'
import { useDistribution } from '../../composables/useDistribution'

export default {
  components: { DistributionChart },
  setup() {
    const { t } = useI18n()
    const byState = useDistribution('state')
    const byUniversity = useDistribution('university')
    return { byState, byUniversity, t }
  },
}
