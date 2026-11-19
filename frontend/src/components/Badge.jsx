export default function Badge({ className = 'bg-gray-100 text-gray-700', children }) {
  return (
    <span className={`inline-block rounded px-2 py-0.5 text-xs font-medium ${className}`}>
      {children}
    </span>
  )
}