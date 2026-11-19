export default function FormField({ label, error, ...inputProps }) {
  return (
    <label className="block space-y-1">
      <span className="text-sm text-gray-700">{label}</span>
      <input className="w-full rounded border border-gray-300 px-3 py-2" {...inputProps} />
      {error && <span className="block text-sm text-red-600">{error}</span>}
    </label>
  )
}