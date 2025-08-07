from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ...infrastructure.repository import PaymentMethodRepository
from ...use_cases import GetPaymentMethodsUseCase

payment_method_repository = PaymentMethodRepository()
get_payment_methods_use_case = GetPaymentMethodsUseCase(payment_method_repository)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
async def get_payment_methods(request):
    """Obtiene los métodos de pago del usuario autenticado"""
    try:
        user_id = str(request.user.id)
        methods = await get_payment_methods_use_case.execute(user_id)
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
        return Response({"payment_methods": methods_data})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
