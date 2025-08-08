"""
Tests comprehensivos para Payment DTOs
Objetivo: Maximizar cobertura probando todos los DTOs de payments
"""

import pytest
from datetime import datetime
from src.apps.payments.api.dtos.payment_dtos import (
    PaymentResponseDTO,
    CreatePaymentRequestDTO,
    SubscriptionResponseDTO,
    CreateSubscriptionRequestDTO,
    SubscriptionPlanResponseDTO,
    InvoiceResponseDTO,
    PaymentMethodResponseDTO,
    CreatePaymentMethodRequestDTO,
    StripeWebhookEventResponseDTO,
)


class TestPaymentResponseDTO:
    """Tests para PaymentResponseDTO"""

    def test_payment_response_dto_creation_full(self):
        """Test creation with all fields"""
        dto = PaymentResponseDTO(
            id="payment_123",
            user_id="user_456",
            stripe_payment_intent_id="pi_123456789",
            amount=2000,
            currency="usd",
            status="succeeded",
            payment_method_id="pm_987654321",
            invoice_id="inv_111222333",
            created_at=datetime(2024, 1, 15, 10, 30, 0)
        )
        
        assert dto.id == "payment_123"
        assert dto.user_id == "user_456"
        assert dto.stripe_payment_intent_id == "pi_123456789"
        assert dto.amount == 2000
        assert dto.currency == "usd"
        assert dto.status == "succeeded"
        assert dto.payment_method_id == "pm_987654321"
        assert dto.invoice_id == "inv_111222333"
        assert dto.created_at == datetime(2024, 1, 15, 10, 30, 0)

    def test_payment_response_dto_creation_minimal(self):
        """Test creation with only required fields"""
        dto = PaymentResponseDTO(
            id="payment_123",
            user_id="user_456",
            stripe_payment_intent_id="pi_123456789",
            amount=2000,
            currency="usd",
            status="pending"
        )
        
        assert dto.id == "payment_123"
        assert dto.user_id == "user_456"
        assert dto.stripe_payment_intent_id == "pi_123456789"
        assert dto.amount == 2000
        assert dto.currency == "usd"
        assert dto.status == "pending"
        assert dto.payment_method_id is None
        assert dto.invoice_id is None
        assert dto.created_at is None

    def test_payment_response_dto_equality(self):
        """Test equality comparison"""
        dto1 = PaymentResponseDTO(
            id="payment_123",
            user_id="user_456",
            stripe_payment_intent_id="pi_123456789",
            amount=2000,
            currency="usd",
            status="succeeded"
        )
        dto2 = PaymentResponseDTO(
            id="payment_123",
            user_id="user_456",
            stripe_payment_intent_id="pi_123456789",
            amount=2000,
            currency="usd",
            status="succeeded"
        )
        
        assert dto1 == dto2


class TestCreatePaymentRequestDTO:
    """Tests para CreatePaymentRequestDTO"""

    def test_create_payment_request_dto_full(self):
        """Test creation with all fields"""
        dto = CreatePaymentRequestDTO(
            user_id="user_456",
            amount=3000,
            currency="eur",
            payment_method_id="pm_123456789"
        )
        
        assert dto.user_id == "user_456"
        assert dto.amount == 3000
        assert dto.currency == "eur"
        assert dto.payment_method_id == "pm_123456789"

    def test_create_payment_request_dto_minimal(self):
        """Test creation with only required fields"""
        dto = CreatePaymentRequestDTO(
            user_id="user_789",
            amount=1500,
            currency="gbp"
        )
        
        assert dto.user_id == "user_789"
        assert dto.amount == 1500
        assert dto.currency == "gbp"
        assert dto.payment_method_id is None


