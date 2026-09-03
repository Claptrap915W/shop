import { useEffect, useState } from 'react'
import { Link, useParams, useSearchParams } from 'react-router-dom'
import { getProduct } from '../api/client'

export default function ProductDetailPage(){
    const { slug } = useParams()
    const [searchParams] = useSearchParams()
    const colorSlug = searchParams.get('color')

    const [product, setProduct] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
    const [selectedSize, setSelectedSize] = useState(null)

    useEffect(() => {
        const contriller = new AbortController()

        setError(null)
        if (!product) setLoading(true)

        getProduct(slug, colorSlug || undefined, contriller.signal)
            .then((data) => {
                setProduct(data)
                setSelectedSize((prev) => 
                    data.current_color_variants?.some((v) => v.size === prev)
                        ? prev
                        : data.current_variant?.size ?? null
                    )
            })
            .catch((err) => { 
                if (err.name === "AbortError") return
                    setError(err.message)
                })
            .finally(() => {
                if (!contriller.signal.aborted) setLoading(false)})

        return () => contriller.abort()
    }, [slug, colorSlug])

    const colors = product
        ? Array.from(
            new Map(
                product.variants.map((v) => [v.color.id, v.color])
            ).values()
        )
        : []
    
    const sizeVariants = product?.current_color_variants ?? []
    const selectedVariant = sizeVariants.find((v) => v.size === selectedSize) ?? null

    if (loading) {
    return (
        <main>
        <p><Link to="/">← 返回列表</Link></p>
        <p>載入中…</p>
        </main>
    )
    }
    if (error) {
    return (
        <main>
        <p><Link to="/">← 返回列表</Link></p>
        <p>錯誤：{error}</p>
        </main>
    )
    }
    if (!product) return null
    return (
    <main>
        <p><Link to="/">← 返回列表</Link></p>
        <h1>{product.name}</h1>
        {product.image && (
        <img src={product.image} alt={product.name} width={280} />
        )}
        <p>HK$ {selectedVariant?.price ?? product.base_price}</p>
        <p>SKU: {selectedVariant?.sku ?? '—'}</p>
        <h2>顏色</h2>
        <ul style={{ display: 'flex', gap: '0.5rem', listStyle: 'none', padding: 0 }}>
        {colors.map((color) => (
            <li key={color.id}>
            <Link
                to={`/products/${product.slug}?color=${color.slug}`}
                style={{
                fontWeight:
                    color.slug === product.current_variant?.color.slug
                    ? 'bold'
                    : 'normal',
                }}
            >
                {color.name}
            </Link>
            </li>
        ))}
        </ul>
        <h2>尺寸</h2>
        <ul style={{ display: 'flex', gap: '0.5rem', listStyle: 'none', padding: 0 }}>
        {sizeVariants.map((variant) => (
            <li key={variant.id}>
            <button
                type="button"
                disabled={!variant.in_stock}
                onClick={() => setSelectedSize(variant.size)}
                style={{
                outline:
                    variant.size === selectedSize ? '2px solid black' : 'none',
                }}
            >
                {variant.size}
                {!variant.in_stock && '（缺貨）'}
            </button>
            </li>
        ))}
        </ul>
        <p>
        variant_id:{' '}
        <strong>{selectedVariant ? selectedVariant.id : '尚未選到'}</strong>
        </p>
    </main>
    )
}