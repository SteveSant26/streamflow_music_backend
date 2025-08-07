from enum import Enum


class PaymentStatus(Enum):
    SUCCEEDED = "succeeded"
    PENDING = "pending"
    FAILED = "failed"
    CANCELED = "canceled"
