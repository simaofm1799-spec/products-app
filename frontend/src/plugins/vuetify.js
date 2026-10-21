import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { createVueI18nAdapter } from 'vuetify/locale/adapters/vue-i18n'
import { useI18n } from 'vue-i18n'
import i18n from '../i18n'

export default createVuetify({
  components,
  defaults: {
    VBtn: { rounded: 'lg' },
    VTextField: { color: 'info', density: 'comfortable', variant: 'outlined' },
  },
  directives,
  locale: { adapter: createVueI18nAdapter({ i18n, useI18n }) },
  theme: {
    // Light mode is the one in use; dark mode stays defined for the future options screen.
    defaultTheme: 'brandLight',
    themes: {
      brand: {
        colors: {
          accent: '#1B7CC4',
          background: '#120B1F',
          error: '#FF5C7A',
          info: '#00B4E6',
          primary: '#E6188D',
          secondary: '#7B3FA0',
          surface: '#1C1230',
        },
        dark: true,
      },
      brandLight: {
        colors: {
          accent: '#1B7CC4',
          background: '#F6F2FB',
          error: '#D6264A',
          info: '#0090BD',
          primary: '#E6188D',
          secondary: '#7B3FA0',
          surface: '#FFFFFF',
        },
        dark: false,
      },
    },
  },
})
