from django.shortcuts import render, get_object_or_404, redirect
from .cart import Cart
from products.models import ProductVariant
from django.contrib import messages


def carts_list(request):
    cart = Cart(request)
    return render(request, 'carts/carts_list.html', {'carts': cart})


def carts_add(request, variant_id):
    """
    DEPRECATED (P4.0): Legacy template 加购端点。
    GET ?quantity=N 会改 session — 刷新／预抓都会偷偷加件。
    新 client 必须用 POST /api/v1/cart/items/（body: variant_id + quantity）。
    本 view 保留给 carts_list.html；P6/P7 才移除。
    """
    cart = Cart(request)

    # 從 DB 撈出 variant，找不到就 404
    variant = get_object_or_404(ProductVariant, id=variant_id)

    # 數量來源：優先讀 GET 的 quantity，沒有就讀 POST，再沒有就預設 1
    # 同時支援 GET（連結）與 POST（表單）兩種呼叫方式
    quantity = int(request.GET.get('quantity', request.POST.get('quantity', 1)))

    cart.add(variant=variant, quantity=quantity)

    # 加完導回購物車頁
    return redirect('carts:list')


def carts_remove(request, variant_id):
    #從購物車移除商品（整項移除，不是減數量）。
    cart = Cart(request)
    variant = get_object_or_404(ProductVariant, id=variant_id)

    cart.remove(variant)
    return redirect('carts:list')


def add_to_cart(request):
    # 商品詳情頁的「加入購物車」。
    # 只接受 POST，GET 直接踢回商品列表
    if request.method == 'POST':

        # 從 POST 表單取出欄位
        sku = request.POST.get('sku')
        product_slug = request.POST.get('product_slug')
        quantity = int(request.POST.get('demo_vertical2', 1))  # 前端的 input name

        # sku 為空或標記為 'out-of-stock' 都不接受
        if not sku or sku == 'out-of-stock':
            messages.error(request, "Please select the valid product size first")
            # HTTP_REFERER：使用者是從哪個頁面來的，就導回哪裡
            # 找不到時 fallback 到商品列表
            return redirect(request.META.get('HTTP_REFERER', 'products:list'))

        # 用 SKU 從 DB 撈出 variant 物件
        # 因為 Cart.add() 需要的是 variant 物件，不是 sku 字串
        variant = get_object_or_404(ProductVariant, sku=sku)

        # 建立 Cart 物件並加入商品
        cart = Cart(request)
        cart.add(variant=variant, quantity=quantity)

        # 成功訊息 + 導回原本的頁面
        messages.success(request, f"成功將 {variant.product.name} ({variant.size}) 加入購物車！")

        return redirect('products:product', slug=product_slug)

    # 用 GET 偷敲網址 → 直接踢回商品列表
    return redirect('products:list')