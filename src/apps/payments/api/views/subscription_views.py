from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.mixins import UseCaseAPIViewMixin

from ...infrastructure.repository import (
    SubscriptionPlanRepository,
    SubscriptionRepository,
)
from ...use_cases import GetSubscriptionPlansUseCase, GetUserSubscriptionUseCase
from ..serializers.schemas import (
    ErrorResponseSerializer,
    SubscriptionPlansResponseSerializer,
    UserSubscriptionWrapperSerializer,
)


class GetSubscriptionPlansAPIView(UseCaseAPIViewMixin):
    """Vista para obtener todos los planes de suscripción disponibles con casos de uso optimizados"""

    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.plan_repository = SubscriptionPlanRepository()
        self.get_plans_use_case = GetSubscriptionPlansUseCase(self.plan_repository)

    @extend_schema(
        tags=["Payments"],
        description="Get all available subscription plans",
        responses={
            200: SubscriptionPlansResponseSerializer,
            500: ErrorResponseSerializer,
        },
    )
    def get(self, request):
        """Obtiene todos los planes de suscripción disponibles"""
        self.log_request_info("GetSubscriptionPlans", f"User: {request.user.id}")

        try:
            # Usar el helper para ejecutar casos de uso
            plans = self.handle_use_case_execution(self.get_plans_use_case)

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

            self.logger.info(f"Retrieved {len(plans_data)} subscription plans")
            return Response({"plans": plans_data})

        except Exception as e:
            self.logger.error(f"Error getting subscription plans: {str(e)}")
            return Response(
                {"error": "Failed to retrieve subscription plans"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class GetUserSubscriptionAPIView(UseCaseAPIViewMixin):
    """Vista para obtener la suscripción del usuario autenticado con casos de uso optimizados"""

    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.subscription_repository = SubscriptionRepository()
        self.get_subscription_use_case = GetUserSubscriptionUseCase(
            self.subscription_repository
        )

    @extend_schema(
        tags=["Payments"],
        description="Get user subscription details",
        responses={
            200: UserSubscriptionWrapperSerializer,
            500: ErrorResponseSerializer,
        },
    )
    def get(self, request):
        """Obtiene la suscripción del usuario autenticado"""
        self.log_request_info("GetUserSubscription", f"User: {request.user.id}")

        try:
            # Usar el helper para ejecutar casos de uso
            subscription = self.handle_use_case_execution(
                self.get_subscription_use_case, str(request.user.id)
            )

            if not subscription:
                self.logger.info(f"No subscription found for user {request.user.id}")
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
                    subscription.trial_end.isoformat()
                    if subscription.trial_end
                    else None
                ),
                "canceled_at": (
                    subscription.canceled_at.isoformat()
                    if subscription.canceled_at
                    else None
                ),
                "is_active": subscription.is_active,
                "is_on_trial": subscription.is_on_trial,
            }

            self.logger.info(f"Retrieved subscription data for user {request.user.id}")
            return Response({"subscription": subscription_data})

        except Exception as e:
            self.logger.error(f"Error getting user subscription: {str(e)}")
            return Response(
                {"error": "Failed to retrieve user subscription"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
