import { useState } from 'react'
import { useSearchParams } from 'react-router'
import { withQuery } from '../api/client'
import { useApi } from '../hooks/useApi'
import ListingCard from '../components/ListingCard'
import Pagination from '../components/Pagination'
import { Empty, ErrorBox, Loading } from '../components/States'

const LIMIT = 12
const FILTER_KEYS = ['q', 'category_id', 'mode', 'condition', 'min_price', 'max_price', 'sort']
const inputClass = 'w-full rounded border border-gray-300 bg-white px-3 py-2'

export default function CatalogPage() {
  const [params, setParams] = useSearchParams()
  const [resetCount, setResetCount] = useState(0)
  const page = Math.max(1, Number(params.get('page')) || 1)

  // Фильтры лежат в адресной строке: ссылкой можно поделиться, обновление страницы их не сбрасывает
  const filters = Object.fromEntries(FILTER_KEYS.map((key) => [key, params.get(key) || '']))

  const listings = useApi(withQuery('/listings/', { ...filters, limit: LIMIT, offset: (page - 1) * LIMIT }))
  const categories = useApi('/categories/')

  function applyFilters(event) {
    event.preventDefault()
    const next = {}
    for (const [key, value] of new FormData(event.currentTarget).entries()) {
      const text = String(value).trim()
      if (text) next[key] = text
    }
    setParams(next) // ключа page нет, значит возвращаемся на первую страницу
  }

  function goToPage(nextPage) {
    const next = new URLSearchParams(params)
    next.set('page', String(nextPage))
    setParams(next)
    window.scrollTo({ top: 0 })
  }

  function resetFilters() {
    setParams({})
    setResetCount((n) => n + 1)
  }

  // key пересоздаёт форму, когда фильтры изменились извне (кнопка «Назад»),
  // загрузились категории (для select) или нажали «Сбросить»
  const formKey = JSON.stringify(filters) + (categories.data ? '+c' : '') + resetCount
  const { data } = listings

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Каталог</h1>

      <form key={formKey} onSubmit={applyFilters}
            className="grid gap-2 rounded bg-white p-3 shadow sm:grid-cols-2 lg:grid-cols-4">
        <input name="q" defaultValue={filters.q} maxLength={200}
               placeholder="Поиск по названию и описанию" className={`${inputClass} sm:col-span-2`} />
        <select name="category_id" defaultValue={filters.category_id} className={inputClass}>
          <option value="">Все категории</option>
          {categories.data?.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
        <select name="sort" defaultValue={filters.sort} className={inputClass}>
          <option value="">Сортировка по умолчанию</option>
          <option value="date">По дате</option>
          <option value="price">По цене</option>
        </select>
        <select name="mode" defaultValue={filters.mode} className={inputClass}>
          <option value="">Любой режим</option>
          <option value="sale">Продажа</option>
          <option value="exchange">Обмен</option>
          <option value="free">Даром</option>
        </select>
        <select name="condition" defaultValue={filters.condition} className={inputClass}>
          <option value="">Любое состояние</option>
          <option value="new">Новое</option>
          <option value="used">Б/у</option>
        </select>
        <input name="min_price" type="number" min="0" step="any"
               defaultValue={filters.min_price} placeholder="Цена от" className={inputClass} />
        <input name="max_price" type="number" min="0" step="any"
               defaultValue={filters.max_price} placeholder="Цена до" className={inputClass} />
        <div className="flex gap-2 sm:col-span-2 lg:col-span-4">
          <button type="submit" className="rounded bg-blue-600 px-4 py-2 text-white">Показать</button>
          <button type="button" onClick={resetFilters}
                  className="rounded border border-gray-300 px-4 py-2">Сбросить</button>
        </div>
      </form>

      {listings.loading && <Loading />}
      {listings.error && <ErrorBox error={listings.error} onRetry={listings.reload} />}
      {data && (
        data.items.length === 0 ? (
          <Empty>
            {data.total > 0 ? (
              <>На этой странице ничего нет.{' '}
                <button onClick={() => goToPage(1)} className="text-blue-600 underline">К первой странице</button></>
            ) : 'Ничего не найдено. Измените условия поиска.'}
          </Empty>
        ) : (
          <>
            <p className="text-sm text-gray-500">Найдено: {data.total}</p>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {data.items.map((listing) => <ListingCard key={listing.id} listing={listing} />)}
            </div>
            <Pagination total={data.total} limit={LIMIT} page={page} onPage={goToPage} />
          </>
        )
      )}
    </div>
  )
}