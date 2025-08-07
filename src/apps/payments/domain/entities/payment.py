from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional

from ..enums.payment_status import PaymentStatus


@dataclass
class PaymentEntity:
    """Pago realizado"""

    id: str
    stripe_payment_intent_id: str
    user_id: str
    amount: int  # En centavos
    currency: str
    status: PaymentStatus
    payment_method_id: Optional[str] = None
    invoice_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
