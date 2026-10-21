export default {
  props: {
    color: { default: 'primary', type: String },
    hint: { default: '', type: String },
    icon: { required: true, type: String },
    label: { required: true, type: String },
    value: { required: true, type: [Number, String] },
  },
}
