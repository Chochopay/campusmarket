import { Link, NavLink, Outlet } from 'react-router'
import { useAuth } from '../auth/useAuth'
import { TIMEZONE } from '../utils/format'

const linkClass = ({ isActive }) =>
  `rounded px-2 py-1 ${isActive ? 'bg-blue-600 text-white' : 'text-gray-700 hover:bg-gray-100'}`

export default function Layout() {
  const { user, loading, logout } = useAuth()
  const isModerator = user && (user.role === 'moderator' || user.role === 'admin')

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <header className="border-b bg-white">
        <nav className="mx-auto flex max-w-5xl flex-wrap items-center gap-2 p-3">
          <Link to="/" className="mr-2 text-lg font-bold text-blue-600">CampusMarket</Link>
          <NavLink to="/" end className={linkClass}>Каталог</NavLink>
          {user && (
            <>
              <NavLink to="/my/listings" className={linkClass}>Мои объявления</NavLink>
              <NavLink to="/my/requests" className={linkClass}>Мои заявки</NavLink>
              <NavLink to="/favorites" className={linkClass}>Избранное</NavLink>
            </>
          )}
          {isModerator && <NavLink to="/moderation" className={linkClass}>Жалобы</NavLink>}

          <div className="ml-auto flex items-center gap-2">
            {loading ? null : user ? (
              <>
                <span className="text-sm text-gray-600">{user.username}</span>
                <button onClick={logout} className="rounded border px-2 py-1 hover:bg-gray-100">Выйти</button>
              </>
            ) : (
              <>
                <NavLink to="/login" className={linkClass}>Вход</NavLink>
                <NavLink to="/register" className={linkClass}>Регистрация</NavLink>
              </>
            )}
          </div>
        </nav>
      </header>
      <main className="mx-auto max-w-5xl p-3">
        <footer className="mx-auto max-w-5xl p-3 text-xs text-gray-500">
          Время указано по часовому поясу {TIMEZONE}
        </footer>
        <Outlet />
      </main>
    </div>
  )
}