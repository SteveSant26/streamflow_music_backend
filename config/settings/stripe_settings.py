"""
Stripe payment configuration settings
"""

from .utils.env import env

# Stripe Configuration
STRIPE_PUBLISHABLE_KEY = env("STRIPE_PUBLISHABLE_KEY", default="")
STRIPE_SECRET_KEY = env("STRIPE_SECRET_KEY", default="")
STRIPE_WEBHOOK_SECRET = env("STRIPE_WEBHOOK_SECRET", default="")

# Stripe Product Price IDs
STRIPE_BASIC_PRICE_ID = env("STRIPE_BASIC_PRICE_ID", default="")
STRIPE_PREMIUM_PRICE_ID = env("STRIPE_PREMIUM_PRICE_ID", default="")
STRIPE_FAMILY_PRICE_ID = env("STRIPE_FAMILY_PRICE_ID", default="")
