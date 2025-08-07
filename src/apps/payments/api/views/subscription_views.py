from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ...infrastructure.repository import (
    SubscriptionPlanRepository,
    SubscriptionRepository,
)
from ...use_cases import GetSubscriptionPlansUseCase, GetUserSubscriptionUseCase

# Inicializar dependencias
plan_repository = SubscriptionPlanRepository()
subscription_repository = SubscriptionRepository()

# Inicializar casos de uso
get_plans_use_case = GetSubscriptionPlansUseCase(plan_repository)
get_subscription_use_case = GetUserSubscriptionUseCase(subscription_repository)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
async def get_subscription_plans(request):
    """Obtiene todos los planes de suscripción disponibles"""
    try:
        plans = await get_plans_use_case.execute()
        plans_data = [
            {
                "id": plan.id,
                "name": plan.name,
                "description": plan.description,
                "price": plan.price,
                "currency": plan.currency,
                "interval": plan.interval,
                "interval_count": plan.interval_count,
                "features": plan.features,
                "stripe_price_id": plan.stripe_price_id,
                "is_active": plan.is_active,
            }
            for plan in plans
        ]
        return Response({"plans": plans_data})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
async def get_user_subscription(request):
    """Obtiene la suscripción del usuario autenticado"""
    try:
        subscription = await get_subscription_use_case.execute(str(request.user.id))
        if not subscription:
            return Response({"subscription": None})
        subscription_data = {
            "id": subscription.id,
            "user_id": subscription.user_id,
            "plan_id": subscription.plan_id,
            "stripe_subscription_id": subscription.stripe_subscription_id,
            "stripe_customer_id": subscription.stripe_customer_id,
            "status": subscription.status.value,
            "current_period_start": subscription.current_period_start.isoformat(),
            "current_period_end": subscription.current_period_end.isoformat(),
            "trial_start": (
                subscription.trial_start.isoformat()
                if subscription.trial_start
                else None
            ),
            "trial_end": (
                subscription.trial_end.isoformat() if subscription.trial_end else None
            ),
            "canceled_at": (
                subscription.canceled_at.isoformat()
                if subscription.canceled_at
                else None
            ),
            "is_active": subscription.is_active,
            "is_on_trial": subscription.is_on_trial,
        }
        return Response({"subscription": subscription_data})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
