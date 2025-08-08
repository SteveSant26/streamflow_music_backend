"""
Tests para las entidades del dominio de payments
"""

import pytest
from datetime import datetime, timezone
from decimal import Decimal
from src.apps.payments.domain.entities import (
    PaymentEntity,
    SubscriptionEntity,
    SubscriptionPlanEntity,
    PaymentMethodEntity,
    InvoiceEntity
)
from src.apps.payments.domain.enums import (
    PaymentStatus,
    SubscriptionStatus,
    InvoiceStatus
)


class TestPaymentEntity:
    """Tests para la entidad PaymentEntity"""

    def test_payment_entity_creation_minimal(self):
        """Test creación de payment con datos mínimos"""
        payment = PaymentEntity(
            id="payment-1",
            stripe_payment_intent_id="pi_1234567890",
            user_id="user-123",
            amount=2999,  # $29.99 en centavos
            currency="usd",
            status=PaymentStatus.PENDING
        )
        
        assert payment.id == "payment-1"
        assert payment.stripe_payment_intent_id == "pi_1234567890"
        assert payment.user_id == "user-123"
        assert payment.amount == 2999
        assert payment.currency == "usd"
        assert payment.status == PaymentStatus.PENDING
        assert payment.payment_method_id is None
        assert payment.invoice_id is None
        assert payment.metadata == {}
        assert payment.created_at is None

    def test_payment_entity_creation_complete(self):
        """Test creación de payment con datos completos"""
        metadata = {"subscription_id": "sub-123", "plan": "premium"}
        created_time = datetime.now()
        
        payment = PaymentEntity(
            id="payment-1",
            stripe_payment_intent_id="pi_1234567890",
            user_id="user-123",
            amount=2999,
            currency="usd",
            status=PaymentStatus.SUCCEEDED,
            payment_method_id="pm_1234567890",
            invoice_id="in_1234567890",
            metadata=metadata,
            created_at=created_time
        )
        
        assert payment.payment_method_id == "pm_1234567890"
        assert payment.invoice_id == "in_1234567890"
        assert payment.metadata == metadata
        assert payment.created_at == created_time
        assert payment.status == PaymentStatus.SUCCEEDED

    def test_payment_entity_amount_validation(self):
        """Test diferentes montos de pago"""
        # Monto normal
        payment = PaymentEntity(
            id="payment-1",
            stripe_payment_intent_id="pi_1234567890",
            user_id="user-123",
            amount=999,  # $9.99
            currency="usd",
            status=PaymentStatus.PENDING
        )
        assert payment.amount == 999

        # Monto alto
        payment_high = PaymentEntity(
            id="payment-2",
            stripe_payment_intent_id="pi_0987654321",
            user_id="user-456",
            amount=9999999,  # $99,999.99
            currency="usd",
            status=PaymentStatus.PENDING
        )
        assert payment_high.amount == 9999999

    def test_payment_entity_different_currencies(self):
        """Test diferentes monedas"""
        currencies = ["usd", "eur", "gbp", "cad"]
        
        for i, currency in enumerate(currencies):
            payment = PaymentEntity(
                id=f"payment-{i}",
                stripe_payment_intent_id=f"pi_{i}",
                user_id="user-123",
                amount=1000,
                currency=currency,
                status=PaymentStatus.PENDING
            )
            assert payment.currency == currency

    def test_payment_entity_status_transitions(self):
        """Test diferentes estados de pago"""
        statuses = [
            PaymentStatus.PENDING,
            PaymentStatus.SUCCEEDED,
            PaymentStatus.FAILED,
            PaymentStatus.CANCELED
        ]
        
        for status in statuses:
            payment = PaymentEntity(
                id="payment-1",
                stripe_payment_intent_id="pi_1234567890",
                user_id="user-123",
                amount=2999,
                currency="usd",
                status=status
            )
            assert payment.status == status


