"""
Repository implementations for payments
"""
from typing import List, Optional
from django.contrib.auth import get_user_model
from django.utils import timezone

from ..domain.interfaces import (
    ISubscriptionPlanRepository,
    ISubscriptionRepository,
    IPaymentMethodRepository,
    IInvoiceRepository,
    IPaymentRepository,
    IStripeWebhookRepository
)
from ..domain.entities import (
    SubscriptionPlan as SubscriptionPlanEntity,
    Subscription as SubscriptionEntity,
    PaymentMethod as PaymentMethodEntity,
    Invoice as InvoiceEntity,
    Payment as PaymentEntity,
    StripeWebhookEvent as StripeWebhookEventEntity,
    SubscriptionStatus,
    PaymentStatus,
    InvoiceStatus
)
from .models import (
    SubscriptionPlan,
    Subscription,
    PaymentMethod,
    Invoice,
    Payment,
    StripeWebhookEvent
)

User = get_user_model()


class SubscriptionPlanRepository(ISubscriptionPlanRepository):
    """Implementación del repositorio de planes de suscripción"""

    async def get_all_active(self) -> List[SubscriptionPlanEntity]:
        """Obtiene todos los planes activos"""
        plans = SubscriptionPlan.objects.filter(is_active=True)
        return [self._to_entity(plan) for plan in plans]

    async def get_by_id(self, plan_id: str) -> Optional[SubscriptionPlanEntity]:
        """Obtiene un plan por ID"""
        try:
            plan = SubscriptionPlan.objects.get(id=plan_id)
            return self._to_entity(plan)
        except SubscriptionPlan.DoesNotExist:
            return None

    async def get_by_stripe_price_id(self, stripe_price_id: str) -> Optional[SubscriptionPlanEntity]:
        """Obtiene un plan por el price ID de Stripe"""
        try:
            plan = SubscriptionPlan.objects.get(stripe_price_id=stripe_price_id)
            return self._to_entity(plan)
        except SubscriptionPlan.DoesNotExist:
            return None

    async def create(self, plan: SubscriptionPlanEntity) -> SubscriptionPlanEntity:
        """Crea un nuevo plan"""
        model = SubscriptionPlan.objects.create(
            name=plan.name,
            description=plan.description,
            price=plan.price,
            currency=plan.currency,
            interval=plan.interval,
            interval_count=plan.interval_count,
            features=plan.features,
            stripe_price_id=plan.stripe_price_id,
            is_active=plan.is_active
        )
        return self._to_entity(model)

    async def update(self, plan: SubscriptionPlanEntity) -> SubscriptionPlanEntity:
        """Actualiza un plan existente"""
        model = SubscriptionPlan.objects.get(id=plan.id)
        model.name = plan.name
        model.description = plan.description
        model.price = plan.price
        model.currency = plan.currency
        model.interval = plan.interval
        model.interval_count = plan.interval_count
        model.features = plan.features
        model.stripe_price_id = plan.stripe_price_id
        model.is_active = plan.is_active
        model.save()
        return self._to_entity(model)

    def _to_entity(self, model: SubscriptionPlan) -> SubscriptionPlanEntity:
        """Convierte el modelo a entidad"""
        return SubscriptionPlanEntity(
            id=str(model.id),
            name=model.name,
            description=model.description,
            price=model.price,
            currency=model.currency,
            interval=model.interval,
            interval_count=model.interval_count,
            features=model.features,
            stripe_price_id=model.stripe_price_id,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at
        )


class SubscriptionRepository(ISubscriptionRepository):
    """Implementación del repositorio de suscripciones"""

    async def get_by_user_id(self, user_id: str) -> Optional[SubscriptionEntity]:
        """Obtiene la suscripción activa de un usuario"""
        try:
            subscription = Subscription.objects.select_related('user', 'plan').get(
                user_id=user_id,
                status__in=['active', 'trialing']
            )
            return self._to_entity(subscription)
        except Subscription.DoesNotExist:
            return None

    async def get_by_stripe_subscription_id(self, stripe_subscription_id: str) -> Optional[SubscriptionEntity]:
        """Obtiene una suscripción por su ID de Stripe"""
        try:
            subscription = Subscription.objects.select_related('user', 'plan').get(
                stripe_subscription_id=stripe_subscription_id
            )
            return self._to_entity(subscription)
        except Subscription.DoesNotExist:
            return None

    async def create(self, subscription: SubscriptionEntity) -> SubscriptionEntity:
        """Crea una nueva suscripción"""
        user = User.objects.get(id=subscription.user_id)
        plan = SubscriptionPlan.objects.get(id=subscription.plan_id)
        
        model = Subscription.objects.create(
            user=user,
            plan=plan,
            stripe_subscription_id=subscription.stripe_subscription_id,
            stripe_customer_id=subscription.stripe_customer_id,
            status=subscription.status.value,
            current_period_start=subscription.current_period_start,
            current_period_end=subscription.current_period_end,
            trial_start=subscription.trial_start,
            trial_end=subscription.trial_end,
            canceled_at=subscription.canceled_at,
            ended_at=subscription.ended_at
        )
        return self._to_entity(model)

    async def update(self, subscription: SubscriptionEntity) -> SubscriptionEntity:
        """Actualiza una suscripción existente"""
        model = Subscription.objects.get(id=subscription.id)
        model.status = subscription.status.value
        model.current_period_start = subscription.current_period_start
        model.current_period_end = subscription.current_period_end
        model.trial_start = subscription.trial_start
        model.trial_end = subscription.trial_end
        model.canceled_at = subscription.canceled_at
        model.ended_at = subscription.ended_at
        model.save()
        return self._to_entity(model)

    async def cancel(self, subscription_id: str) -> bool:
        """Cancela una suscripción"""
        try:
            model = Subscription.objects.get(id=subscription_id)
            model.canceled_at = timezone.now()
            model.status = 'canceled'
            model.save()
            return True
        except Subscription.DoesNotExist:
            return False

    def _to_entity(self, model: Subscription) -> SubscriptionEntity:
        """Convierte el modelo a entidad"""
        return SubscriptionEntity(
            id=str(model.id),
            user_id=str(model.user.id),
            stripe_subscription_id=model.stripe_subscription_id,
            stripe_customer_id=model.stripe_customer_id,
            plan_id=str(model.plan.id),
            status=SubscriptionStatus(model.status),
            current_period_start=model.current_period_start,
            current_period_end=model.current_period_end,
            trial_start=model.trial_start,
            trial_end=model.trial_end,
            canceled_at=model.canceled_at,
            ended_at=model.ended_at,
            created_at=model.created_at,
            updated_at=model.updated_at
        )


