export default function Placeholder({ title, description }) {
  return (
    <div className="space-y-2">
      <h2 className="font-display text-2xl font-bold text-command-900">{title}</h2>
      <p className="text-sm text-command-600">{description}</p>
      <div className="card mt-4 border-dashed">
        <p className="text-sm text-command-500">
          This module will be connected to live APIs in upcoming phases.
        </p>
      </div>
    </div>
  )
}
