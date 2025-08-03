"""
API views for payments
"""
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..application.use_cases import (
    CancelSubscriptionUseCase,
    CreateBillingPortalRequest,
    CreateBillingPortalSessionUseCase,
    CreateCheckoutSessionRequest,
    CreateCheckoutSessionUseCase,
    GetInvoiceHistoryUseCase,
    GetPaymentMethodsUseCase,
    GetSubscriptionPlansUseCase,
    GetUpcomingInvoiceUseCase,
    GetUserSubscriptionUseCase,
    ProcessStripeWebhookUseCase,
)
from ..infrastructure.repositories import (
    InvoiceRepository,
    PaymentMethodRepository,
    PaymentRepository,
    StripeWebhookRepository,
    SubscriptionPlanRepository,
    SubscriptionRepository,
)
from ..infrastructure.services.stripe_service import StripeService

# Inicializar dependencias
stripe_service = StripeService()
plan_repository = SubscriptionPlanRepository()
subscription_repository = SubscriptionRepository()
payment_method_repository = PaymentMethodRepository()
invoice_repository = InvoiceRepository()
payment_repository = PaymentRepository()
webhook_repository = StripeWebhookRepository()

# Inicializar casos de uso
get_plans_use_case = GetSubscriptionPlansUseCase(plan_repository)
get_subscription_use_case = GetUserSubscriptionUseCase(subscription_repository)
create_checkout_use_case = CreateCheckoutSessionUseCase(
    stripe_service, plan_repository, subscription_repository
)
create_billing_portal_use_case = CreateBillingPortalSessionUseCase(
    stripe_service, subscription_repository
)
cancel_subscription_use_case = CancelSubscriptionUseCase(
    stripe_service, subscription_repository
)
get_payment_methods_use_case = GetPaymentMethodsUseCase(payment_method_repository)
get_upcoming_invoice_use_case = GetUpcomingInvoiceUseCase(
    stripe_service, subscription_repository
)
get_invoice_history_use_case = GetInvoiceHistoryUseCase(invoice_repository)
process_webhook_use_case = ProcessStripeWebhookUseCase(
    stripe_service, subscription_repository, invoice_repository, payment_repository
)


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
            "trial_start": subscription.trial_start.isoformat()
            if subscription.trial_start
            else None,
            "trial_end": subscription.trial_end.isoformat()
            if subscription.trial_end
            else None,
            "canceled_at": subscription.canceled_at.isoformat()
            if subscription.canceled_at
            else None,
            "is_active": subscription.is_active,
            "is_on_trial": subscription.is_on_trial,
        }

        return Response({"subscription": subscription_data})

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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


@api_view(["GET"])
@permission_classes([IsAuthenticated])
async def get_payment_methods(request):
    """Obtiene los métodos de pago del usuario"""
    try:
        payment_methods = await get_payment_methods_use_case.execute(
            str(request.user.id)
        )

        methods_data = [
            {
                "id": pm.id,
                "stripe_payment_method_id": pm.stripe_payment_method_id,
                "type": pm.type,
                "card": {
                    "brand": pm.card_brand,
                    "last4": pm.card_last4,
                    "exp_month": pm.card_exp_month,
                    "exp_year": pm.card_exp_year,
                }
                if pm.card_brand
                else None,
                "is_default": pm.is_default,
                "created_at": pm.created_at.isoformat(),
            }
            for pm in payment_methods
        ]

        return Response({"payment_methods": methods_data})

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
async def get_upcoming_invoice(request):
    """Obtiene la próxima factura del usuario"""
    try:
        invoice = await get_upcoming_invoice_use_case.execute(str(request.user.id))

        if not invoice:
            return Response({"invoice": None})

        return Response({"invoice": invoice})

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
async def get_invoice_history(request):
    """Obtiene el historial de facturas del usuario"""
    try:
        limit = int(request.GET.get("limit", 10))
        invoices = await get_invoice_history_use_case.execute(
            str(request.user.id), limit
        )

        invoices_data = [
            {
                "id": invoice.id,
                "stripe_invoice_id": invoice.stripe_invoice_id,
                "amount": invoice.amount,
                "currency": invoice.currency,
                "status": invoice.status.value,
                "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
                "paid_at": invoice.paid_at.isoformat() if invoice.paid_at else None,
                "created_at": invoice.created_at.isoformat(),
            }
            for invoice in invoices
        ]

        return Response({"invoices": invoices_data})

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
async def get_stripe_public_key(request):
    """Obtiene la clave pública de Stripe"""
    from django.conf import settings

    return Response({"publishable_key": settings.STRIPE_PUBLISHABLE_KEY})


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(View):
    """Vista para manejar webhooks de Stripe"""

    async def post(self, request):
        """Procesa eventos de webhook de Stripe"""
        try:
            payload = request.body
            signature = request.META.get("HTTP_STRIPE_SIGNATURE")

            if not signature:
                return HttpResponse("Firma faltante", status=400)

            success = await process_webhook_use_case.execute(payload, signature)

            if success:
                return HttpResponse("OK")
            else:
                return HttpResponse("Error procesando webhook", status=400)

        except Exception as e:
            print(f"Error en webhook: {e}")
            return HttpResponse("Error interno", status=500)
