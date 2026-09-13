export function formatNumber(n) {
  if (n == null || Number.isNaN(n)) return '—'
  return new Intl.NumberFormat('en-IN').format(Math.round(n))
}

export function formatPercent(n, digits = 1) {
  if (n == null || Number.isNaN(n)) return '—'
  return `${Number(n).toFixed(digits)}%`
}
