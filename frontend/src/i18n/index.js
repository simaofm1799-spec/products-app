import { createI18n } from 'vue-i18n'
import { en as vuetifyEn, pt as vuetifyPt } from 'vuetify/locale'
import enMessages from './locales/en.json'
import ptMessages from './locales/pt.json'

export const SUPPORTED_LOCALES = ['pt', 'en']
export const LOCALE_KEY = 'locale'
const DEFAULT_LOCALE = 'pt'

// Order: language saved by the user > browser language > default
function detectLocale() {
  let saved = null
  try {
    saved = localStorage.getItem(LOCALE_KEY)
  } catch {
    // no localStorage: fall through to the browser language
  }
  const browser = navigator.language?.slice(0, 2)

  let locale = DEFAULT_LOCALE
  if (SUPPORTED_LOCALES.includes(saved)) locale = saved
  else if (SUPPORTED_LOCALES.includes(browser)) locale = browser
  return locale
}

const i18n = createI18n({
  fallbackLocale: 'en',
  legacy: false,
  locale: detectLocale(),
  // `$vuetify` holds Vuetify's own texts (table footer, aria labels...), so they follow the same language
  messages: {
    en: { ...enMessages, $vuetify: vuetifyEn },
    pt: { ...ptMessages, $vuetify: vuetifyPt },
  },
})

document.documentElement.lang = i18n.global.locale.value

// For the future options screen
export function setLocale(locale) {
  if (SUPPORTED_LOCALES.includes(locale)) {
    i18n.global.locale.value = locale
    document.documentElement.lang = locale
    try {
      localStorage.setItem(LOCALE_KEY, locale)
    } catch {
      // the choice only lasts for this session
    }
  }
}

export default i18n
