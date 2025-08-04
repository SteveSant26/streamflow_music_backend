import asyncio
import logging
import time
import uuid


class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger("django.request")
        self._is_coroutine = asyncio.iscoroutinefunction(get_response)

    def __call__(self, request):
        if self._is_coroutine:
            return self.__acall__(request)
        return self.__sync_call__(request)

    def __sync_call__(self, request):
        self._process_request(request)
        try:
            response = self.get_response(request)
        except Exception as ex:
            self._process_exception(request, ex)
            raise
        return self._process_response(request, response)

    async def __acall__(self, request):
        self._process_request(request)
        try:
            response = await self.get_response(request)
        except Exception as ex:
            self._process_exception(request, ex)
            raise
        return self._process_response(request, response)

    def _process_request(self, request):
        request.request_id = str(uuid.uuid4())[:8]
        request._start_time = time.time()
        self.logger.info(
            f"[{request.request_id}] {request.method} {request.build_absolute_uri()} - "
            f"IP: {self.get_client_ip(request)} - User-Agent: {request.META.get('HTTP_USER_AGENT', '')[:50]}..."
        )

    def _process_response(self, request, response):
        duration = time.time() - getattr(request, "_start_time", time.time())
        request_id = getattr(request, "request_id", "unknown")
        self.logger.info(
            f"[{request_id}] {request.method} {request.build_absolute_uri()} - "
            f"Status: {response.status_code} - Time: {duration:.3f}s"
        )
        response["X-Request-ID"] = request_id
        response["X-Process-Time"] = f"{duration:.3f}"
        return response

    def _process_exception(self, request, exception):
        duration = time.time() - getattr(request, "_start_time", time.time())
        request_id = getattr(request, "request_id", "unknown")
        self.logger.error(
            f"[{request_id}] {request.method} {request.build_absolute_uri()} - "
            f"ERROR: {str(exception)} - Time: {duration:.3f}s"
        )

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        return (
            x_forwarded_for.split(",")[0].strip()
            if x_forwarded_for
            else request.META.get("REMOTE_ADDR", "unknown")
        )
