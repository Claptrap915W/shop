from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.contrib import messages
from PIL import Image
from loguru import logger

from products.models import Product
from users.models import UserProfile
from orders.models import Order
from .forms import RegisterForm, ProfileUpdateForm, CustomPasswordForm
from carts.services import merge_session_cart_into_db


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            try:
                merge_session_cart_into_db(request, user)
            except Exception:
                logger.exception(
                    f'Failed to merge session cart for user {user.username}'
                )
            login(request, user)
            return redirect("pages:index")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile_form = ProfileUpdateForm(instance=profile, user=user)
    pwd_form = CustomPasswordForm(user)

    if request.method == "POST":
        profile_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=profile, user=user
        )
        pwd_form = CustomPasswordForm(user, request.POST)

        password_attempted = bool(request.POST.get('new_password1'))
        profile_ok = profile_form.is_valid()
        password_ok = pwd_form.is_valid() if password_attempted else True

        if profile_ok and password_ok:
            user.first_name = profile_form.cleaned_data['first_name']
            user.last_name = profile_form.cleaned_data['last_name']
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if profile.avatar:
                profile.save()
                img_path = profile.avatar.path
                try:
                    img = Image.open(img_path).convert("RGB")
                    x = int(profile.crop_x)
                    y = int(profile.crop_y)
                    w = int(profile.crop_w)
                    h = int(profile.crop_h)

                    if w > 0 and h > 0:
                        img = img.crop((x, y, x + w, y + h))
                    img = img.resize((300, 300), Image.Resampling.LANCZOS)
                    img.save(img_path, "JPEG", quality=85)
                except Exception:
                    pass
            else:
                profile.save()

            if password_attempted:
                pwd_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Profile and password updated successfully.')
            else:
                messages.success(request, 'Profile updated successfully.')

            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')

    context = {
        'profile_form': profile_form,
        'pwd_form': pwd_form,
        'user': user,
        'profile': profile,
    }
    return render(request, "accounts/profile.html", context)


class AccountDashboard(LoginRequiredMixin, TemplateView):
    template_name = "accounts/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["user"] = user

        profile, _ = UserProfile.objects.get_or_create(user=user)

        context["point_balance"] = profile.points
        context["order_history"] = Order.objects.filter(user=user).count()
        context["total_favourites"] = profile.favorites.count()
        return context


@login_required
def order_history(request):
    orders = (
        Order.objects.filter(user=request.user)
        .prefetch_related('items')
        .select_related('payment')
        .order_by('-created_at')
    )
    return render(request, 'accounts/orders.html', {
        'order_list': orders,
        'user': request.user,
    })


@login_required
def order_detail(request, order_no):
    order = get_object_or_404(
        Order.objects.select_related('payment').prefetch_related('items'),
        order_no=order_no,
        user=request.user,
    )
    return render(request, 'accounts/order_detail.html', {
        'order': order,
        'user': request.user,
    })


@login_required
def favourites(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    fav_list = profile.favorites.all()
    return render(request, "accounts/favourites.html", {
        "fav_list": fav_list,
        "user": request.user,
    })


@login_required
def toggle_favourite(request, product_id):
    profile = request.user.profile
    product = get_object_or_404(Product, id=product_id)

    if product in profile.favorites.all():
        profile.favorites.remove(product)
        status = 'removed'
    else:
        profile.favorites.add(product)
        status = 'added'

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': status, 'product_id': product_id})
    return redirect(request.META.get('HTTP_REFERER', 'products:list'))
