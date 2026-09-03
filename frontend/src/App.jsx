import { Route, Routes } from 'react-router-dom'
import ProductListPage from './pages/ProductListPage.jsx'
import ProductDetailPage from './pages/ProductDetailPage.jsx'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<ProductListPage />} />
      <Route path="/products/:slug" element={<ProductDetailPage />} />
    </Routes>
  )
}