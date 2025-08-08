from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.mixins import UseCaseAPIViewMixin

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
from ..serializers.schemas import (
    BillingPortalRequestSerializer,
    BillingPortalResponseSerializer,
    CancelSubscriptionRequestSerializer,
    CancelSubscriptionResponseSerializer,
    CheckoutSessionRequestSerializer,
    CheckoutSessionResponseSerializer,
    ErrorResponseSerializer,
)


class CreateCheckoutSessionAPIView(UseCaseAPIViewMixin):
    """Vista para crear una sesión de checkout para suscripción con casos de uso optimizados"""

    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stripe_service = StripeService()
        self.plan_repository = SubscriptionPlanRepository()
        self.subscription_repository = SubscriptionRepository()
        self.create_checkout_use_case = CreateCheckoutSessionUseCase(
            self.stripe_service, self.plan_repository, self.subscription_repository
        )

    @extend_schema(
        tags=["Payments"],
        description="Create a checkout session for subscription",
        request=CheckoutSessionRequestSerializer,
        responses={
            200: CheckoutSessionResponseSerializer,
            400: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
    )
    def post(self, request):
        """Crea una sesión de checkout para suscripción"""
        self.log_request_info("CreateCheckoutSession", f"User: {request.user.id}")

        try:
            data = request.data

            # Validar datos requeridos
            required_fields = ["plan_id", "success_url", "cancel_url"]
            for field in required_fields:
                if not data.get(field):
                    return Response(
                        {"error": f"Missing required field: {field}"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            checkout_request = CreateCheckoutSessionRequest(
                user_id=str(request.user.id),
                plan_id=data.get("plan_id"),
                success_url=data.get("success_url"),
                cancel_url=data.get("cancel_url"),
                allow_promotion_codes=data.get("allow_promotion_codes", True),
                email=data.get("email")
                or getattr(getattr(request, "user", None), "email", None),
                name=data.get("name")
                or getattr(
                    getattr(request, "user", None), "get_full_name", lambda: None
                )()
                or getattr(getattr(request, "user", None), "username", None),
            )

            # Usar el helper para ejecutar casos de uso
            result = self.handle_use_case_execution(
                self.create_checkout_use_case, checkout_request
            )

            self.logger.info(f"Checkout session created for user {request.user.id}")
            return Response({"url": result["url"], "session_id": result["session_id"]})

        except ValueError as e:
            self.logger.error(f"Validation error creating checkout session: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            self.logger.error(f"Error creating checkout session: {str(e)}")
            return Response(
                {"error": "Failed to create checkout session"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CreateBillingPortalSessionAPIView(UseCaseAPIViewMixin):
    """Vista para crear una sesión del portal de facturación con casos de uso optimizados"""

    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stripe_service = StripeService()
        self.subscription_repository = SubscriptionRepository()
        self.create_billing_portal_use_case = CreateBillingPortalSessionUseCase(
            self.stripe_service, self.subscription_repository
        )

    @extend_schema(
        tags=["Payments"],
        description="Create a billing portal session",
        request=BillingPortalRequestSerializer,
        responses={
            200: BillingPortalResponseSerializer,
            400: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
    )
    def post(self, request):
        """Crea una sesión del portal de facturación"""
        self.log_request_info("CreateBillingPortalSession", f"User: {request.user.id}")

        try:
            data = request.data

            # Validar datos requeridos
            if not data.get("return_url"):
                return Response(
                    {"error": "Missing required field: return_url"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            portal_request = CreateBillingPortalRequest(
                user_id=str(request.user.id), return_url=data.get("return_url")
            )

            # Usar el helper para ejecutar casos de uso
            result = self.handle_use_case_execution(
                self.create_billing_portal_use_case, portal_request
            )

            self.logger.info(
                f"Billing portal session created for user {request.user.id}"
            )
            return Response({"url": result["url"]})

        except ValueError as e:
            self.logger.error(
                f"Validation error creating billing portal session: {str(e)}"
            )
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            self.logger.error(f"Error creating billing portal session: {str(e)}")
            return Response(
                {"error": "Failed to create billing portal session"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CancelSubscriptionAPIView(UseCaseAPIViewMixin):
    """Vista para cancelar la suscripción del usuario con casos de uso optimizados"""

    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stripe_service = StripeService()
        self.subscription_repository = SubscriptionRepository()
        self.cancel_subscription_use_case = CancelSubscriptionUseCase(
            self.stripe_service, self.subscription_repository
        )

    @extend_schema(
        tags=["Payments"],
        description="Cancel user subscription",
        request=CancelSubscriptionRequestSerializer,
        responses={
            200: CancelSubscriptionResponseSerializer,
            400: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
    )
    def post(self, request):
        """Cancela la suscripción del usuario"""
        self.log_request_info("CancelSubscription", f"User: {request.user.id}")

        try:
            data = request.data
            subscription_id = data.get("subscription_id")

            # Validar datos requeridos
            if not subscription_id:
                return Response(
                    {"error": "subscription_id is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Usar el helper para ejecutar casos de uso
            success = self.handle_use_case_execution(
                self.cancel_subscription_use_case, subscription_id
            )

            if success:
                self.logger.info(
                    f"Subscription {subscription_id} cancelled successfully"
                )
                return Response({"message": "Subscription cancelled successfully"})
            else:
                self.logger.warning(f"Failed to cancel subscription {subscription_id}")
                return Response(
                    {"error": "Could not cancel subscription"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except ValueError as e:
            self.logger.error(f"Validation error canceling subscription: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            self.logger.error(f"Error canceling subscription: {str(e)}")
            return Response(
                {"error": "Failed to cancel subscription"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
