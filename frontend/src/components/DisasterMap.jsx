import { MapContainer, TileLayer, CircleMarker, Popup, Polyline, useMap } from 'react-leaflet'
import { useEffect } from 'react'
import 'leaflet/dist/leaflet.css'

const severityColor = {
  critical: '#b91c1c',
  high: '#c2410c',
  medium: '#a16207',
  low: '#15803d',
}

function FitBounds({ points }) {
  const map = useMap()
  useEffect(() => {
    if (!points?.length) return
    const lats = points.map((p) => p[0])
    const lngs = points.map((p) => p[1])
    map.fitBounds(
      [
        [Math.min(...lats), Math.min(...lngs)],
        [Math.max(...lats), Math.max(...lngs)],
      ],
      { padding: [40, 40] },
    )
  }, [points, map])
  return null
}

export default function DisasterMap({
  disasters = [],
  zones = [],
  teams = [],
  depots = [],
  routeLine = null,
  onZoneClick,
  height = '420px',
}) {
  const center = disasters[0]
    ? [disasters[0].latitude, disasters[0].longitude]
    : [13.6288, 79.4192]

  const points = [
    ...disasters.map((d) => [d.latitude, d.longitude]),
    ...zones.map((z) => [z.latitude, z.longitude]),
    ...depots.map((d) => [d.latitude, d.longitude]),
  ]

  return (
    <div className="overflow-hidden rounded-lg border border-command-200" style={{ height }}>
      <MapContainer center={center} zoom={8} style={{ height: '100%', width: '100%' }}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <FitBounds points={points} />
        {disasters.map((d) => (
          <CircleMarker
            key={`d-${d.id}`}
            center={[d.latitude, d.longitude]}
            radius={10}
            pathOptions={{ color: severityColor[d.severity] || '#334e68', fillOpacity: 0.7 }}
          >
            <Popup>
              <strong>{d.title}</strong>
              <br />
              {d.status} · pop {d.affected_population}
            </Popup>
          </CircleMarker>
        ))}
        {zones.map((z) => (
          <CircleMarker
            key={`z-${z.id}`}
            center={[z.latitude, z.longitude]}
            radius={8}
            pathOptions={{ color: severityColor[z.priority || z.severity] || '#486581', fillOpacity: 0.5 }}
            eventHandlers={{ click: () => onZoneClick?.(z) }}
          >
            <Popup>
              <strong>{z.name}</strong>
              <br />
              Priority: {z.priority}
              <br />
              Pop: {z.population}
              <br />
              Food: {Math.round(z.food_demand || 0)} · Water: {Math.round(z.water_demand_litres || 0)}
            </Popup>
          </CircleMarker>
        ))}
        {depots.map((d) => (
          <CircleMarker
            key={`depot-${d.id}`}
            center={[d.latitude, d.longitude]}
            radius={7}
            pathOptions={{ color: '#1d4ed8', fillColor: '#3b82f6', fillOpacity: 0.8 }}
          >
            <Popup>
              <strong>Depot: {d.name}</strong>
              <br />
              {d.location_name}
            </Popup>
          </CircleMarker>
        ))}
        {teams.map((t) => (
          <CircleMarker
            key={`t-${t.id}`}
            center={[t.latitude, t.longitude]}
            radius={6}
            pathOptions={{ color: '#7c3aed', fillOpacity: 0.7 }}
          >
            <Popup>
              <strong>{t.name}</strong>
              <br />
              {t.status}
            </Popup>
          </CircleMarker>
        ))}
        {routeLine?.length >= 2 && (
          <Polyline positions={routeLine} pathOptions={{ color: '#0f766e', weight: 4 }} />
        )}
      </MapContainer>
    </div>
  )
}