class PaymentMethodRepository(IPaymentMethodRepository):
    """Implementación del repositorio de métodos de pago"""

    async def get_by_user_id(self, user_id: str) -> List[PaymentMethodEntity]:
        """Obtiene todos los métodos de pago de un usuario"""
        payment_methods = PaymentMethod.objects.filter(user_id=user_id)
        return [self._to_entity(pm) for pm in payment_methods]

    async def get_default_by_user_id(self, user_id: str) -> Optional[PaymentMethodEntity]:
        """Obtiene el método de pago por defecto de un usuario"""
        try:
            payment_method = PaymentMethod.objects.get(user_id=user_id, is_default=True)
            return self._to_entity(payment_method)
        except PaymentMethod.DoesNotExist:
            return None

    async def create(self, payment_method: PaymentMethodEntity) -> PaymentMethodEntity:
        """Crea un nuevo método de pago"""
        user = User.objects.get(id=payment_method.user_id)
        
        model = PaymentMethod.objects.create(
            user=user,
            stripe_payment_method_id=payment_method.stripe_payment_method_id,
            type=payment_method.type,
            card_brand=payment_method.card_brand or "",
            card_last4=payment_method.card_last4 or "",
            card_exp_month=payment_method.card_exp_month,
            card_exp_year=payment_method.card_exp_year,
            is_default=payment_method.is_default
        )
        return self._to_entity(model)

    async def update(self, payment_method: PaymentMethodEntity) -> PaymentMethodEntity:
        """Actualiza un método de pago"""
        model = PaymentMethod.objects.get(id=payment_method.id)
        model.is_default = payment_method.is_default
        model.save()
        return self._to_entity(model)

    async def delete(self, payment_method_id: str) -> bool:
        """Elimina un método de pago"""
        try:
            PaymentMethod.objects.get(id=payment_method_id).delete()
            return True
        except PaymentMethod.DoesNotExist:
            return False

    def _to_entity(self, model: PaymentMethod) -> PaymentMethodEntity:
        """Convierte el modelo a entidad"""
        return PaymentMethodEntity(
            id=str(model.id),
            stripe_payment_method_id=model.stripe_payment_method_id,
            user_id=str(model.user.id),
            type=model.type,
            card_brand=model.card_brand if model.card_brand else None,
            card_last4=model.card_last4 if model.card_last4 else None,
            card_exp_month=model.card_exp_month,
            card_exp_year=model.card_exp_year,
            is_default=model.is_default,
            created_at=model.created_at
        )


