from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class SubscriptionPlanEntity:
    """Plan de suscripción"""

    id: str
    name: str
    description: str
    price: int  # En centavos
    currency: str
    interval: str  # 'month' o 'year'
    interval_count: int
    features: List[str]
    stripe_price_id: str
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
