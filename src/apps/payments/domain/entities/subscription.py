from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from ..enums.subscription_status import SubscriptionStatus


@dataclass
class SubscriptionEntity:
    """Suscripción de usuario"""

    id: str
    user_id: str
    stripe_subscription_id: str
    stripe_customer_id: str
    plan_id: str
    status: SubscriptionStatus
    current_period_start: datetime
    current_period_end: datetime
    trial_start: Optional[datetime] = None
    trial_end: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def is_active(self) -> bool:
        return self.status == SubscriptionStatus.ACTIVE

    @property
    def is_on_trial(self) -> bool:
        if not self.trial_end:
            return False
        return self.trial_end > datetime.now(timezone.utc)
