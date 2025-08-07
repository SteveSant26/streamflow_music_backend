from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CheckoutSession:
    """Sesión de checkout de Stripe"""

    id: str
    stripe_session_id: str
    user_id: str
    plan_id: str
    amount: int
    currency: str
    success_url: str
    cancel_url: str
    status: str
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
