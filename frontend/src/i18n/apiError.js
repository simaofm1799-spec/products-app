import i18n from './index'

const { t, te } = i18n.global

// The API sends a stable `code` (plus `params`); the text shown comes from the i18n files.

function fieldErrorMessage(err) {
  const params = err.params ?? {}
  // normalise the constraint names sent by the API (ge/gt -> min, le/lt -> max)
  const values = { ...params, max: params.le ?? params.lt, min: params.ge ?? params.gt }
  const fieldKey = `fields.${err.field}`
  const field = te(fieldKey) ? t(fieldKey) : err.field
  const key = `validation.${err.code}`
  return `${field}: ${te(key) ? t(key, values) : t('validation.INVALID_VALUE')}`
}

/** Translated message for an API error body ({ code, params?, errors? }). */
export function apiErrorMessage(data) {
  const key = `errors.${data?.code}`
  let message = t('errors.UNKNOWN')
  if (data?.code === 'VALIDATION_ERROR' && data.errors?.length) {
    message = data.errors.map(fieldErrorMessage).join('\n')
  } else if (data?.code && te(key)) {
    message = t(key, data.params ?? {})
  }
  return message
}

export const networkErrorMessage = () => t('errors.NETWORK_ERROR')
