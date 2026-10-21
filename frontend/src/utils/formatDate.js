// How dates are shown in the app: the API sends 'YYYY-M-D' and the tables show 'YYYY/M/D'
export const formatDate = (value) => (value ? String(value).replaceAll('-', '/') : '')
