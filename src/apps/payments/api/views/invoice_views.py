from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.mixins import UseCaseAPIViewMixin

from ...infrastructure.repository import InvoiceRepository, SubscriptionRepository
from ...infrastructure.services.stripe_service import StripeService
from ...use_cases import GetInvoiceHistoryUseCase, GetUpcomingInvoiceUseCase
from ..serializers import InvoiceSerializer
from ..serializers.schemas import (
    ErrorResponseSerializer,
    PaginatedInvoiceResponseSerializer,
    UpcomingInvoiceWrapperSerializer,
)


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
        responses={200: UpcomingInvoiceWrapperSerializer, 500: ErrorResponseSerializer},
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
            200: PaginatedInvoiceResponseSerializer,
            400: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
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
