from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ...infrastructure.repository import (
    SubscriptionPlanRepository,
    SubscriptionRepository,
)
from ...infrastructure.services.stripe_service import StripeService
from ...use_cases import (
    CancelSubscriptionUseCase,
    CreateBillingPortalRequest,
    CreateBillingPortalSessionUseCase,
    CreateCheckoutSessionRequest,
    CreateCheckoutSessionUseCase,
)

stripe_service = StripeService()
plan_repository = SubscriptionPlanRepository()
subscription_repository = SubscriptionRepository()

create_checkout_use_case = CreateCheckoutSessionUseCase(
    stripe_service, plan_repository, subscription_repository
)
create_billing_portal_use_case = CreateBillingPortalSessionUseCase(
    stripe_service, subscription_repository
)
cancel_subscription_use_case = CancelSubscriptionUseCase(
    stripe_service, subscription_repository
)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
async def create_checkout_session(request):
    """Crea una sesión de checkout para suscripción"""
    try:
        data = request.data
        checkout_request = CreateCheckoutSessionRequest(
            user_id=str(request.user.id),
            plan_id=data.get("plan_id"),
            success_url=data.get("success_url"),
            cancel_url=data.get("cancel_url"),
            allow_promotion_codes=data.get("allow_promotion_codes", True),
        )
        result = await create_checkout_use_case.execute(checkout_request)
        return Response({"url": result["url"], "session_id": result["session_id"]})
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
async def create_billing_portal_session(request):
    """Crea una sesión del portal de facturación"""
    try:
        data = request.data
        portal_request = CreateBillingPortalRequest(
            user_id=str(request.user.id), return_url=data.get("return_url")
        )
        result = await create_billing_portal_use_case.execute(portal_request)
        return Response({"url": result["url"]})
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
async def cancel_subscription(request):
    """Cancela la suscripción del usuario"""
    try:
        data = request.data
        subscription_id = data.get("subscription_id")
        if not subscription_id:
            return Response(
                {"error": "subscription_id es requerido"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        success = await cancel_subscription_use_case.execute(subscription_id)
        if success:
            return Response({"message": "Suscripción cancelada exitosamente"})
        else:
            return Response(
                {"error": "No se pudo cancelar la suscripción"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