class InvoiceRepository(IInvoiceRepository):
    """Implementación del repositorio de facturas"""

    async def get_by_user_id(self, user_id: str, limit: int = 10) -> List[InvoiceEntity]:
        """Obtiene las facturas de un usuario"""
        invoices = Invoice.objects.filter(user_id=user_id)[:limit]
        return [self._to_entity(invoice) for invoice in invoices]

    async def get_by_stripe_invoice_id(self, stripe_invoice_id: str) -> Optional[InvoiceEntity]:
        """Obtiene una factura por su ID de Stripe"""
        try:
            invoice = Invoice.objects.get(stripe_invoice_id=stripe_invoice_id)
            return self._to_entity(invoice)
        except Invoice.DoesNotExist:
            return None

    async def create(self, invoice: InvoiceEntity) -> InvoiceEntity:
        """Crea una nueva factura"""
        user = User.objects.get(id=invoice.user_id)
        subscription = None
        if invoice.subscription_id:
            subscription = Subscription.objects.get(id=invoice.subscription_id)
        
        model = Invoice.objects.create(
            user=user,
            subscription=subscription,
            stripe_invoice_id=invoice.stripe_invoice_id,
            amount=invoice.amount,
            currency=invoice.currency,
            status=invoice.status.value,
            due_date=invoice.due_date,
            paid_at=invoice.paid_at
        )
        return self._to_entity(model)

    async def update(self, invoice: InvoiceEntity) -> InvoiceEntity:
        """Actualiza una factura"""
        model = Invoice.objects.get(id=invoice.id)
        model.status = invoice.status.value
        model.paid_at = invoice.paid_at
        model.save()
        return self._to_entity(model)

    def _to_entity(self, model: Invoice) -> InvoiceEntity:
        """Convierte el modelo a entidad"""
        return InvoiceEntity(
            id=str(model.id),
            stripe_invoice_id=model.stripe_invoice_id,
            subscription_id=str(model.subscription.id) if model.subscription else "",
            user_id=str(model.user.id),
            amount=model.amount,
            currency=model.currency,
            status=InvoiceStatus(model.status),
            due_date=model.due_date,
            paid_at=model.paid_at,
            created_at=model.created_at
        )


class PaymentRepository(IPaymentRepository):
    """Implementación del repositorio de pagos"""

    async def get_by_user_id(self, user_id: str, limit: int = 10) -> List[PaymentEntity]:
        """Obtiene los pagos de un usuario"""
        payments = Payment.objects.filter(user_id=user_id)[:limit]
        return [self._to_entity(payment) for payment in payments]

    async def get_by_stripe_payment_intent_id(self, stripe_payment_intent_id: str) -> Optional[PaymentEntity]:
        """Obtiene un pago por su Payment Intent ID de Stripe"""
        try:
            payment = Payment.objects.get(stripe_payment_intent_id=stripe_payment_intent_id)
            return self._to_entity(payment)
        except Payment.DoesNotExist:
            return None

    async def create(self, payment: PaymentEntity) -> PaymentEntity:
        """Crea un nuevo pago"""
        user = User.objects.get(id=payment.user_id)
        invoice = None
        if payment.invoice_id:
            invoice = Invoice.objects.get(id=payment.invoice_id)
        
        payment_method = None
        if payment.payment_method_id:
            payment_method = PaymentMethod.objects.get(id=payment.payment_method_id)
        
        model = Payment.objects.create(
            user=user,
            stripe_payment_intent_id=payment.stripe_payment_intent_id,
            invoice=invoice,
            payment_method=payment_method,
            amount=payment.amount,
            currency=payment.currency,
            status=payment.status.value,
            metadata=payment.metadata
        )
        return self._to_entity(model)

    async def update(self, payment: PaymentEntity) -> PaymentEntity:
        """Actualiza un pago"""
        model = Payment.objects.get(id=payment.id)
        model.status = payment.status.value
        model.metadata = payment.metadata
        model.save()
        return self._to_entity(model)

    def _to_entity(self, model: Payment) -> PaymentEntity:
        """Convierte el modelo a entidad"""
        return PaymentEntity(
            id=str(model.id),
            stripe_payment_intent_id=model.stripe_payment_intent_id,
            user_id=str(model.user.id),
            amount=model.amount,
            currency=model.currency,
            status=PaymentStatus(model.status),
            payment_method_id=str(model.payment_method.id) if model.payment_method else None,
            invoice_id=str(model.invoice.id) if model.invoice else None,
            metadata=model.metadata,
            created_at=model.created_at
        )


class StripeWebhookRepository(IStripeWebhookRepository):
    """Implementación del repositorio de webhooks de Stripe"""

    async def get_by_stripe_event_id(self, stripe_event_id: str) -> Optional[StripeWebhookEventEntity]:
        """Obtiene un evento por su ID de Stripe"""
        try:
            event = StripeWebhookEvent.objects.get(stripe_event_id=stripe_event_id)
            return self._to_entity(event)
        except StripeWebhookEvent.DoesNotExist:
            return None

    async def create(self, webhook_event: StripeWebhookEventEntity) -> StripeWebhookEventEntity:
        """Crea un nuevo evento de webhook"""
        model = StripeWebhookEvent.objects.create(
            stripe_event_id=webhook_event.stripe_event_id,
            event_type=webhook_event.event_type,
            processed=webhook_event.processed,
            data=webhook_event.data
        )
        return self._to_entity(model)

    async def mark_as_processed(self, event_id: str) -> bool:
        """Marca un evento como procesado"""
        try:
            model = StripeWebhookEvent.objects.get(id=event_id)
            model.processed = True
            model.processed_at = timezone.now()
            model.save()
            return True
        except StripeWebhookEvent.DoesNotExist:
            return False

    def _to_entity(self, model: StripeWebhookEvent) -> StripeWebhookEventEntity:
        """Convierte el modelo a entidad"""
        return StripeWebhookEventEntity(
            id=str(model.id),
            stripe_event_id=model.stripe_event_id,
            event_type=model.event_type,
            processed=model.processed,
            data=model.data,
            created_at=model.created_at,
            processed_at=model.processed_at
        )
