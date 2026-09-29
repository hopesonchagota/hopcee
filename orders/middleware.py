from .models import Cart


class CartCountMiddleware:
    """Attaches request.cart_count so the navbar badge works on every page,
    for guests and logged-in staff alike — carts are keyed by session, not
    by user account."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.session.session_key:
            request.session.save()

        request.cart_count = 0
        cart = Cart.objects.filter(session_key=request.session.session_key).first()
        if cart is not None:
            request.cart_count = sum(item.quantity for item in cart.items.all())

        return self.get_response(request)
