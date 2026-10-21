import { useI18n } from 'vue-i18n'

export default {
  props: {
    modelValue: { required: true, type: String },
  },
  emits: ['update:modelValue'],
  setup() {
    const { t } = useI18n()
    return { t }
  },
}
