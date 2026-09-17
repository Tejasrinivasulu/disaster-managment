/** Build ops deep-links with disaster/zone context. */
export function opsLink(path, { disasterId, zoneId } = {}) {
  const q = new URLSearchParams()
  if (disasterId != null && disasterId !== '') q.set('disaster_id', String(disasterId))
  if (zoneId != null && zoneId !== '') q.set('zone_id', String(zoneId))
  const s = q.toString()
  return s ? `${path}?${s}` : path
}

export function readOpsQuery(searchParams) {
  return {
    disasterId: searchParams.get('disaster_id') || '',
    zoneId: searchParams.get('zone_id') || '',
  }
}