class TestSubscriptionResponseDTO:
    """Tests para SubscriptionResponseDTO"""

    def test_subscription_response_dto_creation_full(self):
        """Test creation with all fields"""
        start_date = datetime(2024, 1, 1, 0, 0, 0)
        end_date = datetime(2024, 2, 1, 0, 0, 0)
        trial_start = datetime(2023, 12, 1, 0, 0, 0)
        trial_end = datetime(2023, 12, 31, 0, 0, 0)
        canceled_at = datetime(2024, 1, 15, 10, 30, 0)
        
        dto = SubscriptionResponseDTO(
            id="sub_123",
            user_id="user_456",
            plan_id="plan_789",
            stripe_subscription_id="sub_stripe_123",
            stripe_customer_id="cus_stripe_456",
            status="active",
            current_period_start=start_date,
            current_period_end=end_date,
            trial_start=trial_start,
            trial_end=trial_end,
            canceled_at=canceled_at,
            ended_at=None
        )
        
        assert dto.id == "sub_123"
        assert dto.user_id == "user_456"
        assert dto.plan_id == "plan_789"
        assert dto.stripe_subscription_id == "sub_stripe_123"
        assert dto.stripe_customer_id == "cus_stripe_456"
        assert dto.status == "active"
        assert dto.current_period_start == start_date
        assert dto.current_period_end == end_date
        assert dto.trial_start == trial_start
        assert dto.trial_end == trial_end
        assert dto.canceled_at == canceled_at
        assert dto.ended_at is None

    def test_subscription_response_dto_creation_minimal(self):
        """Test creation with only required fields"""
        start_date = datetime(2024, 1, 1, 0, 0, 0)
        end_date = datetime(2024, 2, 1, 0, 0, 0)
        
        dto = SubscriptionResponseDTO(
            id="sub_123",
            user_id="user_456",
            plan_id="plan_789",
            stripe_subscription_id="sub_stripe_123",
            stripe_customer_id="cus_stripe_456",
            status="trial",
            current_period_start=start_date,
            current_period_end=end_date
        )
        
        assert dto.id == "sub_123"
        assert dto.trial_start is None
        assert dto.trial_end is None
        assert dto.canceled_at is None
        assert dto.ended_at is None


class TestCreateSubscriptionRequestDTO:
    """Tests para CreateSubscriptionRequestDTO"""

    def test_create_subscription_request_dto_full(self):
        """Test creation with all fields"""
        dto = CreateSubscriptionRequestDTO(
            user_id="user_123",
            plan_id="plan_456",
            payment_method_id="pm_789"
        )
        
        assert dto.user_id == "user_123"
        assert dto.plan_id == "plan_456"
        assert dto.payment_method_id == "pm_789"

    def test_create_subscription_request_dto_minimal(self):
        """Test creation with only required fields"""
        dto = CreateSubscriptionRequestDTO(
            user_id="user_123",
            plan_id="plan_456"
        )
        
        assert dto.user_id == "user_123"
        assert dto.plan_id == "plan_456"
        assert dto.payment_method_id is None


class TestSubscriptionPlanResponseDTO:
    """Tests para SubscriptionPlanResponseDTO"""

    def test_subscription_plan_response_dto_creation_full(self):
        """Test creation with all fields"""
        created_at = datetime(2024, 1, 1, 10, 0, 0)
        updated_at = datetime(2024, 1, 15, 15, 30, 0)
        
        dto = SubscriptionPlanResponseDTO(
            id="plan_123",
            name="Premium Plan",
            description="Premium subscription with all features",
            price=999,
            currency="usd",
            interval="month",
            interval_count=1,
            features=["feature1", "feature2", "feature3"],
            stripe_price_id="price_123456789",
            is_active=True,
            created_at=created_at,
            updated_at=updated_at
        )
        
        assert dto.id == "plan_123"
        assert dto.name == "Premium Plan"
        assert dto.description == "Premium subscription with all features"
        assert dto.price == 999
        assert dto.currency == "usd"
        assert dto.interval == "month"
        assert dto.interval_count == 1
        assert dto.features == ["feature1", "feature2", "feature3"]
        assert dto.stripe_price_id == "price_123456789"
        assert dto.is_active is True
        assert dto.created_at == created_at
        assert dto.updated_at == updated_at

    def test_subscription_plan_response_dto_creation_minimal(self):
        """Test creation with only required fields"""
        dto = SubscriptionPlanResponseDTO(
            id="plan_123",
            name="Basic Plan",
            description="Basic subscription",
            price=499,
            currency="usd",
            interval="year",
            interval_count=1,
            features=["basic_feature"],
            stripe_price_id="price_987654321"
        )
        
        assert dto.id == "plan_123"
        assert dto.is_active is True  # default value
        assert dto.created_at is None
        assert dto.updated_at is None

    def test_subscription_plan_response_dto_inactive(self):
        """Test creation with inactive plan"""
        dto = SubscriptionPlanResponseDTO(
            id="plan_inactive",
            name="Old Plan",
            description="Deprecated plan",
            price=299,
            currency="usd",
            interval="month",
            interval_count=3,
            features=[],
            stripe_price_id="price_old",
            is_active=False
        )
        
        assert dto.is_active is False
        assert dto.features == []


