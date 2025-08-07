from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ...infrastructure.repository import InvoiceRepository, SubscriptionRepository
from ...infrastructure.services.stripe_service import StripeService
from ...use_cases import GetInvoiceHistoryUseCase, GetUpcomingInvoiceUseCase

stripe_service = StripeService()
subscription_repository = SubscriptionRepository()
invoice_repository = InvoiceRepository()

get_upcoming_invoice_use_case = GetUpcomingInvoiceUseCase(
    stripe_service, subscription_repository
)
get_invoice_history_use_case = GetInvoiceHistoryUseCase(invoice_repository)


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
                "created_at": (
                    invoice.created_at.isoformat() if invoice.created_at else None
                ),
            }
            for invoice in invoices
        ]
        return Response({"invoices": invoices_data})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
