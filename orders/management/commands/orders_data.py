import json
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from orders.models import Order, OrderItem, Payment
from products.models import ProductVariant

BASE_DIR = Path(__file__).resolve().parent.parent
IMPORT_DIR = BASE_DIR / 'import_files'
EXPORT_DIR = BASE_DIR / 'export_files'

def list_import_files():
    IMPORT_DIR.mkdir(parents=True, exist_ok=True)
    return sorted(IMPORT_DIR.glob('*.json'))

def normalize_phone(phone):
    return re.sub(r'[\s\-()]', '', str(phone or ''))

def is_valid_phone(phone):
    digits = re.sub(r'\D', '', normalize_phone(phone))
    return 7 <= len(digits) <= 15


def parse_str(value, default=''):
    if value is None:
        return default
    return str(value).strip()


def parse_decimal(value, default=None):
    if value is None or str(value).strip() == '':
        return default
    return Decimal(str(value))


def validate_decimal_field(errors, label, value):
    if value is None or str(value).strip() == '':
        return
    try:
        if Decimal(str(value)) < 0:
            errors.append(f'{label} 不能为负数')
    except (InvalidOperation, ValueError):
        errors.append(f'{label} 格式无效')


def validate_order(data):
    errors = []

    order_no = (data.get('order_no') or '').strip()
    username = (data.get('username') or '').strip()

    if not order_no:
        errors.append('缺少 order_no')
    elif Order.objects.filter(order_no=order_no).exists():
        errors.append(f'order_no 已存在: {order_no}')

    if not username:
        errors.append('缺少 username')
    elif not User.objects.filter(username=username).exists():
        errors.append(f'找不到用户: {username}')

    if not (data.get('full_name') or '').strip():
        errors.append('缺少 full_name')

    if not (data.get('email') or '').strip():
        errors.append('缺少 email')

    phone = (data.get('phone') or '').strip()
    if not phone:
        errors.append('缺少 phone')
    elif not is_valid_phone(phone):
        errors.append(f'不是有效的电话: {phone}')

    if not (data.get('address') or '').strip():
        errors.append('缺少 address')

    status = (data.get('status') or '').strip().lower()
    if status not in ('pending', 'paid', 'failed', 'cancelled'):
        errors.append(f'无效 status: {status}')

    items = data.get('items') or []
    if not items:
        errors.append('至少需要 1 个商品 item')
    else:
        for i, item in enumerate(items, start=1):
            sku = (item.get('sku') or '').strip()
            qty = item.get('quantity')

            if not sku:
                errors.append(f'第 {i} 项缺少 sku')
            elif not ProductVariant.objects.filter(sku=sku).exists():
                errors.append(f'找不到 SKU: {sku}')

            if not isinstance(qty, int) or qty < 1:
                errors.append(f'第 {i} 项 quantity 必须是 >= 1 的整数')

            validate_decimal_field(errors, f'第 {i} 项 price', item.get('price'))
            validate_decimal_field(errors, f'第 {i} 项 subtotal', item.get('subtotal'))

    validate_decimal_field(errors, 'total', data.get('total'))

    payment = data.get('payment') or {}
    pay_status = (payment.get('status') or '').strip().lower()
    if pay_status not in ('success', 'failed'):
        errors.append('payment.status 必须是 success 或 failed')

    validate_decimal_field(errors, 'payment.amount', payment.get('amount'))

    if status == 'paid' and pay_status != 'success':
        errors.append('status=paid 时 payment.status 必须是 success')

    return errors


@transaction.atomic
def save_one_order(data):
    user = User.objects.get(username=data['username'].strip())
    payment_data = data['payment']
    created_at = parse_datetime(data.get('created_at') or '') or timezone.now()
    paid_at = parse_datetime(payment_data.get('paid_at') or '')

    phone = normalize_phone(data['phone']).strip()

    order = Order.objects.create(
        user=user,
        order_no=data['order_no'].strip(),
        full_name=data['full_name'].strip(),
        email=data['email'].strip().lower(),
        phone=phone,
        address=data['address'].strip(),
        total=Decimal('0.00'),
        status=data['status'].strip().lower(),
    )
    Order.objects.filter(pk=order.pk).update(
        created_at=created_at,
        updated_at=created_at,
    )

    items_total = Decimal('0.00')

    for item in data['items']:
        item_sku = parse_str(item.get('sku'))
        variant = ProductVariant.objects.get(sku=item_sku)

        price = parse_decimal(item.get('price'), Decimal('0.00'))
        qty = int(item['quantity'])
        subtotal = parse_decimal(item.get('subtotal'), price * qty)
        items_total += subtotal

        OrderItem.objects.create(
            order=order,
            variant=variant,
            product_name=parse_str(item.get('product_name')),
            product_slug=parse_str(item.get('product_slug')),
            sku=item_sku,
            color_name=parse_str(item.get('color_name')),
            size=parse_str(item.get('size')),
            image_path=parse_str(item.get('image_path')),
            image_alt=parse_str(item.get('image_alt')),
            price=price,
            quantity=qty,
            subtotal=subtotal,
        )

    order_total = parse_decimal(data.get('total'), items_total)
    payment_amount = parse_decimal(payment_data.get('amount'), order_total)
    payment_method = parse_str(payment_data.get('method')) or 'credit_card'

    Payment.objects.create(
        order=order,
        method=payment_method,
        status=payment_data['status'].strip().lower(),
        amount=payment_amount,
        card_last_four=parse_str(payment_data.get('card_last_four'))[-4:],
        transaction_id=parse_str(payment_data.get('transaction_id')),
        paid_at=paid_at,
    )

    order.total = order_total
    order.save(update_fields=['total'])

    return order


