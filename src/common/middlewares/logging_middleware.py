import asyncio
import logging
import time
import uuid

from django.utils.deprecation import MiddlewareMixin


class LoggingMiddleware(MiddlewareMixin):
    """Middleware para logging automático de requests HTTP"""

    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.logger = logging.getLogger("django.request")
        # Check if we have async views
        if get_response and asyncio.iscoroutinefunction(get_response):
            self.async_capable = True
            self.sync_capable = False

    # Sync methods
    def process_request(self, request):
        return self._process_request_impl(request)

    def process_response(self, request, response):
        return self._process_response_impl(request, response)

    # Async methods
    async def aprocess_request(self, request):
        return self._process_request_impl(request)

    async def aprocess_response(self, request, response):
        return self._process_response_impl(request, response)

    def _process_request_impl(self, request):
        request.request_id = str(uuid.uuid4())[:8]

        # Guardar tiempo inicio
        request._start_time = time.time()

        # Datos del request
        method = request.method
        url = request.build_absolute_uri()
        client_ip = self.get_client_ip(request)
        user_agent = request.META.get("HTTP_USER_AGENT", "unknown")

        self.logger.info(
            f"[{request.request_id}] {method} {url} - IP: {client_ip} - User-Agent: {user_agent[:50]}..."
        )

    def _process_response_impl(self, request, response):
        # Calcular tiempo transcurrido
        start_time = getattr(request, "_start_time", None)
        if start_time:
            process_time = time.time() - start_time
        else:
            process_time = -1

        # Datos básicos
        method = getattr(request, "method", "unknown")
        url = getattr(request, "build_absolute_uri", lambda: "unknown")()
        request_id = getattr(request, "request_id", "unknown")

        self.logger.info(
            f"[{request_id}] {method} {url} - Status: {response.status_code} - Time: {process_time:.3f}s"
        )

        # Añadir headers para debugging
        response["X-Request-ID"] = request_id
        if process_time >= 0:
            response["X-Process-Time"] = f"{process_time:.3f}"

        return response

    # Async versions of exception handling
    async def aprocess_exception(self, request, exception):
        return self.process_exception(request, exception)

    def process_exception(self, request, exception):
        # Calcular tiempo incluso en caso de error
        start_time = getattr(request, "_start_time", None)
        if start_time:
            process_time = time.time() - start_time
        else:
            process_time = -1

        method = getattr(request, "method", "unknown")
        url = getattr(request, "build_absolute_uri", lambda: "unknown")()
        request_id = getattr(request, "request_id", "unknown")

        self.logger.error(
            f"[{request_id}] {method} {url} - ERROR: {str(exception)} - Time: {process_time:.3f}s"
        )
        # Django seguirá el flujo normal de la excepción después
        return None

    def get_client_ip(self, request):
        # Intentar obtener IP real, incluyendo casos con proxy reverso
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR", "unknown")
        return ip
