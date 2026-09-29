"""
WhatsApp integration helpers.

Two separate channels are used, on purpose:

1. CUSTOMER -> HOPCEE (the actual order request): the customer's browser is
   redirected to a wa.me "click-to-chat" link, pre-filled with the order
   details, addressed to Hopcee's own WhatsApp number. The customer taps
   Send. No server-side API or credentials are needed for this — it's the
   core ordering channel and always works.

2. HOPCEE -> CUSTOMER (status updates): optional, only if
   WHATSAPP_CLOUD_API_TOKEN / WHATSAPP_CLOUD_API_PHONE_ID (Meta's WhatsApp
   Cloud API) are configured. If not configured, it safely falls back to
   just logging the message so development keeps working without any
   external credentials.

Neither channel ever includes prices, subtotals, or totals — see
ORDER 34/NO-PRICES rule.
"""

import logging
from urllib.parse import quote

import requests
from django.conf import settings

logger = logging.getLogger("hopcee.whatsapp")


def normalize_phone(phone: str) -> str:
    """Turn a local Malawi number like 0991234567 into +265991234567."""
    phone = (phone or "").strip().replace(" ", "").replace("-", "")
    if phone.startswith("+"):
        return phone
    if phone.startswith("0"):
        return "+265" + phone[1:]
    if phone.startswith("265"):
        return "+" + phone
    return phone


def whatsapp_click_to_chat_link(phone: str, message: str) -> str:
    """Build a wa.me link that opens WhatsApp with a pre-filled message."""
    number = normalize_phone(phone).replace("+", "")
    return f"https://wa.me/{number}?text={quote(message)}"


def send_whatsapp_message(to_number: str, message: str, order=None) -> bool:
    """
    Attempt to send a WhatsApp message via the Cloud API (used only for
    Hopcee -> customer status updates). Always logs the attempt to the DB.
    Returns True if it was actually sent via the API, False if it only
    fell back to logging.
    """
    from .models import WhatsAppNotificationLog  # local import: avoid circularity

    to = normalize_phone(to_number)
    sent_via_api = False

    token = settings.WHATSAPP_CLOUD_API_TOKEN
    phone_id = settings.WHATSAPP_CLOUD_API_PHONE_ID

    if token and phone_id:
        url = f"https://graph.facebook.com/{settings.WHATSAPP_API_VERSION}/{phone_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "to": to.lstrip("+"),
            "type": "text",
            "text": {"body": message},
        }
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            sent_via_api = True
        except requests.RequestException:
            logger.exception("WhatsApp Cloud API send failed for %s", to)
    else:
        logger.info("[WhatsApp fallback — no API credentials set] To %s: %s", to, message)

    WhatsAppNotificationLog.objects.create(
        order=order, to_number=to, message=message, was_sent_via_api=sent_via_api
    )
    return sent_via_api


def status_update_message(order) -> str:
    """Hopcee -> customer. No prices."""
    status_text = {
        "pending": "has been received and is Pending — we'll head to the market soon.",
        "bought": f"has been Bought at {order.market.name}! Next stop: transport to Bunda Campus.",
        "in_transit": "is now on the way (In Transit) to LUANAR Bunda Campus.",
        "delivered": "has been Delivered. Thank you for using Hopcee!",
        "cancelled": "has been Cancelled. Message us on WhatsApp if this is unexpected.",
    }
    detail = status_text.get(order.status, f"status changed to {order.get_status_display()}.")
    return (
        f"Hello {order.customer_name}, your Hopcee order {order.order_code} {detail}\n"
        f"We'll keep you posted here on WhatsApp until it's in your hands."
    )


def order_whatsapp_message(order) -> str:
    """
    CUSTOMER -> HOPCEE. This is the text pre-filled into the wa.me link the
    customer's browser opens right after they submit the order form — it
    IS the order request. No prices, ever.
    """
    lines = [
        "Hello Hopcee, I'd like to submit an order request.",
        f"Order code: {order.order_code}",
        f"Name: {order.customer_name}",
        f"My WhatsApp number: {order.delivery_phone}",
        f"Market: {order.market.name}",
        "Items:",
    ]
    for item in order.items.all():
        lines.append(f"  • {item.quantity} x {item.product_name}")
    lines.append(f"Preferred delivery date: {order.delivery_date:%d %b %Y}")
    lines.append(f"Delivery point: {order.delivery_point}")
    if order.notes:
        lines.append(f"Notes: {order.notes}")
    lines.append("Please confirm availability, sourcing and the final amount. Thank you!")
    return "\n".join(lines)


def order_hopcee_link(order) -> str:
    """The wa.me link that sends the order request to Hopcee's own number."""
    from django.conf import settings as dj_settings

    return whatsapp_click_to_chat_link(dj_settings.HOPCEE["WHATSAPP_NUMBER"], order_whatsapp_message(order))