def import_orders(filepath):
    path = Path(filepath)

    with path.open(encoding='utf-8') as f:
        payload = json.load(f)

    orders = payload.get('orders', [])
    accepted = []
    rejected = []

    for data in orders:
        order_no = (data.get('order_no') or '（无编号）').strip()
        errors = validate_order(data)

        if errors:
            rejected.append({'order_no': order_no, 'reasons': errors})
            continue
        
        try:
            order = save_one_order(data)
            accepted.append(order.order_no)
        except Exception as exc:
            rejected.append({
                'order_no': order_no,
                'reasons': [f'写入失败: {exc}'],
            })

    return {
        'accepted': accepted,
        'rejected': rejected,
        'total_in_file': len(orders),
    }


def get_export_filepath(filepath=None):
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    if filepath:
        return Path(filepath)

    today = timezone.localdate().strftime('%Y%m%d')
    filepath = EXPORT_DIR / f'orders_export_{today}.json'
    if filepath.exists():
        time_part = timezone.localtime().strftime('%H%M%S')
        filepath = EXPORT_DIR / f'orders_export_{today}_{time_part}.json'
    return filepath


def export_orders(filepath=None):
    filepath = get_export_filepath(filepath)

    orders = (
        Order.objects
        .select_related('user', 'payment')
        .prefetch_related('items')
        .order_by('created_at')
    )

    payload = {
        'meta': {
            'exported_at': timezone.localdate().isoformat(),
            'total_orders': orders.count(),
        },
        'orders': [],
    }

    for order in orders:
        payment = getattr(order, 'payment', None)
        payload['orders'].append({
            'order_no': order.order_no,
            'username': order.user.username,
            'full_name': order.full_name,
            'email': order.email,
            'phone': order.phone,
            'address': order.address,
            'status': order.status,
            'created_at': order.created_at.isoformat(),
            'total': str(order.total),
            'items': [
                {
                    'sku': item.sku,
                    'quantity': item.quantity,
                    'price': str(item.price),
                    'subtotal': str(item.subtotal),
                    'product_name': item.product_name,
                    'product_slug': item.product_slug,
                    'color_name': item.color_name,
                    'size': item.size,
                    'image_path': item.image_path,
                    'image_alt': item.image_alt,
                }
                for item in order.items.all()
            ],
            'payment': {
                'method': payment.method,
                'status': payment.status,
                'amount': str(payment.amount),
                'card_last_four': payment.card_last_four,
                'transaction_id': payment.transaction_id,
                'paid_at': payment.paid_at.isoformat() if payment.paid_at else None,
            } if payment else None,
        })

    with filepath.open('w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    return str(filepath)


@transaction.atomic
def clear_all_orders():
    item_count = OrderItem.objects.count()
    payment_count = Payment.objects.count()
    order_count = Order.objects.count()

    OrderItem.objects.all().delete()
    Payment.objects.all().delete()
    Order.objects.all().delete()

    return {
        'orders': order_count,
        'items': item_count,
        'payments': payment_count,
    }


class Command(BaseCommand):
    def handle(self, *args, **options):
        while True:
            self.stdout.write('')
            self.stdout.write('========== Orders 数据管理 ==========')
            self.stdout.write('1. 匯入 JSON')
            self.stdout.write('2. 匯出 JSON')
            self.stdout.write('3. 清空所有订单')
            self.stdout.write('0. 离开')
            self.stdout.write('====================================')

            choice = input('请选择功能 [0-3]: ').strip()

            if choice == '1':
                self.do_import()
            elif choice == '2':
                self.do_export()
            elif choice == '3':
                self.do_clear()
            elif choice == '0':
                self.stdout.write('已离开。')
                break
            else:
                self.stdout.write(self.style.WARNING('无效选项，请重新输入。'))

    def print_import_result(self, filename, result):
        if result.get('error'):
            self.stdout.write(self.style.ERROR(f'{filename}: {result["error"]}'))
            return

        self.stdout.write(self.style.SUCCESS(
            f'{filename}: 共 {result["total_in_file"]} 笔，'
            f'成功 {len(result["accepted"])}，拒绝 {len(result["rejected"])}'
        ))
        for item in result['rejected']:
            self.stdout.write(f"  ! {item['order_no']}")
            for reason in item['reasons']:
                self.stdout.write(f'      - {reason}')

    def do_import(self):
        files = list_import_files()
        if not files:
            self.stdout.write(self.style.ERROR(f'没有 JSON 文件: {IMPORT_DIR}'))
            return

        self.stdout.write(f'\nImport 文件夹: {IMPORT_DIR}')
        for i, filepath in enumerate(files, start=1):
            self.stdout.write(f'  {i}. {filepath.name}')
        self.stdout.write('  0. 返回')

        choice = input('请选择要匯入的文件编号: ').strip()
        if choice == '0':
            return

        try:
            filepath = files[int(choice) - 1]
        except (ValueError, IndexError):
            self.stdout.write(self.style.ERROR('无效选项'))
            return

        result = import_orders(filepath)
        self.print_import_result(filepath.name, result)

    def do_export(self):
        saved_path = export_orders()
        self.stdout.write(self.style.SUCCESS(f'已匯出到: {saved_path}'))

    def do_clear(self):
        confirm = input('确定要清空所有 Order / OrderItem / Payment 吗？输入 yes 确认: ').strip()
        if confirm.lower() != 'yes':
            self.stdout.write('已取消。')
            return

        counts = clear_all_orders()
        self.stdout.write(self.style.SUCCESS(
            f"已删除 {counts['orders']} 笔订单、"
            f"{counts['items']} 条明细、"
            f"{counts['payments']} 条付款记录"
        ))