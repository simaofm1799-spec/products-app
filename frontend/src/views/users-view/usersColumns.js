import { formatDate } from '../../utils/formatDate'

// Every column the users table can show. The format of a column (and of its filter) is described
// in `composables/useServerTable.js` and in `docs/TABLES.md`.
// The API filters, sorts and pages, and can sort by any column (nested fields included).
export const USER_COLUMNS = [
  { key: 'image', labelKey: 'users.columns.image', sortable: false, visible: true, width: 72 },
  {
    filter: { param: 'name', type: 'text' },
    key: 'firstName',
    labelKey: 'users.columns.name',
    value: (user) => `${user.firstName ?? ''} ${user.lastName ?? ''}`.trim(),
    visible: true,
    width: 200,
  },
  {
    filter: { max: 70, min: 18, param: 'age', type: 'range' },
    key: 'age',
    labelKey: 'users.columns.age',
    visible: true,
    width: 130,
  },
  {
    filter: { labelGroup: 'gender', options: ['female', 'male', 'other'], param: 'gender', type: 'select' },
    key: 'gender',
    labelKey: 'users.columns.gender',
    visible: true,
    width: 130,
  },
  {
    filter: { labelGroup: 'roles', options: ['admin', 'moderator', 'user'], param: 'role', type: 'select' },
    key: 'role',
    labelKey: 'users.columns.role',
    visible: true,
    width: 170,
  },
  {
    filter: { param: 'state', type: 'text' },
    key: 'address.state',
    labelKey: 'users.columns.state',
    visible: true,
    width: 160,
  },
  {
    filter: { param: 'username', type: 'text' },
    key: 'username',
    labelKey: 'users.columns.username',
    width: 160,
  },
  { filter: { param: 'email', type: 'text' }, key: 'email', labelKey: 'users.columns.email', width: 260 },
  { filter: { param: 'phone', type: 'text' }, key: 'phone', labelKey: 'users.columns.phone', width: 180 },
  {
    filter: { param: 'birthDate', type: 'text' },
    key: 'birthDate',
    labelKey: 'users.columns.birthDate',
    value: (user) => formatDate(user.birthDate),
    width: 190,
  },
  {
    filter: {
      options: ['A+', 'A-', 'AB+', 'AB-', 'B+', 'B-', 'O+', 'O-'],
      param: 'bloodGroup',
      type: 'select',
    },
    key: 'bloodGroup',
    labelKey: 'users.columns.bloodGroup',
    width: 150,
  },
  {
    filter: { max: 205, min: 145, param: 'height', type: 'range' },
    key: 'height',
    labelKey: 'users.columns.height',
    width: 150,
  },
  {
    filter: { max: 105, min: 45, param: 'weight', type: 'range' },
    key: 'weight',
    labelKey: 'users.columns.weight',
    width: 150,
  },
  {
    filter: {
      options: ['Amber', 'Blue', 'Brown', 'Gray', 'Green', 'Hazel', 'Red', 'Violet'],
      param: 'eyeColor',
      type: 'select',
    },
    key: 'eyeColor',
    labelKey: 'users.columns.eyeColor',
    width: 150,
  },
  {
    filter: { param: 'city', type: 'text' },
    key: 'address.city',
    labelKey: 'users.columns.city',
    width: 160,
  },
  {
    filter: { param: 'country', type: 'text' },
    key: 'address.country',
    labelKey: 'users.columns.country',
    width: 160,
  },
  {
    filter: { param: 'company', type: 'text' },
    key: 'company.name',
    labelKey: 'users.columns.company',
    width: 220,
  },
]
