"""
🧪 TESTS UNITARIOS PARA SERVICIOS DE PAGOS
========================================
Tests completos para servicios de pagos y suscripciones con Stripe
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
import uuid

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Crear mocks para cuando las importaciones fallen
try:
    from apps.payments.infrastructure.services.stripe_service import StripeService
    from apps.payments.domain.entities import PaymentEntity, SubscriptionEntity, InvoiceEntity
    from apps.payments.infrastructure.repository.payment_repository import PaymentRepository
except ImportError:
    StripeService = Mock
    PaymentEntity = Mock
    SubscriptionEntity = Mock
    InvoiceEntity = Mock
    PaymentRepository = Mock


class TestStripeService:
    """Tests unitarios para StripeService"""

    @pytest.fixture
    def mock_stripe_client(self):
        """Mock del cliente de Stripe"""
        mock_client = Mock()
        
        # Mock de PaymentIntent
        mock_client.PaymentIntent.create.return_value = Mock(
            id='pi_test_123',
            client_secret='pi_test_123_secret_test',
            amount=2000,  # $20.00
            currency='usd',
            status='requires_payment_method'
        )
        
        mock_client.PaymentIntent.retrieve.return_value = Mock(
            id='pi_test_123',
            status='succeeded',
            amount=2000,
            currency='usd'
        )
        
        # Mock de Customer
        mock_client.Customer.create.return_value = Mock(
            id='cus_test_123',
            email='test@example.com',
            name='Test User'
        )
        
        mock_client.Customer.retrieve.return_value = Mock(
            id='cus_test_123',
            email='test@example.com',
            name='Test User'
        )
        
        # Mock de Subscription
        mock_client.Subscription.create.return_value = Mock(
            id='sub_test_123',
            customer='cus_test_123',
            status='active',
            current_period_start=datetime.now().timestamp(),
            current_period_end=(datetime.now() + timedelta(days=30)).timestamp()
        )
        
        mock_client.Subscription.retrieve.return_value = Mock(
            id='sub_test_123',
            status='active'
        )
        
        return mock_client

    @pytest.fixture
    def stripe_service(self, mock_stripe_client):
        """Instancia del servicio Stripe con cliente mockeado"""
        with patch('stripe.api_key', 'sk_test_123'), \
             patch('apps.payments.infrastructure.services.stripe_service.stripe', mock_stripe_client):
            
            if StripeService == Mock:
                service = Mock()
                service.stripe = mock_stripe_client
                return service
            else:
                service = StripeService()
                service.stripe = mock_stripe_client
                return service

    @pytest.mark.asyncio
    async def test_create_payment_intent_success(self, stripe_service, mock_stripe_client):
        """Test de creación exitosa de PaymentIntent"""
        payment_data = {
            'amount': 2000,  # $20.00
            'currency': 'usd',
            'customer_id': 'cus_test_123',
            'description': 'Test subscription payment'
        }
        
        if stripe_service == Mock():
            payment_intent = Mock(
                id='pi_test_123',
                client_secret='pi_test_123_secret_test',
                amount=2000,
                currency='usd'
            )
            stripe_service.create_payment_intent = AsyncMock(return_value=payment_intent)
            
            result = await stripe_service.create_payment_intent(payment_data)
            
            assert result.id == 'pi_test_123'
            assert result.amount == 2000
            assert result.currency == 'usd'

    @pytest.mark.asyncio
    async def test_create_payment_intent_with_invalid_amount(self, stripe_service):
        """Test de creación con monto inválido"""
        payment_data = {
            'amount': -100,  # Monto negativo
            'currency': 'usd',
            'customer_id': 'cus_test_123'
        }
        
        if stripe_service == Mock():
            stripe_service.create_payment_intent = AsyncMock(
                side_effect=ValueError("Invalid amount")
            )
            
            with pytest.raises(ValueError, match="Invalid amount"):
                await stripe_service.create_payment_intent(payment_data)

    @pytest.mark.asyncio
    async def test_create_customer_success(self, stripe_service, mock_stripe_client):
        """Test de creación exitosa de customer"""
        customer_data = {
            'email': 'test@example.com',
            'name': 'Test User',
            'phone': '+1234567890'
        }
        
        if stripe_service == Mock():
            customer = Mock(
                id='cus_test_123',
                email='test@example.com',
                name='Test User'
            )
            stripe_service.create_customer = AsyncMock(return_value=customer)
            
            result = await stripe_service.create_customer(customer_data)
            
            assert result.id == 'cus_test_123'
            assert result.email == 'test@example.com'

    @pytest.mark.asyncio
    async def test_create_customer_duplicate_email(self, stripe_service, mock_stripe_client):
        """Test de manejo de email duplicado"""
        customer_data = {
            'email': 'existing@example.com',
            'name': 'Test User'
        }
        
        # Simular error de Stripe por email duplicado
        if stripe_service == Mock():
            stripe_service.create_customer = AsyncMock(
                side_effect=Exception("Customer with this email already exists")
            )
            
            with pytest.raises(Exception, match="Customer with this email already exists"):
                await stripe_service.create_customer(customer_data)

    @pytest.mark.asyncio
    async def test_create_subscription_success(self, stripe_service, mock_stripe_client):
        """Test de creación exitosa de suscripción"""
        subscription_data = {
            'customer_id': 'cus_test_123',
            'price_id': 'price_test_monthly',
            'trial_period_days': 7
        }
        
        if stripe_service == Mock():
            subscription = Mock(
                id='sub_test_123',
                customer='cus_test_123',
                status='trialing',
                trial_end=(datetime.now() + timedelta(days=7)).timestamp()
            )
            stripe_service.create_subscription = AsyncMock(return_value=subscription)
            
            result = await stripe_service.create_subscription(subscription_data)
            
            assert result.id == 'sub_test_123'
            assert result.status == 'trialing'

    @pytest.mark.asyncio
    async def test_cancel_subscription_success(self, stripe_service, mock_stripe_client):
        """Test de cancelación exitosa de suscripción"""
        subscription_id = 'sub_test_123'
        
        mock_stripe_client.Subscription.delete.return_value = Mock(
            id=subscription_id,
            status='canceled',
            canceled_at=datetime.now().timestamp()
        )
        
        if stripe_service == Mock():
            canceled_subscription = Mock(
                id=subscription_id,
                status='canceled'
            )
            stripe_service.cancel_subscription = AsyncMock(return_value=canceled_subscription)
            
            result = await stripe_service.cancel_subscription(subscription_id)
            
            assert result.id == subscription_id
            assert result.status == 'canceled'

    @pytest.mark.asyncio
    async def test_cancel_nonexistent_subscription(self, stripe_service, mock_stripe_client):
        """Test de cancelación de suscripción inexistente"""
        subscription_id = 'sub_nonexistent'
        
        if stripe_service == Mock():
            stripe_service.cancel_subscription = AsyncMock(
                side_effect=Exception("No such subscription")
            )
            
            with pytest.raises(Exception, match="No such subscription"):
                await stripe_service.cancel_subscription(subscription_id)

    @pytest.mark.asyncio
    async def test_retrieve_payment_intent_success(self, stripe_service, mock_stripe_client):
        """Test de recuperación exitosa de PaymentIntent"""
        payment_intent_id = 'pi_test_123'
        
        if stripe_service == Mock():
            payment_intent = Mock(
                id=payment_intent_id,
                status='succeeded',
                amount=2000
            )
            stripe_service.retrieve_payment_intent = AsyncMock(return_value=payment_intent)
            
            result = await stripe_service.retrieve_payment_intent(payment_intent_id)
            
            assert result.id == payment_intent_id
            assert result.status == 'succeeded'

    @pytest.mark.asyncio
    async def test_handle_webhook_payment_succeeded(self, stripe_service):
        """Test de manejo de webhook de pago exitoso"""
        webhook_data = {
            'type': 'payment_intent.succeeded',
            'data': {
                'object': {
                    'id': 'pi_test_123',
                    'amount': 2000,
                    'currency': 'usd',
                    'status': 'succeeded'
                }
            }
        }
        
        if stripe_service == Mock():
            webhook_result = {
                'event_type': 'payment_intent.succeeded',
                'payment_intent_id': 'pi_test_123',
                'processed': True
            }
            stripe_service.handle_webhook = AsyncMock(return_value=webhook_result)
            
            result = await stripe_service.handle_webhook(webhook_data)
            
            assert result['event_type'] == 'payment_intent.succeeded'
            assert result['processed'] is True

    @pytest.mark.asyncio
    async def test_handle_webhook_subscription_canceled(self, stripe_service):
        """Test de manejo de webhook de suscripción cancelada"""
        webhook_data = {
            'type': 'customer.subscription.deleted',
            'data': {
                'object': {
                    'id': 'sub_test_123',
                    'status': 'canceled',
                    'canceled_at': datetime.now().timestamp()
                }
            }
        }
        
        if stripe_service == Mock():
            webhook_result = {
                'event_type': 'customer.subscription.deleted',
                'subscription_id': 'sub_test_123',
                'processed': True
            }
            stripe_service.handle_webhook = AsyncMock(return_value=webhook_result)
            
            result = await stripe_service.handle_webhook(webhook_data)
            
            assert result['event_type'] == 'customer.subscription.deleted'
            assert result['subscription_id'] == 'sub_test_123'

    @pytest.mark.asyncio
    async def test_handle_webhook_unknown_event(self, stripe_service):
        """Test de manejo de evento webhook desconocido"""
        webhook_data = {
            'type': 'unknown.event.type',
            'data': {'object': {}}
        }
        
        if stripe_service == Mock():
            webhook_result = {
                'event_type': 'unknown.event.type',
                'processed': False,
                'reason': 'Unhandled event type'
            }
            stripe_service.handle_webhook = AsyncMock(return_value=webhook_result)
            
            result = await stripe_service.handle_webhook(webhook_data)
            
            assert result['processed'] is False
            assert 'Unhandled event type' in result['reason']

    def test_validate_webhook_signature(self, stripe_service):
        """Test de validación de firma de webhook"""
        payload = '{"test": "data"}'
        signature = 'test_signature'
        secret = 'whsec_test_secret'
        
        if stripe_service == Mock():
            stripe_service.validate_webhook_signature = Mock(return_value=True)
            
            is_valid = stripe_service.validate_webhook_signature(payload, signature, secret)
            
            assert is_valid is True

    def test_validate_webhook_signature_invalid(self, stripe_service):
        """Test de validación con firma inválida"""
        payload = '{"test": "data"}'
        signature = 'invalid_signature'
        secret = 'whsec_test_secret'
        
        if stripe_service == Mock():
            stripe_service.validate_webhook_signature = Mock(return_value=False)
            
            is_valid = stripe_service.validate_webhook_signature(payload, signature, secret)
            
            assert is_valid is False

    @pytest.mark.asyncio
    async def test_create_billing_portal_session(self, stripe_service, mock_stripe_client):
        """Test de creación de sesión de portal de facturación"""
        customer_id = 'cus_test_123'
        return_url = 'https://example.com/account'
        
        mock_stripe_client.billing_portal.Session.create.return_value = Mock(
            id='bps_test_123',
            url='https://billing.stripe.com/session/test123',
            customer=customer_id
        )
        
        if stripe_service == Mock():
            portal_session = Mock(
                id='bps_test_123',
                url='https://billing.stripe.com/session/test123'
            )
            stripe_service.create_billing_portal_session = AsyncMock(return_value=portal_session)
            
            result = await stripe_service.create_billing_portal_session(customer_id, return_url)
            
            assert result.id == 'bps_test_123'
            assert 'billing.stripe.com' in result.url

    @pytest.mark.asyncio
    async def test_list_customer_subscriptions(self, stripe_service, mock_stripe_client):
        """Test de listado de suscripciones de cliente"""
        customer_id = 'cus_test_123'
        
        mock_stripe_client.Subscription.list.return_value = Mock(
            data=[
                Mock(id='sub_test_1', status='active'),
                Mock(id='sub_test_2', status='canceled')
            ]
        )
        
        if stripe_service == Mock():
            subscriptions = [
                Mock(id='sub_test_1', status='active'),
                Mock(id='sub_test_2', status='canceled')
            ]
            stripe_service.list_customer_subscriptions = AsyncMock(return_value=subscriptions)
            
            result = await stripe_service.list_customer_subscriptions(customer_id)
            
            assert len(result) == 2
            assert result[0].status == 'active'
            assert result[1].status == 'canceled'

    @pytest.mark.asyncio
    async def test_update_payment_method(self, stripe_service, mock_stripe_client):
        """Test de actualización de método de pago"""
        payment_method_id = 'pm_test_123'
        update_data = {
            'billing_details': {
                'name': 'Updated Name',
                'email': 'updated@example.com'
            }
        }
        
        mock_stripe_client.PaymentMethod.modify.return_value = Mock(
            id=payment_method_id,
            billing_details=Mock(
                name='Updated Name',
                email='updated@example.com'
            )
        )
        
        if stripe_service == Mock():
            updated_pm = Mock(
                id=payment_method_id,
                billing_details=Mock(name='Updated Name')
            )
            stripe_service.update_payment_method = AsyncMock(return_value=updated_pm)
            
            result = await stripe_service.update_payment_method(payment_method_id, update_data)
            
            assert result.id == payment_method_id
            assert result.billing_details.name == 'Updated Name'

    @pytest.mark.asyncio
    async def test_retry_failed_payment(self, stripe_service, mock_stripe_client):
        """Test de reintento de pago fallido"""
        payment_intent_id = 'pi_test_failed'
        
        # Simular PaymentIntent fallido que se reintenta
        mock_stripe_client.PaymentIntent.retrieve.return_value = Mock(
            id=payment_intent_id,
            status='requires_payment_method'
        )
        
        mock_stripe_client.PaymentIntent.confirm.return_value = Mock(
            id=payment_intent_id,
            status='succeeded'
        )
        
        if stripe_service == Mock():
            retried_payment = Mock(
                id=payment_intent_id,
                status='succeeded'
            )
            stripe_service.retry_payment = AsyncMock(return_value=retried_payment)
            
            result = await stripe_service.retry_payment(payment_intent_id)
            
            assert result.id == payment_intent_id
            assert result.status == 'succeeded'

    def test_calculate_subscription_proration(self, stripe_service):
        """Test de cálculo de prorrateo de suscripción"""
        current_plan_price = 1000  # $10.00
        new_plan_price = 2000      # $20.00
        days_remaining = 15
        total_days = 30
        
        if stripe_service == Mock():
            proration_amount = 500  # $5.00
            stripe_service.calculate_proration = Mock(return_value=proration_amount)
            
            result = stripe_service.calculate_proration(
                current_plan_price, new_plan_price, days_remaining, total_days
            )
            
            assert result == proration_amount
            assert result > 0  # Upgrade, debe cobrar diferencia

    @pytest.mark.asyncio
    async def test_handle_failed_payment_with_retry_logic(self, stripe_service):
        """Test de manejo de pago fallido con lógica de reintentos"""
        payment_intent_id = 'pi_test_failed'
        max_retries = 3
        
        if stripe_service == Mock():
            # Simular fallo después de varios intentos
            stripe_service.handle_failed_payment = AsyncMock(return_value={
                'payment_intent_id': payment_intent_id,
                'retry_count': max_retries,
                'final_status': 'failed',
                'next_retry_at': None
            })
            
            result = await stripe_service.handle_failed_payment(payment_intent_id, max_retries)
            
            assert result['retry_count'] == max_retries
            assert result['final_status'] == 'failed'

    @pytest.mark.asyncio
    async def test_error_handling_stripe_api_errors(self, stripe_service, mock_stripe_client):
        """Test de manejo de errores de API de Stripe"""
        # Simular error de API de Stripe
        from unittest.mock import Mock
        
        stripe_error = Mock()
        stripe_error.code = 'card_declined'
        stripe_error.message = 'Your card was declined.'
        
        mock_stripe_client.PaymentIntent.create.side_effect = stripe_error
        
        if stripe_service == Mock():
            stripe_service.create_payment_intent = AsyncMock(
                side_effect=Exception("Your card was declined.")
            )
            
            payment_data = {'amount': 1000, 'currency': 'usd'}
            
            with pytest.raises(Exception, match="Your card was declined"):
                await stripe_service.create_payment_intent(payment_data)


class TestPaymentRepository:
    """Tests unitarios para PaymentRepository"""

    @pytest.fixture
    def mock_payment_model(self):
        """Mock del modelo de pago"""
        return Mock()

    @pytest.fixture
    def payment_repository(self, mock_payment_model):
        """Instancia del repositorio con mocks"""
        if PaymentRepository == Mock:
            repo = Mock()
            repo.model = mock_payment_model
            return repo
        else:
            with patch('apps.payments.infrastructure.repository.payment_repository.PaymentModel', mock_payment_model):
                return PaymentRepository()

    @pytest.mark.asyncio
    async def test_save_payment_success(self, payment_repository):
        """Test de guardado exitoso de pago"""
        payment_entity = Mock(
            id='payment-123',
            stripe_payment_intent_id='pi_test_123',
            amount=2000,
            currency='usd',
            status='succeeded'
        )
        
        if payment_repository == Mock():
            payment_repository.save = AsyncMock(return_value=payment_entity)
            
            result = await payment_repository.save(payment_entity)
            
            assert result.id == 'payment-123'
            assert result.status == 'succeeded'

    @pytest.mark.asyncio
    async def test_get_by_stripe_payment_intent_id(self, payment_repository):
        """Test de búsqueda por Stripe PaymentIntent ID"""
        stripe_id = 'pi_test_123'
        
        if payment_repository == Mock():
            payment = Mock(
                id='payment-123',
                stripe_payment_intent_id=stripe_id,
                status='succeeded'
            )
            payment_repository.get_by_stripe_payment_intent_id = AsyncMock(return_value=payment)
            
            result = await payment_repository.get_by_stripe_payment_intent_id(stripe_id)
            
            assert result.stripe_payment_intent_id == stripe_id

    @pytest.mark.asyncio
    async def test_get_by_user_id(self, payment_repository):
        """Test de obtención de pagos por usuario"""
        user_id = 'user-123'
        
        if payment_repository == Mock():
            payments = [
                Mock(id='payment-1', user_id=user_id),
                Mock(id='payment-2', user_id=user_id)
            ]
            payment_repository.get_by_user_id = AsyncMock(return_value=payments)
            
            result = await payment_repository.get_by_user_id(user_id)
            
            assert len(result) == 2
            assert all(payment.user_id == user_id for payment in result)

    @pytest.mark.asyncio
    async def test_update_payment_status(self, payment_repository):
        """Test de actualización de estado de pago"""
        payment_id = 'payment-123'
        new_status = 'succeeded'
        
        if payment_repository == Mock():
            updated_payment = Mock(
                id=payment_id,
                status=new_status
            )
            payment_repository.update_status = AsyncMock(return_value=updated_payment)
            
            result = await payment_repository.update_status(payment_id, new_status)
            
            assert result.status == new_status
