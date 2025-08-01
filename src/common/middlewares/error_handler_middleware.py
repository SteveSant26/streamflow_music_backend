import asyncio

from django.http import JsonResponse
from rest_framework import status
from rest_framework.serializers import ValidationError

from ..exceptions import DomainException


class ErrorHandlerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.
        if asyncio.iscoroutinefunction(self.get_response):
            # Mark that this middleware works with async views
            self.async_capable = True
            self.sync_capable = False

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as exception:
            return self.process_exception(request, exception)

    async def __acall__(self, request):
        try:
            response = await self.get_response(request)
            return response
        except Exception as exception:
            return self.process_exception(request, exception)

    def process_exception(self, _, exception):
        if isinstance(exception, DomainException):
            identifier = getattr(exception, "identifier", "unknown_error")
            return self._handle_error(exception.args[0], exception.code, identifier)
        if isinstance(exception, ValidationError):
            return self._handle_error(exception.detail, status.HTTP_400_BAD_REQUEST)

        return self._handle_error(
            {"internal_server_error": [str(exception)]},
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "internal_server_error",
        )

    def _handle_error(self, message, code, identifier="error"):
        if not isinstance(message, dict):
            message = {identifier: [str(message)]}

        error_response = {
            "errors": message,
            "code": code,
        }
        return JsonResponse(error_response, status=code)
