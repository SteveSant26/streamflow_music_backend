from django.conf import settings
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.mixins import LoggingMixin, UseCaseAPIViewMixin

from ...infrastructure.repository import (
    InvoiceRepository,
    PaymentRepository,
    StripeWebhookRepository,
    SubscriptionRepository,
)
from ...infrastructure.services.stripe_service import StripeService
from ...use_cases import ProcessStripeWebhookUseCase
from ..serializers.schemas import (
    ErrorResponseSerializer,
    StripePublicKeyResponseSerializer,
)


class GetStripePublicKeyAPIView(UseCaseAPIViewMixin):
    """Vista para obtener la clave pública de Stripe con logging y casos de uso integrados"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Payments"],
        description="Get Stripe public key for client-side integration",
        responses={
            200: StripePublicKeyResponseSerializer,
            403: ErrorResponseSerializer,
        },
    )
    def get(self, request):
        """Obtiene la clave pública de Stripe"""
        self.log_request_info("GetStripePublicKey", f"User: {request.user.id}")

        try:
            public_key = settings.STRIPE_PUBLISHABLE_KEY
            if not public_key:
                self.logger.error("Stripe publishable key not configured")
                return Response(
                    {"error": "Stripe configuration error"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            self.logger.info("Stripe public key retrieved successfully")
            return Response({"publishable_key": public_key})

        except Exception as e:
            self.logger.error(f"Error retrieving Stripe public key: {str(e)}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(LoggingMixin, View):
    """Vista para manejar webhooks de Stripe con logging integrado y casos de uso optimizados"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Inicialización lazy de servicios y repositorios
        self._stripe_service = None
        self._subscription_repository = None
        self._invoice_repository = None
        self._payment_repository = None
        self._webhook_repository = None
        self._process_webhook_use_case = None

    @property
    def stripe_service(self):
        """Lazy loading del servicio Stripe"""
        if self._stripe_service is None:
            self._stripe_service = StripeService()
        return self._stripe_service

    @property
    def subscription_repository(self):
        """Lazy loading del repositorio de suscripciones"""
        if self._subscription_repository is None:
            self._subscription_repository = SubscriptionRepository()
        return self._subscription_repository

    @property
    def invoice_repository(self):
        """Lazy loading del repositorio de facturas"""
        if self._invoice_repository is None:
            self._invoice_repository = InvoiceRepository()
        return self._invoice_repository

    @property
    def payment_repository(self):
        """Lazy loading del repositorio de pagos"""
        if self._payment_repository is None:
            self._payment_repository = PaymentRepository()
        return self._payment_repository

    @property
    def webhook_repository(self):
        """Lazy loading del repositorio de webhooks"""
        if self._webhook_repository is None:
            self._webhook_repository = StripeWebhookRepository()
        return self._webhook_repository

    @property
    def process_webhook_use_case(self):
        """Lazy loading del caso de uso de procesamiento de webhooks"""
        if self._process_webhook_use_case is None:
            self._process_webhook_use_case = ProcessStripeWebhookUseCase(
                self.stripe_service,
                self.subscription_repository,
                self.invoice_repository,
                self.payment_repository,
            )
        return self._process_webhook_use_case

    def _validate_webhook_signature(self, payload, signature):
        """Valida la firma del webhook de Stripe"""
        if not signature:
            self.logger.warning("Webhook received without signature")
            return False
        return True

    def _log_webhook_processing(self, payload_size, signature_present):
        """Log información del webhook"""
        self.logger.info(
            f"Processing Stripe webhook - Payload size: {payload_size} bytes, "
            f"Signature present: {signature_present}"
        )

    async def post(self, request):
        """Procesa webhooks de Stripe de manera optimizada"""
        payload = request.body
        signature = request.META.get("HTTP_STRIPE_SIGNATURE")

        # Log información del webhook
        self._log_webhook_processing(len(payload), bool(signature))

        try:
            # Validar firma
            if not self._validate_webhook_signature(payload, signature):
                return HttpResponse("Missing or invalid signature", status=400)

            # Procesar webhook usando el caso de uso
            success = await self.process_webhook_use_case.execute(payload, signature)

            if success:
                self.logger.info("Webhook processed successfully")
                return HttpResponse("OK", status=200)
            else:
                self.logger.error("Failed to process webhook")
                return HttpResponse("Error processing webhook", status=400)

        except ValueError as e:
            self.logger.error(f"Invalid webhook payload: {str(e)}")
            return HttpResponse("Invalid payload", status=400)
        except Exception as e:
            self.logger.error(f"Unexpected error processing webhook: {str(e)}")
            return HttpResponse("Internal server error", status=500)
