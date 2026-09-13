from products.models import ProductVariant
from decimal import Decimal
from copy import deepcopy


class Cart:

    def __init__(self, request):
        self.session = request.session

        # 嘗試從 session 取出已有的購物車
        carts = self.session.get('carts')
        if not carts:
            # 第一次使用 → 建立空字典並寫進 session
            carts = self.session['carts'] = {}

        self.carts = carts

    def add(self, variant, quantity=1, override_quantity=False):
        # session key 必須是字串（JSON 規範）
        variant_id = str(variant.id)

        # 若購物車還沒有這項商品 → 先建立 entry
        if variant_id not in self.carts:
            self.carts[variant_id] = {'quantity': 0}

        # 根據模式決定是「累加」還是「覆蓋」
        if override_quantity:
            self.carts[variant_id]['quantity'] = quantity
        else:
            self.carts[variant_id]['quantity'] += quantity

        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, variant):
        variant_id = str(variant.id)

        if variant_id in self.carts:
            del self.carts[variant_id]
            self.save()

    def __iter__(self):
        variant_ids = self.carts.keys()
        if not variant_ids:
            return

        # 一次撈出所有 variant，預先 JOIN product 與 color，並 prefetch images
        variants = ProductVariant.objects.filter(
            id__in=variant_ids
        ).select_related('product', 'color').prefetch_related('product__images')

        # 複製一份來修改，避免污染 session 中原始的 carts 結構
        cart = deepcopy(self.carts)
        for variant in variants:
            cart[str(variant.id)]['variant'] = variant

        # 逐筆計算價格、找圖片，然後 yield 出去
        for item in cart.values():
            variant = item.get('variant')

            # 商品已被刪除（DB 撈不到）→ 跳過這筆，避免模板報錯
            if not variant:
                continue

            # 即時取價格（確保用到最新價格，不是加入購物車當時的舊價）
            price = Decimal(str(variant.final_price))
            item['price'] = price
            item['total_price'] = item['price'] * item['quantity']

            # --- 尋找對應顏色的圖片 ---
            color_image = None
            color_image_text = None

            if variant.color:
                # 在商品的多張圖中，找 color_id 與 variant 相符的那張
                for img in variant.product.images.all():
                    if variant.color_id == img.color_id:
                        color_image = img.image
                        color_image_text = img.alt_text
                        break

                # 找不到對應顏色的圖 → fallback 用商品封面圖
                if not color_image and variant.product.image:
                    color_image = variant.product.image
                    color_image_text = variant.product.name

            item['image'] = color_image
            item['image_text'] = color_image_text

            yield item #yield 產生 generator，呼叫端可逐筆取出，省記憶體

    def __len__(self):
        #回傳購物車的「總件數」（不是商品種類數）。
        return sum(item['quantity'] for item in self.carts.values())

    def get_total_price(self):
        #計算購物車總金額。
        variant_ids = self.carts.keys()

        # 一次撈出所有 variant 並 JOIN product（避免 N+1）
        variants = ProductVariant.objects.filter(id__in=variant_ids).select_related('product')

        total = Decimal('0')
        for variant in variants:
            # 從 session 字典取出對應數量（找不到視為 0）
            qty = self.carts.get(str(variant.id), {}).get('quantity', 0)
            total += Decimal(str(variant.final_price)) * qty

        return total

    def clear(self):
        # 清空整台購物車
        self.session.pop('carts', None)
        self.carts = self.session['carts'] = {}
        self.save()        