class TestInvoiceResponseDTO:
    """Tests para InvoiceResponseDTO"""

    def test_invoice_response_dto_creation_full(self):
        """Test creation with all fields"""
        due_date = datetime(2024, 2, 1, 0, 0, 0)
        paid_at = datetime(2024, 1, 25, 14, 30, 0)
        created_at = datetime(2024, 1, 1, 10, 0, 0)
        
        dto = InvoiceResponseDTO(
            id="inv_123",
            stripe_invoice_id="in_stripe_123",
            subscription_id="sub_456",
            user_id="user_789",
            amount=2500,
            currency="eur",
            status="paid",
            due_date=due_date,
            paid_at=paid_at,
            created_at=created_at
        )
        
        assert dto.id == "inv_123"
        assert dto.stripe_invoice_id == "in_stripe_123"
        assert dto.subscription_id == "sub_456"
        assert dto.user_id == "user_789"
        assert dto.amount == 2500
        assert dto.currency == "eur"
        assert dto.status == "paid"
        assert dto.due_date == due_date
        assert dto.paid_at == paid_at
        assert dto.created_at == created_at

    def test_invoice_response_dto_creation_minimal(self):
        """Test creation with only required fields"""
        dto = InvoiceResponseDTO(
            id="inv_123",
            stripe_invoice_id="in_stripe_123",
            subscription_id="sub_456",
            user_id="user_789",
            amount=1000,
            currency="usd",
            status="open"
        )
        
        assert dto.id == "inv_123"
        assert dto.due_date is None
        assert dto.paid_at is None
        assert dto.created_at is None


class TestPaymentMethodResponseDTO:
    """Tests para PaymentMethodResponseDTO"""

    def test_payment_method_response_dto_creation_full(self):
        """Test creation with all fields"""
        created_at = datetime(2024, 1, 10, 9, 0, 0)
        
        dto = PaymentMethodResponseDTO(
            id="pm_123",
            user_id="user_456",
            stripe_payment_method_id="pm_stripe_789",
            type="card",
            card_brand="visa",
            card_last4="4242",
            card_exp_month=12,
            card_exp_year=2028,
            is_default=True,
            created_at=created_at
        )
        
        assert dto.id == "pm_123"
        assert dto.user_id == "user_456"
        assert dto.stripe_payment_method_id == "pm_stripe_789"
        assert dto.type == "card"
        assert dto.card_brand == "visa"
        assert dto.card_last4 == "4242"
        assert dto.card_exp_month == 12
        assert dto.card_exp_year == 2028
        assert dto.is_default is True
        assert dto.created_at == created_at

    def test_payment_method_response_dto_creation_minimal(self):
        """Test creation with only required fields"""
        dto = PaymentMethodResponseDTO(
            id="pm_123",
            user_id="user_456",
            stripe_payment_method_id="pm_stripe_789",
            type="bank_account"
        )
        
        assert dto.id == "pm_123"
        assert dto.card_brand is None
        assert dto.card_last4 is None
        assert dto.card_exp_month is None
        assert dto.card_exp_year is None
        assert dto.is_default is False  # default value
        assert dto.created_at is None


class TestCreatePaymentMethodRequestDTO:
    """Tests para CreatePaymentMethodRequestDTO"""

    def test_create_payment_method_request_dto_full(self):
        """Test creation with all fields"""
        dto = CreatePaymentMethodRequestDTO(
            user_id="user_123",
            stripe_payment_method_id="pm_stripe_456",
            type="card",
            card_brand="mastercard",
            card_last4="1234",
            card_exp_month=6,
            card_exp_year=2030
        )
        
        assert dto.user_id == "user_123"
        assert dto.stripe_payment_method_id == "pm_stripe_456"
        assert dto.type == "card"
        assert dto.card_brand == "mastercard"
        assert dto.card_last4 == "1234"
        assert dto.card_exp_month == 6
        assert dto.card_exp_year == 2030

    def test_create_payment_method_request_dto_minimal(self):
        """Test creation with only required fields"""
        dto = CreatePaymentMethodRequestDTO(
            user_id="user_123",
            stripe_payment_method_id="pm_stripe_456",
            type="sepa_debit"
        )
        
        assert dto.user_id == "user_123"
        assert dto.stripe_payment_method_id == "pm_stripe_456"
        assert dto.type == "sepa_debit"
        assert dto.card_brand is None
        assert dto.card_last4 is None
        assert dto.card_exp_month is None
        assert dto.card_exp_year is None


