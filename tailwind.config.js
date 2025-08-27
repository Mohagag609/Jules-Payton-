/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './accounting_app/templates/**/*.html',
    './accounting_app/accounting/templates/**/*.html',
    './accounting_app/**/forms.py',
  ],
  safelist: [
    'bg-red-100',
    'text-red-700',
    'border-red-400',
    'bg-green-100',
    'text-green-700',
    'border-green-400',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
