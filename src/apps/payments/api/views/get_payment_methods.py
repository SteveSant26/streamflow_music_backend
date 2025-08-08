from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.mixins import UseCaseAPIViewMixin

from ...infrastructure.repository import PaymentMethodRepository
from ...use_cases import GetPaymentMethodsUseCase
from ..serializers.schemas import (
    ErrorResponseSerializer,
    PaymentMethodsResponseSerializer,
)


class GetPaymentMethodsAPIView(UseCaseAPIViewMixin):
    """Vista para obtener los métodos de pago del usuario autenticado con casos de uso optimizados"""

    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.payment_method_repository = PaymentMethodRepository()
        self.get_payment_methods_use_case = GetPaymentMethodsUseCase(
            self.payment_method_repository
        )

    @extend_schema(
        tags=["Payments"],
        description="Get user payment methods",
        responses={200: PaymentMethodsResponseSerializer, 500: ErrorResponseSerializer},
    )
    def get(self, request):
        """Obtiene los métodos de pago del usuario autenticado"""
        self.log_request_info("GetPaymentMethods", f"User: {request.user.id}")

        try:
            user_id = str(request.user.id)

            # Usar el helper para ejecutar casos de uso
            methods = self.handle_use_case_execution(
                self.get_payment_methods_use_case, user_id
            )

            methods_data = [
                {
                    "id": m.id,
                    "user_id": m.user_id,
                    "type": m.type,
                    "last4": m.last4,
                    "exp_month": m.exp_month,
                    "exp_year": m.exp_year,
                    "brand": m.brand,
                    "is_default": m.is_default,
                    "created_at": m.created_at.isoformat() if m.created_at else None,
                }
                for m in methods
            ]

            self.logger.info(
                f"Retrieved {len(methods_data)} payment methods for user {request.user.id}"
            )
            return Response({"payment_methods": methods_data})

        except Exception as e:
            self.logger.error(f"Error getting payment methods: {str(e)}")
            return Response(
                {"error": "Failed to retrieve payment methods"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
