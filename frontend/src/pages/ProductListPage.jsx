import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getProducts } from '../api/client'

export default function ProductListPage() {
const [products, setProducts] = useState([])
const [loading, setLoading] = useState(true)
const [error, setError] = useState(null)

useEffect(() => {
    getProducts()
    .then((data) => setProducts(data.results ?? []))
    .catch((err) => setError(err.message))
    .finally(() => setLoading(false))
}, [])

if (loading) {
    return (
    <main>
        <h1>商品列表</h1>
        <p>加载中…</p>
    </main>
    )
}

if (error) {
    return (
    <main>
        <h1>商品列表</h1>
        <p>错误：{error}</p>
    </main>
    )
}

return (
    <main>
    <h1>商品列表</h1>
    <ul style={{ listStyle: 'none', padding: 0, display: 'grid', gap: '1rem' }}>
        {products.map((product) => (
        <li key={product.id}>
            <Link to={`/products/${product.slug}`}>
            {product.image && (
                <img
                src={product.image}
                alt={product.name}
                width={200}
                height={200}
                style={{ objectFit: 'cover' }}
                />
            )}
            <h2>{product.name}</h2>
            <p>HK$ {product.base_price}</p>
            {product.category && (
                <p>{product.category.name}</p>
            )}
            </Link>
        </li>
        ))}
    </ul>
    </main>
)
}