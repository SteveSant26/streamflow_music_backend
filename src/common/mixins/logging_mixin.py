from ..utils.logging_config import get_logger


class LoggingMixin:
    """Mixin que proporciona funcionalidad de logging a las clases."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._logger = get_logger(self.__class__.__name__)

    @property
    def logger(self):
        if not hasattr(self, "_logger"):
            self._logger = get_logger(self.__class__.__name__)
        return self._logger
