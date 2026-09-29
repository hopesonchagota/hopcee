from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Order, OrderStatusHistory
from .utils import send_whatsapp_message, status_update_message

_STATUS_FIELD_TRACKER = {}


@receiver(pre_save, sender=Order)
def _remember_previous_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            previous = Order.objects.get(pk=instance.pk)
            _STATUS_FIELD_TRACKER[instance.pk] = previous.status
        except Order.DoesNotExist:
            _STATUS_FIELD_TRACKER[instance.pk] = None
    else:
        _STATUS_FIELD_TRACKER[instance.pk] = None


@receiver(post_save, sender=Order)
def _notify_on_status_change(sender, instance, created, **kwargs):
    previous_status = _STATUS_FIELD_TRACKER.pop(instance.pk, None)

    if created:
        # The order request itself is handed to Hopcee by redirecting the
        # customer's browser to WhatsApp (see orders.views.checkout) — that
        # click-to-chat message IS the "order received" notice, sent by the
        # customer. We just record the starting status here.
        OrderStatusHistory.objects.create(order=instance, status=instance.status)
        return

    if previous_status is not None and previous_status != instance.status:
        OrderStatusHistory.objects.create(order=instance, status=instance.status)
        # Optional Hopcee -> customer status ping (falls back to a log
        # entry if no WhatsApp Cloud API credentials are configured).
        send_whatsapp_message(
            instance.delivery_phone, status_update_message(instance), order=instance
        )
