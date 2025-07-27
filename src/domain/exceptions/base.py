from typing import Any, Dict, Optional


class DomainException(Exception):
    """Excepción base del dominio - equivalente a BaseError de Django"""

    def __init__(
        self,
        message: str,
        code: int = 500,
        identifier: str = "domain_error",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.code = code  # HTTP status code
        self.identifier = identifier  # Para identificar el tipo de error
        self.details = details or {}
        super().__init__(self._serialize_errors(message))

    def _serialize_errors(self, errors):
        if isinstance(errors, list):
            return {self.identifier: [str(e) for e in errors]}

        if isinstance(errors, dict):
            serialized = {}
            for key, error_list in errors.items():
                serialized[key] = [str(e) for e in error_list]
            return serialized

        return {self.identifier: [str(errors)]}


__all__ = ["DomainException"]
