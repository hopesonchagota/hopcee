from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/item/<int:item_id>/update/", views.update_cart_item, name="update_cart_item"),
    path("checkout/", views.checkout, name="checkout"),
    path("success/<str:order_code>/", views.order_success, name="order_success"),
    path("track/", views.track_order, name="track_order"),
]
