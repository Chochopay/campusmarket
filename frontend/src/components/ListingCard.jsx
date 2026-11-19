import { Link } from 'react-router'
import { CONDITION_LABELS } from '../utils/labels'
import { formatPrice, imageUrl } from '../utils/format'

export default function ListingCard({ listing }) {
  // главное фото это то, у которого наименьшая позиция
  const first = [...listing.listing_images].sort((a, b) => a.position - b.position)[0]
  return (
    <Link to={`/listings/${listing.id}`}
          className="block overflow-hidden rounded bg-white shadow hover:shadow-md">
      {first ? (
        <img src={imageUrl(first.img_file)} alt="" className="h-40 w-full object-cover" />
      ) : (
        <div className="flex h-40 items-center justify-center bg-gray-200 text-gray-500">Нет фото</div>
      )}
      <div className="space-y-1 p-3">
        <p className="break-words font-semibold">{listing.name}</p>
        <p className="text-blue-700">{formatPrice(listing)}</p>
        <p className="text-xs text-gray-500">
          {listing.category_name} · {CONDITION_LABELS[listing.condition]}
        </p>
      </div>
    </Link>
  )
}