import { useEffect, useState } from 'react'
import { getHealth } from '../services/api'

export default function DemoBanner() {
  const [demoMode, setDemoMode] = useState(true)

  useEffect(() => {
    getHealth()
      .then((data) => setDemoMode(data.demo_mode !== false))
      .catch(() => setDemoMode(true))
  }, [])

  if (!demoMode) return null

  return (
    <span className="badge bg-amber-100 text-amber-800 ring-1 ring-amber-300">
      Demo Data
    </span>
  )
}
