from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Product, CustomUser
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Product)
def notify_users_on_product_creation(sender, instance, created, **kwargs):
    if created:  # Only notify on creation
        # Fetch users who should be notified
        users = CustomUser.objects.exclude(email="").filter(user_type__in=['Warehouse', 'Procurement'])
        recipient_list = [user.email for user in users]

        # Exit if no recipients are found
        if not recipient_list:
            logger.info("No recipients found for product creation email.")
            return

        # Email content
        subject = "New Product Created"
        message = f"A new product has been added:\n\n" \
                  f"Category: {instance.category or 'N/A'}\n" \
                  f"Color/Design: {instance.color_design or 'N/A'}\n" \
                  f"Block No: {instance.block_no or 'N/A'}\n" \
                  f"Bundles: {instance.bundles or 'N/A'}\n" \
                  f"Price: ${instance.price or 'N/A'}\n\n" \
                  f"Check it out in the system for more details."
        from_email = settings.DEFAULT_FROM_EMAIL  # or 'your_email@gmail.com'

        # Send the email
        try:
            send_mail(subject, message, from_email, recipient_list)
            logger.info(f"Email sent successfully to: {recipient_list}")
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
