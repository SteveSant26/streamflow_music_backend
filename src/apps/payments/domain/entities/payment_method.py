from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class PaymentMethodEntity:
    """Método de pago del usuario"""

    id: str
    stripe_payment_method_id: str
    user_id: str
    type: str  # 'card', 'sepa_debit', etc.
    card_brand: Optional[str] = None
    card_last4: Optional[str] = None
    card_exp_month: Optional[int] = None
    card_exp_year: Optional[int] = None
    is_default: bool = False
    created_at: Optional[datetime] = None
