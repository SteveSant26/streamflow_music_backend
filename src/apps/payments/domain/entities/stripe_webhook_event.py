from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class StripeWebhookEventEntity:
    """Evento de webhook de Stripe"""

    id: str
    stripe_event_id: str
    event_type: str
    processed: bool = False
    data: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