class TestStripeWebhookEventResponseDTO:
    """Tests para StripeWebhookEventResponseDTO"""

    def test_stripe_webhook_event_response_dto_creation_full(self):
        """Test creation with all fields"""
        created_at = datetime(2024, 1, 15, 14, 30, 0)
        processed_at = datetime(2024, 1, 15, 14, 31, 0)
        event_data = {
            "object": "payment_intent",
            "id": "pi_123456789",
            "amount": 2000,
            "currency": "usd",
            "status": "succeeded"
        }
        
        dto = StripeWebhookEventResponseDTO(
            id="event_123",
            stripe_event_id="evt_stripe_456",
            event_type="payment_intent.succeeded",
            processed=True,
            data=event_data,
            created_at=created_at,
            processed_at=processed_at
        )
        
        assert dto.id == "event_123"
        assert dto.stripe_event_id == "evt_stripe_456"
        assert dto.event_type == "payment_intent.succeeded"
        assert dto.processed is True
        assert dto.data == event_data
        assert dto.created_at == created_at
        assert dto.processed_at == processed_at

    def test_stripe_webhook_event_response_dto_creation_minimal(self):
        """Test creation with only required fields"""
        event_data = {"type": "invoice.payment_succeeded"}
        
        dto = StripeWebhookEventResponseDTO(
            id="event_123",
            stripe_event_id="evt_stripe_456",
            event_type="invoice.payment_succeeded",
            processed=False,
            data=event_data
        )
        
        assert dto.id == "event_123"
        assert dto.processed is False
        assert dto.data == event_data
        assert dto.created_at is None
        assert dto.processed_at is None

    def test_stripe_webhook_event_response_dto_complex_data(self):
        """Test with complex event data"""
        complex_data = {
            "object": "subscription",
            "id": "sub_123456789",
            "customer": "cus_987654321",
            "items": {
                "data": [
                    {
                        "id": "si_item_123",
                        "price": {
                            "id": "price_789",
                            "unit_amount": 999,
                            "currency": "usd"
                        }
                    }
                ]
            },
            "metadata": {
                "user_id": "user_123",
                "custom_field": "custom_value"
            }
        }
        
        dto = StripeWebhookEventResponseDTO(
            id="event_complex",
            stripe_event_id="evt_complex_123",
            event_type="customer.subscription.updated",
            processed=True,
            data=complex_data
        )
        
        assert dto.data["object"] == "subscription"
        assert dto.data["items"]["data"][0]["price"]["unit_amount"] == 999
        assert dto.data["metadata"]["user_id"] == "user_123"


class TestDTOsInteraction:
    """Tests de interacción entre DTOs"""

    def test_payment_and_subscription_workflow(self):
        """Test workflow combining payment and subscription DTOs"""
        # Create payment method
        payment_method = CreatePaymentMethodRequestDTO(
            user_id="user_workflow",
            stripe_payment_method_id="pm_workflow_123",
            type="card",
            card_brand="visa",
            card_last4="4242"
        )
        
        # Create subscription
        subscription_request = CreateSubscriptionRequestDTO(
            user_id=payment_method.user_id,
            plan_id="plan_premium",
            payment_method_id=payment_method.stripe_payment_method_id
        )
        
        # Create payment
        payment_request = CreatePaymentRequestDTO(
            user_id=subscription_request.user_id,
            amount=999,
            currency="usd",
            payment_method_id=subscription_request.payment_method_id
        )
        
        assert payment_method.user_id == subscription_request.user_id == payment_request.user_id
        assert payment_method.stripe_payment_method_id == subscription_request.payment_method_id == payment_request.payment_method_id

    def test_invoice_and_payment_relationship(self):
        """Test relationship between invoice and payment DTOs"""
        # Create invoice
        invoice = InvoiceResponseDTO(
            id="inv_relation",
            stripe_invoice_id="in_stripe_relation",
            subscription_id="sub_relation",
            user_id="user_relation",
            amount=1999,
            currency="eur",
            status="open"
        )
        
        # Create related payment
        payment = PaymentResponseDTO(
            id="pay_relation",
            user_id=invoice.user_id,
            stripe_payment_intent_id="pi_relation",
            amount=invoice.amount,
            currency=invoice.currency,
            status="requires_payment_method",
            invoice_id=invoice.id
        )
        
        assert payment.user_id == invoice.user_id
        assert payment.amount == invoice.amount
        assert payment.currency == invoice.currency
        assert payment.invoice_id == invoice.id
