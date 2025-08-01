"""
Stripe Configuration for Django Backend
This file contains all the necessary configurations for Stripe integration
"""

# settings/stripe_settings.py
import os
from .base import env

# Stripe Configuration
STRIPE_PUBLISHABLE_KEY = env('STRIPE_PUBLISHABLE_KEY', default='')
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY', default='')
STRIPE_WEBHOOK_SECRET = env('STRIPE_WEBHOOK_SECRET', default='')

# Price IDs from Stripe Dashboard (you'll get these after creating products)
STRIPE_PRICE_IDS = {
    'premium_monthly': env('STRIPE_PREMIUM_MONTHLY_PRICE_ID', default=''),
    'premium_yearly': env('STRIPE_PREMIUM_YEARLY_PRICE_ID', default=''),
}

# Stripe Configuration
STRIPE_CONFIG = {
    'api_version': '2023-10-16',
    'api_key': STRIPE_SECRET_KEY,
    'webhook_secret': STRIPE_WEBHOOK_SECRET,
    'success_url': env('FRONTEND_URL', default='http://localhost:4200') + '/subscription/success',
    'cancel_url': env('FRONTEND_URL', default='http://localhost:4200') + '/subscription/plans',
}

# Add to your main settings
if STRIPE_SECRET_KEY:
    import stripe
    stripe.api_key = STRIPE_SECRET_KEY
    stripe.api_version = STRIPE_CONFIG['api_version']
