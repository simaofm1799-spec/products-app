import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useDisplay } from 'vuetify'
import ChatBot from '../../components/chat-bot/ChatBot.vue'
import { useAuth } from '../../composables/useAuth'
import { SUPPORTED_LOCALES, setLocale } from '../../i18n'

function useAppShell() {
  const APP_NAME = 'Stockly'

  const { locale, t } = useI18n()
  const { mdAndUp } = useDisplay()
  const { loadUser, logout, user } = useAuth()

  // Side menu: open by default on desktop, closed on mobile (where it overlays the page).
  // It must start as `null` (not `false`): with `false` Vuetify keeps the drawer closed even
  // when it is `permanent`; with `null` it picks the default for the screen size.
  const drawer = ref(null)
  const isDrawerOpen = computed(() => drawer.value ?? mdAndUp.value)
  const toggleDrawer = () => {
    drawer.value = !isDrawerOpen.value
  }

  // The language switch toggles between the two supported languages (off = first, on = second)
  const [offLocale, onLocale] = SUPPORTED_LOCALES

  const navItems = computed(() => [
    { icon: 'mdi-account-group-outline', title: t('nav.users'), to: '/users' },
    { icon: 'mdi-shopping-outline', title: t('nav.products'), to: '/products' },
    { icon: 'mdi-warehouse', title: t('nav.stock'), to: '/stock' },
  ])

  const fullName = computed(() =>
    user.value ? `${user.value.firstName ?? ''} ${user.value.lastName ?? ''}`.trim() : '',
  )
  const initials = computed(() =>
    [user.value?.firstName, user.value?.lastName]
      .map((name) => name?.[0] ?? '')
      .join('')
      .toUpperCase(),
  )

  onMounted(loadUser)

  return {
    APP_NAME,
    drawer,
    fullName,
    initials,
    locale,
    logout,
    navItems,
    offLocale,
    onLocale,
    setLocale,
    t,
    toggleDrawer,
    user,
  }
}

export default {
  components: { ChatBot },
  setup() {
    return useAppShell()
  },
}
