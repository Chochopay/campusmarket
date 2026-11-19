import { useState } from 'react'
import { imageUrl } from '../utils/format'

export default function Gallery({ images }) {
  const sorted = [...images].sort((a, b) => a.position - b.position)
  const [index, setIndex] = useState(0)

  if (sorted.length === 0) {
    return <div className="flex h-64 items-center justify-center rounded bg-gray-200 text-gray-500">Нет фото</div>
  }
  const current = sorted[Math.min(index, sorted.length - 1)]

  return (
    <div className="space-y-2">
      <img src={imageUrl(current.img_file)} alt="Фото объявления"
           className="h-64 w-full rounded bg-gray-100 object-contain sm:h-96" />
      {sorted.length > 1 && (
        <div className="flex gap-2 overflow-x-auto">
          {sorted.map((img, i) => (
            <button key={img.id} onClick={() => setIndex(i)}
                    className={`shrink-0 overflow-hidden rounded border-2 ${i === index ? 'border-blue-600' : 'border-transparent'}`}>
              <img src={imageUrl(img.img_file)} alt={`Фото ${i + 1}`} className="h-16 w-16 object-cover" />
            </button>
          ))}
        </div>
      )}
    </div>
  )
}