from typing import Any, Dict, List

import stripe
from django.conf import settings

from ...domain.exceptions import (
    BillingPortalError,
    CheckoutSessionError,
    CustomerCreationError,
    InvoiceError,
    PaymentMethodError,
    StripeServiceError,
    SubscriptionError,
    WebhookError,
)
from ...domain.interfaces import IStripeService


class StripeService(IStripeService):
    """Implementación del servicio de Stripe"""

    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.api_version = "2023-10-16"

    def create_customer(self, user_profile_id: str, email: str, name: str) -> str:
        """Crea un cliente en Stripe"""
        try:
            customer = stripe.Customer.create(
                email=email, name=name, metadata={"user_id": user_profile_id}
            )
            return customer.id
        except Exception as e:
            raise CustomerCreationError(f"Error creando cliente: {e}")

    def create_checkout_session(
        self,
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """Crea una sesión de checkout"""
        try:
            session_params = {
                "customer": customer_id,
                "payment_method_types": ["card"],
                "line_items": [{"price": price_id, "quantity": 1}],
                "mode": kwargs.get("mode", "subscription"),
                "success_url": success_url,
                "cancel_url": cancel_url,
                "allow_promotion_codes": kwargs.get("allow_promotion_codes", True),
                "billing_address_collection": "required",
                "customer_update": {"address": "auto", "name": "auto"},
            }

            if kwargs.get("trial_period_days"):
                session_params["subscription_data"] = {
                    "trial_period_days": kwargs["trial_period_days"]
                }

            session = stripe.checkout.Session.create(**session_params)
            return {"id": session.id, "url": session.url}
        except Exception as e:
            raise CheckoutSessionError(f"Error creando sesión de checkout: {e}")

    def create_billing_portal_session(
        self, customer_id: str, return_url: str
    ) -> Dict[str, Any]:
        """Crea una sesión del portal de facturación"""
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id, return_url=return_url
            )
            return {"url": session.url}
        except Exception as e:
            raise BillingPortalError(f"Error creando portal de facturación: {e}")

    def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Obtiene una suscripción de Stripe"""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return {
                "id": subscription["id"],
                "customer": subscription["customer"],
                "status": subscription["status"],
                "current_period_start": subscription["current_period_start"],
                "current_period_end": subscription["current_period_end"],
                "trial_start": subscription.get("trial_start"),
                "trial_end": subscription.get("trial_end"),
                "canceled_at": subscription.get("canceled_at"),
                "ended_at": subscription.get("ended_at"),
                "items": [
                    {"price_id": item["price"]["id"], "quantity": item["quantity"]}
                    for item in subscription["items"]["data"]
                ],
            }
        except Exception as e:
            raise SubscriptionError(f"Error obteniendo suscripción: {e}")

    def cancel_subscription(self, subscription_id: str) -> Dict[str, Any] | None:
        """Cancela una suscripción en Stripe"""
        try:
            subscription = stripe.Subscription.modify(
                subscription_id, cancel_at_period_end=True
            )
            return {
                "id": subscription.id,
                "status": subscription.status,
                "canceled_at": subscription.canceled_at,
                "cancel_at_period_end": subscription.cancel_at_period_end,
            }
        except Exception as e:
            raise SubscriptionError(f"Error cancelando suscripción: {e}")

    def get_upcoming_invoice(self, customer_id: str) -> Dict[str, Any] | None:
        """Obtiene la próxima factura de un cliente"""
        try:
            invoices = stripe.Invoice.list(customer=customer_id, limit=1, status="open")
            invoice = invoices.data[0] if invoices.data else None
            if not invoice:
                return None
            return {
                "id": invoice.id,
                "amount_due": invoice.amount_due,
                "currency": invoice.currency,
                "period_start": invoice.period_start,
                "period_end": invoice.period_end,
                "due_date": invoice.due_date,
                "status": invoice.status,
            }
        except Exception as e:
            raise InvoiceError(f"Error obteniendo próxima factura: {e}")

    def get_payment_methods(self, customer_id: str) -> List[Dict[str, Any]]:
        """Obtiene los métodos de pago de un cliente"""
        try:
            payment_methods = stripe.PaymentMethod.list(
                customer=customer_id, type="card"
            )
            return [
                {
                    "id": pm.id,
                    "type": pm.type,
                    "card": (
                        {
                            "brand": pm.card.brand,
                            "last4": pm.card.last4,
                            "exp_month": pm.card.exp_month,
                            "exp_year": pm.card.exp_year,
                        }
                        if pm.card
                        else None
                    ),
                    "created": pm.created,
                }
                for pm in payment_methods.data
            ]
        except Exception as e:
            raise PaymentMethodError(f"Error obteniendo métodos de pago: {e}")

    def construct_webhook_event(self, payload: bytes, signature: str) -> Dict[str, Any]:
        """Construye un evento de webhook desde el payload"""
        try:
            return stripe.Webhook.construct_event(
                payload, signature, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            raise WebhookError(f"Payload inválido: {e}")
        except Exception as e:
            raise WebhookError(f"Firma de webhook inválida: {e}")

    def get_customer(self, customer_id: str) -> Dict[str, Any]:
        """Obtiene información de un cliente"""
        try:
            customer = stripe.Customer.retrieve(customer_id)
            return {
                "id": customer.id,
                "email": customer.email,
                "name": customer.name,
                "created": customer.created,
                "metadata": customer.metadata,
            }
        except Exception as e:
            raise CustomerCreationError(f"Error obteniendo cliente: {e}")

    def create_payment_intent(
        self, amount: int, currency: str, customer_id: str, **kwargs
    ) -> Dict[str, Any]:
        """Crea un Payment Intent"""
        try:
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                customer=customer_id,
                automatic_payment_methods={"enabled": True},
                **kwargs,
            )
            return {
                "id": intent.id,
                "client_secret": intent.client_secret,
                "status": intent.status,
            }
        except Exception as e:
            raise PaymentMethodError(f"Error creando Payment Intent: {e}")

    def get_invoice_history(
        self, customer_id: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Obtiene el historial de facturas de un cliente"""
        try:
            invoices = stripe.Invoice.list(customer=customer_id, limit=limit)
            return [
                {
                    "id": invoice.id,
                    "amount_paid": invoice.amount_paid,
                    "amount_due": invoice.amount_due,
                    "currency": invoice.currency,
                    "status": invoice.status,
                    "created": invoice.created,
                    "due_date": invoice.due_date,
                    "paid": invoice.status == "paid",
                    "invoice_pdf": invoice.invoice_pdf,
                }
                for invoice in invoices.data
            ]
        except Exception as e:
            raise InvoiceError(f"Error obteniendo historial de facturas: {e}")

    def get_price(self, price_id: str) -> Dict[str, Any]:
        """Obtiene información de un precio"""
        try:
            price = stripe.Price.retrieve(price_id)
            return {
                "id": price.id,
                "product": price.product,
                "unit_amount": price.unit_amount,
                "currency": price.currency,
                "recurring": (
                    {
                        "interval": price.recurring.interval,
                        "interval_count": price.recurring.interval_count,
                    }
                    if price.recurring
                    else None
                ),
                "active": price.active,
            }
        except Exception as e:
            raise StripeServiceError(f"Error obteniendo precio: {e}")

    def get_product(self, product_id: str) -> Dict[str, Any]:
        """Obtiene información de un producto"""
        try:
            product = stripe.Product.retrieve(product_id)
            return {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "active": product.active,
                "metadata": product.metadata,
            }
        except Exception as e:
            raise StripeServiceError(f"Error obteniendo producto: {e}")
