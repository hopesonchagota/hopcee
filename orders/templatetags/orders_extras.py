from django import template

from orders.utils import whatsapp_click_to_chat_link

register = template.Library()


@register.simple_tag
def whatsapp_link(phone, message=""):
    return whatsapp_click_to_chat_link(phone, message)


@register.filter
def mwk(value):
    try:
        return f"MWK {float(value):,.0f}"
    except (TypeError, ValueError):
        return value
