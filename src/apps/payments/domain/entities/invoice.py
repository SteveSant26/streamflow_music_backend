from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ..enums.invoice_status import InvoiceStatus


@dataclass
class Invoice:
    """Factura de suscripción"""

    id: str
    stripe_invoice_id: str
    subscription_id: str
    user_id: str
    amount: int  # En centavos
    currency: str
    status: InvoiceStatus
    due_date: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
