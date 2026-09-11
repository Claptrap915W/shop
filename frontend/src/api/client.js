

const BASE_URL = import.meta.env.VITE_API_URL

async function apiFetch(path, signal){
    const response = await fetch(`${BASE_URL}${path}`, { signal })

    if (!response.ok){
        let detail = ''
        try{
            const body = await response.json()
            detail = body.detail ?? JSON.stringify(body)
        } catch {
            detail = response.statusText
        }
        throw new Error(`API ${response.status}: ${detail}`)
    }

    return response.json()
}

export function getProducts({ page, category, q, min, max} = {}){
    const params = new URLSearchParams()
    if (page) params.set('page', String(page))
    if (category) params.set('category', category)
    if (q) params.set('q', q)
    if (min) params.set('min', min)
    if (max) params.set('max', max)

    const query = params.toString()
    return apiFetch(`/products/${query ? `?${query}` : ''}`)
}

export function getProduct(slug, color, signal){
    const params = new URLSearchParams()
    if (color) params.set('color', color)
    const query = params.toString()
    return apiFetch(`/products/${slug}/${query ? `?${query}` : ''}`, signal)
}
    
export function getCategories() {
    return apiFetch('/categories/')
}

function getCsrfToken() {
    const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/)
    return match ? decodeURIComponent(match[1]) : ''
}

async function cartFetch(path, { method = 'GET', body, signal } = {}){
    const headers = {}
    if (body != null) {
        headers['Content-Type'] = 'application/json'
    }
    if (method !== 'GET' && method !== 'HEAD'){
        headers['X-CSRFToken'] = getCsrfToken()
    }

    const response = await fetch(`${BASE_URL}${path}`,{
        method,
        headers,
        credentials: 'include',
        signal,
        body: body != null ? JSON.stringify(body) : undefined,
    })

    if (!response.ok) {
        let detail = ''
        let errBody = null
        try {
            errBody = await response.json()
            detail = errBody.detail ?? JSON.stringify(errBody)
        } catch {
            detail = response.statusText || 'no response body'
        }
    
        const error = new Error(`API ${response.status}: ${detail}`)
        error.status = response.status
        error.body = errBody
        throw error
    }

    if (response.status === 204){
        return null
    }

    return response.json()
}

export function getCart(signal) {
    return cartFetch('/cart/', { signal })
}


export function addToCart(variantId, quantity = 1, signal) {
    return cartFetch('/cart/items/', {
        method: 'POST',
        body: { variant_id: variantId, quantity },
        signal,
    })
}
export function updateCartItem(variantId, quantity, signal) {
    return cartFetch(`/cart/items/${variantId}/`, {
        method: 'PATCH',
        body: { quantity },
        signal,
    })
}
export function removeCartItem(variantId, signal) {
    return cartFetch(`/cart/items/${variantId}/`, {
        method: 'DELETE',
        signal,
    })
}