"""
Django app configuration for payments
"""
<<<<<<< HEAD

=======
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.payments"
    verbose_name = "Payments"

    def ready(self):
        """Initialize app when Django starts"""
        # Import stripe settings
        try:
            from django.conf import settings

            if hasattr(settings, "STRIPE_SECRET_KEY") and settings.STRIPE_SECRET_KEY:
                import stripe

                stripe.api_key = settings.STRIPE_SECRET_KEY
                stripe.api_version = "2023-10-16"
        except ImportError:
            pass  # Stripe no instalado
