from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.mixins import UseCaseAPIViewMixin

from ...infrastructure.repository import InvoiceRepository, SubscriptionRepository
from ...infrastructure.services.stripe_service import StripeService
from ...use_cases import GetInvoiceHistoryUseCase, GetUpcomingInvoiceUseCase
from ..serializers import InvoiceSerializer


class GetUpcomingInvoiceAPIView(UseCaseAPIViewMixin):
    """Vista para obtener la próxima factura del usuario con casos de uso optimizados"""

    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stripe_service = StripeService()
        self.subscription_repository = SubscriptionRepository()
        self.get_upcoming_invoice_use_case = GetUpcomingInvoiceUseCase(
            self.stripe_service, self.subscription_repository
        )

    @extend_schema(
        tags=["Payments"],
        description="Get upcoming invoice for the authenticated user",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "invoice": {
                        "anyOf": [
                            {"type": "object"},
                            {"type": "null"},
                        ],
                        "description": "Upcoming invoice details or null if none",
                    }
                },
            },
            500: {
                "type": "object",
                "properties": {"error": {"type": "string"}},
            },
        },
    )
    def get(self, request):
        """Obtiene la próxima factura del usuario"""
        self.log_request_info("GetUpcomingInvoice", f"User: {request.user.id}")

        try:
            # Usar el helper para ejecutar casos de uso
            invoice = self.handle_use_case_execution(
                self.get_upcoming_invoice_use_case, str(request.user.id)
            )

            if not invoice:
                self.logger.info(
                    f"No upcoming invoice found for user {request.user.id}"
                )
                return Response({"invoice": None})

            self.logger.info(f"Retrieved upcoming invoice for user {request.user.id}")
            return Response({"invoice": invoice})

        except Exception as e:
            self.logger.error(f"Error getting upcoming invoice: {str(e)}")
            return Response(
                {"error": "Failed to retrieve upcoming invoice"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class GetInvoiceHistoryAPIView(UseCaseAPIViewMixin):
    """Vista para obtener el historial de facturas del usuario con casos de uso optimizados y paginación"""

    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.invoice_repository = InvoiceRepository()
        self.get_invoice_history_use_case = GetInvoiceHistoryUseCase(
            self.invoice_repository
        )

    def get_serializer_class(self):
        """Especifica el serializador para la paginación"""
        return InvoiceSerializer

    @extend_schema(
        tags=["Payments"],
        description="Get invoice history for the authenticated user with pagination",
        parameters=UseCaseAPIViewMixin.get_pagination_parameters(),
        responses={
            200: {
                "type": "object",
                "properties": {
                    "count": {"type": "integer"},
                    "next": {"type": "string", "nullable": True},
                    "previous": {"type": "string", "nullable": True},
                    "results": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "stripe_invoice_id": {"type": "string"},
                                "amount": {"type": "integer"},
                                "currency": {"type": "string"},
                                "status": {"type": "string"},
                                "due_date": {"type": "string", "format": "date-time"},
                                "paid_at": {"type": "string", "format": "date-time"},
                                "created_at": {"type": "string", "format": "date-time"},
                            },
                        },
                    },
                },
            },
            400: {
                "type": "object",
                "properties": {"error": {"type": "string"}},
            },
            500: {
                "type": "object",
                "properties": {"error": {"type": "string"}},
            },
        },
    )
    def get(self, request):
        """Obtiene el historial de facturas del usuario con paginación"""
        self.log_request_info("GetInvoiceHistory", f"User: {request.user.id}")

        try:
            # Usar el helper para ejecutar casos de uso
            invoices = self.handle_use_case_execution(
                self.get_invoice_history_use_case, str(request.user.id)
            )

            # Usar paginación automática
            return self.paginate_and_respond(invoices, request)

        except Exception as e:
            self.logger.error(f"Error getting invoice history: {str(e)}")
            return Response(
                {"error": "Failed to retrieve invoice history"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
