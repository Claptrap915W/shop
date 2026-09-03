

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