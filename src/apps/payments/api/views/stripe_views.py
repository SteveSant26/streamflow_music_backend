from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.mixins import LoggingMixin

from ...infrastructure.repository import (
    InvoiceRepository,
    PaymentRepository,
    StripeWebhookRepository,
    SubscriptionRepository,
)
from ...infrastructure.services.stripe_service import StripeService
from ...use_cases import ProcessStripeWebhookUseCase

stripe_service = StripeService()
subscription_repository = SubscriptionRepository()
invoice_repository = InvoiceRepository()
payment_repository = PaymentRepository()
webhook_repository = StripeWebhookRepository()

process_webhook_use_case = ProcessStripeWebhookUseCase(
    stripe_service, subscription_repository, invoice_repository, payment_repository
)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_stripe_public_key(request):
    from django.conf import settings

    return Response({"publishable_key": settings.STRIPE_PUBLISHABLE_KEY})


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(LoggingMixin, View):
    """Vista para manejar webhooks de Stripe con logging integrado"""

    async def post(self, request):
        self.logger.info("Recibiendo webhook de Stripe")
        try:
            payload = request.body
            signature = request.META.get("HTTP_STRIPE_SIGNATURE")
            if not signature:
                self.logger.warning("Webhook sin firma recibido")
                return HttpResponse("Firma faltante", status=400)
            success = await process_webhook_use_case.execute(payload, signature)
            if success:
                self.logger.info("Webhook procesado exitosamente")
                return HttpResponse("OK")
            else:
                self.logger.error("Error procesando webhook")
                return HttpResponse("Error procesando webhook", status=400)
        except Exception as e:
            self.logger.error(f"Error en webhook: {e}")
            return HttpResponse("Error interno", status=500)
