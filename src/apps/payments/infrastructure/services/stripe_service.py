"""
Stripe service implementation
"""
try:
    import stripe
except ImportError:
    stripe = None

from typing import Dict, Any, List
from django.conf import settings

from ...domain.interfaces import IStripeService
from ...domain.exceptions import (
    CustomerCreationError,
    CheckoutSessionError,
    BillingPortalError,
    SubscriptionError,
    PaymentMethodError,
    WebhookError,
    InvoiceError,
    StripeServiceError
)


class StripeService(IStripeService):
    """Implementación del servicio de Stripe"""

    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.api_version = "2023-10-16"

    async def create_customer(self, user_id: str, email: str, name: str) -> str:
        """Crea un cliente en Stripe"""
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata={"user_id": user_id}
            )
            return customer.id
        except stripe.error.StripeError as e:
            raise CustomerCreationError(f"Error creando cliente: {e}")

    async def create_checkout_session(
        self,
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Crea una sesión de checkout"""
        try:
            session_params = {
                "customer": customer_id,
                "payment_method_types": ["card"],
                "line_items": [{
                    "price": price_id,
                    "quantity": 1,
                }],
                "mode": kwargs.get("mode", "subscription"),
                "success_url": success_url,
                "cancel_url": cancel_url,
                "allow_promotion_codes": kwargs.get("allow_promotion_codes", True),
                "billing_address_collection": "required",
                "customer_update": {
                    "address": "auto",
                    "name": "auto"
                }
            }

            # Si es un cambio de suscripción
            if "subscription" in kwargs:
                session_params["subscription_data"] = {
                    "items": kwargs.get("items", [])
                }

            # Si es una nueva suscripción con trial
            if kwargs.get("trial_period_days"):
                session_params["subscription_data"] = {
                    "trial_period_days": kwargs["trial_period_days"]
                }

            session = stripe.checkout.Session.create(**session_params)
            return {
                "id": session.id,
                "url": session.url
            }

        except stripe.error.StripeError as e:
            raise CheckoutSessionError(f"Error creando sesión de checkout: {e}")

    async def create_billing_portal_session(
        self,
        customer_id: str,
        return_url: str
    ) -> Dict[str, Any]:
        """Crea una sesión del portal de facturación"""
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )
            return {
                "url": session.url
            }
        except stripe.error.StripeError as e:
            raise BillingPortalError(f"Error creando portal de facturación: {e}")

    async def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Obtiene una suscripción de Stripe"""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return {
                "id": subscription.id,
                "customer": subscription.customer,
                "status": subscription.status,
                "current_period_start": subscription.current_period_start,
                "current_period_end": subscription.current_period_end,
                "trial_start": subscription.trial_start,
                "trial_end": subscription.trial_end,
                "canceled_at": subscription.canceled_at,
                "ended_at": subscription.ended_at,
                "items": [
                    {
                        "price_id": item.price.id,
                        "quantity": item.quantity
                    }
                    for item in subscription.items.data
                ]
            }
        except stripe.error.StripeError as e:
            raise SubscriptionError(f"Error obteniendo suscripción: {e}")

    async def cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Cancela una suscripción en Stripe"""
        try:
            # Cancelar al final del período actual
            subscription = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
            return {
                "id": subscription.id,
                "status": subscription.status,
                "canceled_at": subscription.canceled_at,
                "cancel_at_period_end": subscription.cancel_at_period_end
            }
        except stripe.error.StripeError as e:
            raise SubscriptionError(f"Error cancelando suscripción: {e}")

    async def get_upcoming_invoice(self, customer_id: str) -> Dict[str, Any]:
        """Obtiene la próxima factura de un cliente"""
        try:
            invoice = stripe.Invoice.upcoming(customer=customer_id)
            return {
                "id": invoice.id,
                "amount_due": invoice.amount_due,
                "currency": invoice.currency,
                "period_start": invoice.period_start,
                "period_end": invoice.period_end,
                "due_date": invoice.due_date,
                "status": invoice.status
            }
        except stripe.error.StripeError:
            # Es normal que no haya próxima factura
            return None

    async def get_payment_methods(self, customer_id: str) -> List[Dict[str, Any]]:
        """Obtiene los métodos de pago de un cliente"""
        try:
            payment_methods = stripe.PaymentMethod.list(
                customer=customer_id,
                type="card"
            )
            
            return [
                {
                    "id": pm.id,
                    "type": pm.type,
                    "card": {
                        "brand": pm.card.brand,
                        "last4": pm.card.last4,
                        "exp_month": pm.card.exp_month,
                        "exp_year": pm.card.exp_year
                    } if pm.card else None,
                    "created": pm.created
                }
                for pm in payment_methods.data
            ]
        except stripe.error.StripeError as e:
            raise PaymentMethodError(f"Error obteniendo métodos de pago: {e}")

    def construct_webhook_event(self, payload: bytes, signature: str) -> Dict[str, Any]:
        """Construye un evento de webhook desde el payload"""
        try:
            event = stripe.Webhook.construct_event(
                payload,
                signature,
                settings.STRIPE_WEBHOOK_SECRET
            )
            return event
        except ValueError as e:
            raise WebhookError(f"Payload inválido: {e}")
        except stripe.error.SignatureVerificationError as e:
            raise WebhookError(f"Firma de webhook inválida: {e}")

    async def get_customer(self, customer_id: str) -> Dict[str, Any]:
        """Obtiene información de un cliente"""
        try:
            customer = stripe.Customer.retrieve(customer_id)
            return {
                "id": customer.id,
                "email": customer.email,
                "name": customer.name,
                "created": customer.created,
                "metadata": customer.metadata
            }
        except stripe.error.StripeError as e:
            raise CustomerCreationError(f"Error obteniendo cliente: {e}")

    async def create_payment_intent(
        self,
        amount: int,
        currency: str,
        customer_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Crea un Payment Intent"""
        try:
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                customer=customer_id,
                automatic_payment_methods={"enabled": True},
                **kwargs
            )
            return {
                "id": intent.id,
                "client_secret": intent.client_secret,
                "status": intent.status
            }
        except stripe.error.StripeError as e:
            raise PaymentMethodError(f"Error creando Payment Intent: {e}")

    async def get_invoice_history(
        self,
        customer_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Obtiene el historial de facturas de un cliente"""
        try:
            invoices = stripe.Invoice.list(
                customer=customer_id,
                limit=limit
            )
            
            return [
                {
                    "id": invoice.id,
                    "amount_paid": invoice.amount_paid,
                    "amount_due": invoice.amount_due,
                    "currency": invoice.currency,
                    "status": invoice.status,
                    "created": invoice.created,
                    "due_date": invoice.due_date,
                    "paid": invoice.paid,
                    "invoice_pdf": invoice.invoice_pdf
                }
                for invoice in invoices.data
            ]
        except stripe.error.StripeError as e:
            raise InvoiceError(f"Error obteniendo historial de facturas: {e}")

    async def get_price(self, price_id: str) -> Dict[str, Any]:
        """Obtiene información de un precio"""
        try:
            price = stripe.Price.retrieve(price_id)
            return {
                "id": price.id,
                "product": price.product,
                "unit_amount": price.unit_amount,
                "currency": price.currency,
                "recurring": {
                    "interval": price.recurring.interval,
                    "interval_count": price.recurring.interval_count
                } if price.recurring else None,
                "active": price.active
            }
        except stripe.error.StripeError as e:
            raise StripeServiceError(f"Error obteniendo precio: {e}")

    async def get_product(self, product_id: str) -> Dict[str, Any]:
        """Obtiene información de un producto"""
        try:
            product = stripe.Product.retrieve(product_id)
            return {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "active": product.active,
                "metadata": product.metadata
            }
        except stripe.error.StripeError as e:
            raise StripeServiceError(f"Error obteniendo producto: {e}")