class TestSubscriptionEntity:
    """Tests para la entidad SubscriptionEntity"""

    def test_subscription_entity_creation_minimal(self):
        """Test creación de subscription con datos mínimos"""
        start_date = datetime.now(timezone.utc)
        end_date = datetime.now(timezone.utc)
        
        subscription = SubscriptionEntity(
            id="sub-1",
            user_id="user-123",
            stripe_subscription_id="sub_1234567890",
            stripe_customer_id="cus_1234567890",
            plan_id="plan-premium",
            status=SubscriptionStatus.ACTIVE,
            current_period_start=start_date,
            current_period_end=end_date
        )
        
        assert subscription.id == "sub-1"
        assert subscription.user_id == "user-123"
        assert subscription.stripe_subscription_id == "sub_1234567890"
        assert subscription.stripe_customer_id == "cus_1234567890"
        assert subscription.plan_id == "plan-premium"
        assert subscription.status == SubscriptionStatus.ACTIVE
        assert subscription.current_period_start == start_date
        assert subscription.current_period_end == end_date
        assert subscription.trial_start is None
        assert subscription.trial_end is None
        assert subscription.canceled_at is None
        assert subscription.ended_at is None

    def test_subscription_entity_with_trial(self):
        """Test subscription con período de prueba"""
        now = datetime.now(timezone.utc)
        trial_start = now
        trial_end = datetime(2024, 12, 31, tzinfo=timezone.utc)
        
        subscription = SubscriptionEntity(
            id="sub-1",
            user_id="user-123",
            stripe_subscription_id="sub_1234567890",
            stripe_customer_id="cus_1234567890",
            plan_id="plan-premium",
            status=SubscriptionStatus.TRIALING,
            current_period_start=now,
            current_period_end=trial_end,
            trial_start=trial_start,
            trial_end=trial_end
        )
        
        assert subscription.trial_start == trial_start
        assert subscription.trial_end == trial_end
        assert subscription.status == SubscriptionStatus.TRIALING

    def test_subscription_entity_is_active_property(self):
        """Test propiedad is_active"""
        # Subscription activa
        active_subscription = SubscriptionEntity(
            id="sub-1",
            user_id="user-123",
            stripe_subscription_id="sub_1234567890",
            stripe_customer_id="cus_1234567890",
            plan_id="plan-premium",
            status=SubscriptionStatus.ACTIVE,
            current_period_start=datetime.now(timezone.utc),
            current_period_end=datetime.now(timezone.utc)
        )
        assert active_subscription.is_active is True

        # Subscription cancelada
        canceled_subscription = SubscriptionEntity(
            id="sub-2",
            user_id="user-123",
            stripe_subscription_id="sub_0987654321",
            stripe_customer_id="cus_1234567890",
            plan_id="plan-premium",
            status=SubscriptionStatus.CANCELED,
            current_period_start=datetime.now(timezone.utc),
            current_period_end=datetime.now(timezone.utc)
        )
        assert canceled_subscription.is_active is False

    def test_subscription_entity_is_on_trial_property(self):
        """Test propiedad is_on_trial"""
        now = datetime.now(timezone.utc)
        
        # Sin trial
        no_trial_subscription = SubscriptionEntity(
            id="sub-1",
            user_id="user-123",
            stripe_subscription_id="sub_1234567890",
            stripe_customer_id="cus_1234567890",
            plan_id="plan-premium",
            status=SubscriptionStatus.ACTIVE,
            current_period_start=now,
            current_period_end=now
        )
        assert no_trial_subscription.is_on_trial is False

        # Trial expirado (fecha pasada)
        expired_trial = SubscriptionEntity(
            id="sub-2",
            user_id="user-123",
            stripe_subscription_id="sub_0987654321",
            stripe_customer_id="cus_1234567890",
            plan_id="plan-premium",
            status=SubscriptionStatus.ACTIVE,
            current_period_start=now,
            current_period_end=now,
            trial_end=datetime(2020, 1, 1, tzinfo=timezone.utc)  # Fecha pasada
        )
        assert expired_trial.is_on_trial is False

        # Trial activo (fecha futura)
        active_trial = SubscriptionEntity(
            id="sub-3",
            user_id="user-123",
            stripe_subscription_id="sub_1111111111",
            stripe_customer_id="cus_1234567890",
            plan_id="plan-premium",
            status=SubscriptionStatus.TRIALING,
            current_period_start=now,
            current_period_end=now,
            trial_end=datetime(2030, 12, 31, tzinfo=timezone.utc)  # Fecha futura
        )
        assert active_trial.is_on_trial is True

    def test_subscription_entity_cancellation(self):
        """Test subscription cancelada"""
        now = datetime.now(timezone.utc)
        canceled_time = now
        
        subscription = SubscriptionEntity(
            id="sub-1",
            user_id="user-123",
            stripe_subscription_id="sub_1234567890",
            stripe_customer_id="cus_1234567890",
            plan_id="plan-premium",
            status=SubscriptionStatus.CANCELED,
            current_period_start=now,
            current_period_end=now,
            canceled_at=canceled_time
        )
        
        assert subscription.status == SubscriptionStatus.CANCELED
        assert subscription.canceled_at == canceled_time
        assert subscription.is_active is False

    def test_subscription_entity_different_statuses(self):
        """Test diferentes estados de subscription"""
        now = datetime.now(timezone.utc)
        statuses = [
            SubscriptionStatus.ACTIVE,
            SubscriptionStatus.TRIALING,
            SubscriptionStatus.CANCELED,
            SubscriptionStatus.PAST_DUE,
            SubscriptionStatus.UNPAID,
            SubscriptionStatus.INCOMPLETE,
            SubscriptionStatus.INCOMPLETE_EXPIRED
        ]
        
        for status in statuses:
            subscription = SubscriptionEntity(
                id="sub-1",
                user_id="user-123",
                stripe_subscription_id="sub_1234567890",
                stripe_customer_id="cus_1234567890",
                plan_id="plan-premium",
                status=status,
                current_period_start=now,
                current_period_end=now
            )
            assert subscription.status == status
