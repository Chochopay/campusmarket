import { Route, Routes } from 'react-router'
import Layout from './components/Layout'
import CatalogPage from './pages/CatalogPage'
import ListingPage from './pages/ListingPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import Placeholder from './pages/Placeholder'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<CatalogPage />} />
        <Route path="listings/new" element={<Placeholder title="Новое объявление" />} />
        <Route path="listings/:id" element={<ListingPage />} />
        <Route path="listings/:id/edit" element={<Placeholder title="Редактор" />} />
        <Route path="login" element={<LoginPage />} />
        <Route path="register" element={<RegisterPage />} />
        <Route path="my/listings" element={<Placeholder title="Мои объявления" />} />
        <Route path="my/requests" element={<Placeholder title="Мои заявки" />} />
        <Route path="favorites" element={<Placeholder title="Избранное" />} />
        <Route path="moderation" element={<Placeholder title="Жалобы" />} />
        <Route path="*" element={<Placeholder title="Страница не найдена" />} />
      </Route>
    </Routes>
  )
}