from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from catalog.models import Product

from .forms import CheckoutForm, OrderTrackingForm
from .models import Cart, CartItem, Order, OrderItem
from .utils import order_hopcee_link


def _get_or_create_cart(request):
    """Every visitor gets a cart tied to their browser session — no account
    or login needed to browse or order."""
    if not request.session.session_key:
        request.session.save()
    cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_available=True)
    cart = _get_or_create_cart(request)

    if not cart.is_empty:
        existing_market = cart.items.first().product.market_id
        if existing_market != product.market_id:
            messages.error(
                request,
                "Your order list already has items from another market. Please submit or clear "
                "it before adding products from a different market — Hopcee runs one "
                "trip per market per order.",
            )
            return redirect("orders:cart_detail")

    try:
        quantity = max(1, int(request.POST.get("quantity", 1)))
    except (TypeError, ValueError):
        quantity = 1

    item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={"quantity": quantity})
    if not created:
        item.quantity += quantity
        item.save()

    messages.success(request, f"Added {quantity} x {product.name} to your order list.")
    return redirect(request.META.get("HTTP_REFERER") or "orders:cart_detail")


@require_POST
def update_cart_item(request, item_id):
    cart = _get_or_create_cart(request)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    action = request.POST.get("action")
    if action == "increase":
        item.quantity += 1
        item.save()
    elif action == "decrease":
        item.quantity -= 1
        if item.quantity <= 0:
            item.delete()
        else:
            item.save()
    elif action == "remove":
        item.delete()
    return redirect("orders:cart_detail")


def cart_detail(request):
    cart = _get_or_create_cart(request)
    market = cart.items.first().product.market if not cart.is_empty else None
    return render(request, "orders/cart_detail.html", {"cart": cart, "market": market})


def checkout(request):
    cart = _get_or_create_cart(request)
    if cart.is_empty:
        messages.info(request, "Your order list is empty. Add some products first.")
        return redirect("core:products")

    market = cart.items.first().product.market

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.market = market
            order.status = Order.STATUS_PENDING
            order.save()

            for cart_item in cart.items.select_related("product"):
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    product_name=cart_item.product.name,
                    unit_price=cart_item.product.ordering_price,
                    quantity=cart_item.quantity,
                )
            order.recalculate_totals()
            cart.items.all().delete()

            messages.success(
                request,
                f"Order request {order.order_code} received! Send it to Hopcee on WhatsApp to confirm.",
            )
            return redirect("orders:order_success", order_code=order.order_code)
    else:
        form = CheckoutForm()

    return render(request, "orders/checkout.html", {"form": form, "cart": cart, "market": market})


def order_success(request, order_code):
    order = get_object_or_404(Order, order_code=order_code)
    whatsapp_link = order_hopcee_link(order)
    return render(request, "orders/order_success.html", {"order": order, "whatsapp_link": whatsapp_link})


def track_order(request):
    order = None
    searched = False
    if request.method == "POST":
        form = OrderTrackingForm(request.POST)
        searched = True
        if form.is_valid():
            code = form.cleaned_data["order_code"].strip().upper()
            phone = form.cleaned_data["phone_number"].strip()
            order = Order.objects.filter(order_code__iexact=code, delivery_phone__icontains=phone[-8:]).first()
            if not order:
                messages.error(request, "No matching order found. Double-check the code and phone number.")
    else:
        form = OrderTrackingForm()

    return render(request, "orders/track_order.html", {"form": form, "order": order, "searched": searched})
