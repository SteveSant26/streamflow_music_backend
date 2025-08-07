from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class BillingPortalSession:
    """Sesión del portal de facturación"""

    id: str
    stripe_session_id: str
    user_id: str
    url: str
    return_url: str
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
