"""
Tests para las excepciones del dominio de payments
"""

import pytest
from src.apps.payments.domain.exceptions import (
    PaymentError,
    StripeServiceError,
    CustomerCreationError,
    CheckoutSessionError,
    BillingPortalError,
    SubscriptionError,
    PaymentMethodError,
    WebhookError,
    InvoiceError,
    PlanNotFoundError,
    SubscriptionNotFoundError
)


class TestPaymentExceptions:
    """Tests para las excepciones del dominio de payments"""

    def test_payment_error_base(self):
        """Test excepción base PaymentError"""
        message = "Error general de pago"
        exception = PaymentError(message)
        
        assert str(exception) == message
        assert isinstance(exception, Exception)

    def test_stripe_service_error(self):
        """Test excepción StripeServiceError"""
        message = "Error del servicio de Stripe"
        exception = StripeServiceError(message)
        
        assert str(exception) == message
        assert isinstance(exception, PaymentError)
        assert isinstance(exception, Exception)

    def test_customer_creation_error(self):
        """Test excepción CustomerCreationError"""
        message = "Error al crear el cliente en Stripe"
        exception = CustomerCreationError(message)
        
        assert str(exception) == message
        assert isinstance(exception, StripeServiceError)
        assert isinstance(exception, PaymentError)

    def test_checkout_session_error(self):
        """Test excepción CheckoutSessionError"""
        message = "Error al crear la sesión de checkout"
        exception = CheckoutSessionError(message)
        
        assert str(exception) == message
        assert isinstance(exception, StripeServiceError)
        assert isinstance(exception, PaymentError)

    def test_billing_portal_error(self):
        """Test excepción BillingPortalError"""
        message = "Error al acceder al portal de facturación"
        exception = BillingPortalError(message)
        
        assert str(exception) == message
        assert isinstance(exception, StripeServiceError)
        assert isinstance(exception, PaymentError)

    def test_subscription_error(self):
        """Test excepción SubscriptionError"""
        message = "Error en la suscripción"
        exception = SubscriptionError(message)
        
        assert str(exception) == message
        assert isinstance(exception, StripeServiceError)
        assert isinstance(exception, PaymentError)

    def test_payment_method_error(self):
        """Test excepción PaymentMethodError"""
        message = "Error en el método de pago"
        exception = PaymentMethodError(message)
        
        assert str(exception) == message
        assert isinstance(exception, StripeServiceError)
        assert isinstance(exception, PaymentError)

    def test_webhook_error(self):
        """Test excepción WebhookError"""
        message = "Error procesando webhook de Stripe"
        exception = WebhookError(message)
        
        assert str(exception) == message
        assert isinstance(exception, StripeServiceError)
        assert isinstance(exception, PaymentError)

    def test_invoice_error(self):
        """Test excepción InvoiceError"""
        message = "Error en la factura"
        exception = InvoiceError(message)
        
        assert str(exception) == message
        assert isinstance(exception, StripeServiceError)
        assert isinstance(exception, PaymentError)

    def test_plan_not_found_error(self):
        """Test excepción PlanNotFoundError"""
        message = "Plan de suscripción no encontrado"
        exception = PlanNotFoundError(message)
        
        assert str(exception) == message
        assert isinstance(exception, PaymentError)
        assert not isinstance(exception, StripeServiceError)

    def test_subscription_not_found_error(self):
        """Test excepción SubscriptionNotFoundError"""
        message = "Suscripción no encontrada"
        exception = SubscriptionNotFoundError(message)
        
        assert str(exception) == message
        assert isinstance(exception, PaymentError)
        assert not isinstance(exception, StripeServiceError)

    def test_exception_hierarchy(self):
        """Test jerarquía de excepciones"""
        # Todas las excepciones de Stripe deben heredar de StripeServiceError
        stripe_exceptions = [
            CustomerCreationError("test"),
            CheckoutSessionError("test"),
            BillingPortalError("test"),
            SubscriptionError("test"),
            PaymentMethodError("test"),
            WebhookError("test"),
            InvoiceError("test")
        ]
        
        for exception in stripe_exceptions:
            assert isinstance(exception, StripeServiceError)
            assert isinstance(exception, PaymentError)
            assert isinstance(exception, Exception)

        # Excepciones específicas del dominio
        domain_exceptions = [
            PlanNotFoundError("test"),
            SubscriptionNotFoundError("test")
        ]
        
        for exception in domain_exceptions:
            assert isinstance(exception, PaymentError)
            assert not isinstance(exception, StripeServiceError)
            assert isinstance(exception, Exception)

    def test_all_exceptions_with_different_messages(self):
        """Test todas las excepciones con diferentes mensajes"""
        test_cases = [
            (PaymentError, "Error de pago genérico"),
            (StripeServiceError, "Error del servicio Stripe"),
            (CustomerCreationError, "No se pudo crear el cliente"),
            (CheckoutSessionError, "Sesión de checkout inválida"),
            (BillingPortalError, "Portal de facturación no disponible"),
            (SubscriptionError, "Suscripción no válida"),
            (PaymentMethodError, "Método de pago rechazado"),
            (WebhookError, "Webhook no procesado"),
            (InvoiceError, "Factura no encontrada"),
            (PlanNotFoundError, "Plan premium no existe"),
            (SubscriptionNotFoundError, "Suscripción del usuario no encontrada")
        ]
        
        for exception_class, message in test_cases:
            exception = exception_class(message)
            assert str(exception) == message
            assert isinstance(exception, Exception)

    def test_exceptions_can_be_raised_and_caught(self):
        """Test que las excepciones pueden ser lanzadas y capturadas"""
        # Test PaymentError específica
        with pytest.raises(PlanNotFoundError) as exc_info:
            raise PlanNotFoundError("Plan no encontrado")
        
        assert str(exc_info.value) == "Plan no encontrado"

        # Test captura por clase base
        with pytest.raises(PaymentError):
            raise SubscriptionNotFoundError("Suscripción no encontrada")

        # Test captura de StripeServiceError
        with pytest.raises(StripeServiceError):
            raise CustomerCreationError("Error creando cliente")

        # Test captura general
        with pytest.raises(Exception):
            raise WebhookError("Error en webhook")

    def test_exceptions_with_empty_messages(self):
        """Test excepciones con mensajes vacíos"""
        exceptions = [
            PaymentError(""),
            StripeServiceError(""),
            CustomerCreationError(""),
            PlanNotFoundError(""),
            SubscriptionNotFoundError("")
        ]
        
        for exception in exceptions:
            assert str(exception) == ""
            assert isinstance(exception, Exception)

    def test_exceptions_with_special_characters(self):
        """Test excepciones con caracteres especiales"""
        special_message = "Error: ñáéíóú @#$%^&*()[]{}|\\:;\"'<>,.?/~`"
        
        exceptions = [
            PaymentError(special_message),
            CustomerCreationError(special_message),
            PlanNotFoundError(special_message)
        ]
        
        for exception in exceptions:
            assert str(exception) == special_message
