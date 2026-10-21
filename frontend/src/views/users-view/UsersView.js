import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import ServerTable from '../../components/server-table/ServerTable.vue'
import UsersDistribution from '../users-distribution/UsersDistribution.vue'
import UsersTabs from '../users-tabs/UsersTabs.vue'
import { USER_COLUMNS } from './usersColumns'

const TABS = ['table', 'distribution']

function useUsersView() {
  const { t, te } = useI18n()
  const route = useRoute()
  const router = useRouter()

  const ROLE_COLORS = { admin: 'primary', moderator: 'info', user: 'secondary' }

  const label = (group, value) => (value && te(`${group}.${value}`) ? t(`${group}.${value}`) : value)

  // The open tab is kept in the URL (?tab=distribution), so reloading or sharing the link keeps it
  const tab = computed({
    get: () => (TABS.includes(route.query.tab) ? route.query.tab : TABS[0]),
    set: (value) => router.replace({ query: value === TABS[0] ? {} : { tab: value } }),
  })

  return { label, ROLE_COLORS, t, tab }
}

export default {
  components: { ServerTable, UsersDistribution, UsersTabs },
  setup() {
    return { ...useUsersView(), USER_COLUMNS }
  },
}
