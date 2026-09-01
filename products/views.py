from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Category, Product
from users.models import UserProfile
from django.db.models import Q

def product_list(request):
    """商品列表頁：支援分類、價格篩選 + 分頁"""
    selected_category = request.GET.get('category', '')#取出 category 參數，如果沒有則預設為空字串。
    max_p = request.GET.get('max', '')
    query = request.GET.get('q', '').strip()
    categories = Category.objects.filter(is_active=True, parent=None)#取出頂層分類（沒有 parent 的主分類），且必須是上架狀態。

    # 計算主分類總數 (本身 + 子分類)
    for cat in categories: #來自 models.py 中 related_name='children' 的反向關聯。
        category_ids = [cat.id] + list(cat.children.values_list('id', flat=True)) #只取出 id 欄位，變成一個 list。
        cat.total_product_count = Product.active.filter(category_id__in=category_ids).count()
        
        # 核心修復：將子分別轉為 list 並計算數量，再掛回 cat 物件
        sub_cats = list(cat.children.all()) # 強制執行查詢並轉成 Python list，避免後續模板中重複查詢資料庫。
        for sub in sub_cats:
            sub.sub_product_count = Product.active.filter(category_id=sub.id).count()#為每個子分類計算商品數量，並新增 sub_product_count 屬性,
        cat.sub_categories = sub_cats#把處理好的子分類清單掛到 cat.sub_categories

    # === 3. 商品查詢 ===
    products = Product.active.all()
    
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(variants__sku__icontains=query) |
            Q(category__name__icontains=query) |
            Q(variants__color__name__icontains=query) |
            Q(variants__size__icontains=query) 
        )

    # 分類篩選 (這裡也要包含子分類)
    if selected_category:
        category = get_object_or_404(Category, slug=selected_category)
        category_ids = [category.id] + list(category.children.values_list('id', flat=True))
        products = products.filter(category_id__in=category_ids)

    # 價格篩選
    if max_p:
        try:
            max_price = float(max_p)
            products = products.filter(base_price__lte=max_price)#小於等於（less than or equal）指定的最高價格。
        except ValueError:
            pass
    
    # === 4. 計算總數 (在分頁前) ===
    total_products = products.count()#在套用分頁前先計算總商品數，供模板顯示「共 X 件商品」。
    
    # === 5. 分頁 ===
    paginator = Paginator(products, 6) #每頁顯示 10 筆商品
    page_number = request.GET.get('page', 1)#取得當前頁面的資料
    page_obj = paginator.get_page(page_number)
    
    context = {
        'categories': categories,
        'products': page_obj, 
        'total_products': total_products,
        'selected_category': selected_category,
        'max_p': max_p,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'query': query,
    }
    return render(request, 'products/product_list.html', context)

# ------------------------------------------------------------------
# 2. 商品詳細頁
# ------------------------------------------------------------------
def product(request, slug):

    # Constants for size choices
    SIZES_LIST = ('XS', 'S', 'M', 'L', 'XL', '2XL', '3XL')

    # 如果商品已下架（is_active=False），即使知道網址也會看到 404，防止已下架商品被直接訪問
    # 由於我們在 ActiveProductManager 已經 prefetch_related('images', 'variants')
    # 這裡的 product.images.all() 和 product.variants.all() 不會再發出 SQL 查詢！
    product = get_object_or_404(Product.active, slug=slug)
    all_variants = product.variants.select_related('color').all() 
    all_images = product.images.all()

    # Dedupe the list of available colors
    available_colors = list({variant.color.id: variant.color for variant in all_variants}.values())
    
    # Get the color parameter from URL
    current_color_slug = request.GET.get('color')
    
    # If there is invalid or missing color parameter in URL, default to the first color
    # avoid KeyError if available_colors is empty
    # else, the color parameter is valid, get the first matching color object from available_colors
    # then break the Generator Expression
    is_valid_slug = any(color.slug == current_color_slug for color in available_colors)
    if not is_valid_slug and available_colors:
        current_color = available_colors[0]
        current_color_slug = current_color.slug
    else:
        current_color = next((color for color in available_colors if color.slug == current_color_slug), None)
        current_color_slug = current_color.slug if current_color else None

    is_favorited = False
    profile = None
    if request.user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        is_favorited = profile.favorites.filter(pk=product.pk).exists()
    # Related Products: Same Category + All Sub Categories
    # Get current category + its child categories
    current_cat = product.category
    cat_ids = [current_cat.id] + list(current_cat.children.values_list('id', flat=True))
    # Query related products
    related_products = Product.active.filter(category_id__in=cat_ids).exclude(pk=product.pk)[:6]

    # Handle favorite status
    fav_ids = set()
    if profile:
        fav_ids = set(profile.favorites.values_list('id', flat=True))

    for item in related_products:
        item.is_favorited = item.id in fav_ids
    
    context = {
        'product': product,
        'current_color': current_color,
        'available_colors': available_colors,
        'available_sizes': list({variant.size for variant in all_variants if variant.color.slug == current_color_slug}) if current_color_slug else [],
        'all_sizes': sorted(list({variant.size for variant in all_variants}),
                            key=lambda size: SIZES_LIST.index(size) if size in SIZES_LIST else 99),
        'available_images': sorted([image for image in all_images if image.color == current_color],
                                    key=lambda image: (image.display_order, image.id)),
        'current_variant': next((variant for variant in all_variants if variant.color.id == current_color.id), None),
        'current_color_variants': [variant for variant in all_variants if variant.color_id == current_color.id],
        'is_favorited': is_favorited,
        'related_products': related_products,
    }

    return render(request, 'products/product.html', context)