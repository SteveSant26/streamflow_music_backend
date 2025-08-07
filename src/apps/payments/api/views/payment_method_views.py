from rest_framework.permissions import IsAuthenticated

from common.mixins import CRUDViewSetMixin

from ...infrastructure.filters.payment_method_filter import PaymentMethodFilter
from ...infrastructure.models.payment_method import PaymentMethodModel
from ..serializers import PaymentMethodSerializer


class PaymentMethodViewSet(CRUDViewSetMixin):
    """
    ViewSet for managing user payment methods with CRUD operations, filtering, and logging.
    """

    queryset = PaymentMethodModel.objects.all()
    serializer_class = PaymentMethodSerializer
    filterset_class = PaymentMethodFilter
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only return payment methods for the authenticated user
        user = self.request.user
        return super().get_queryset().filter(user=user)
