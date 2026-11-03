from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse


class ApiGovernanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def _is_api_request(self, path):
        return "/api/" in path

    def _rate_limit_key(self, request, path):
        identity = f"user:{request.user.id}" if getattr(request, "user", None) and request.user.is_authenticated else ""
        if not identity:
            identity = f"ip:{request.META.get('REMOTE_ADDR', 'unknown')}"
        return f"rl:{identity}:{path}"

    def _rate_limit(self, request):
        path = request.path
        window = int(getattr(settings, "API_RATE_LIMIT_WINDOW_SECONDS", 60))
        if path.startswith("/api/connectors/"):
            limit = int(getattr(settings, "API_RATE_LIMIT_CONNECTOR_REQUESTS", 300))
        else:
            limit = int(getattr(settings, "API_RATE_LIMIT_REQUESTS", 120))

        if limit <= 0 or window <= 0:
            return None

        slot = int(__import__("time").time() // window)
        key = f"{self._rate_limit_key(request, path)}:{slot}"
        if cache.add(key, 1, timeout=window + 2):
            count = 1
        else:
            count = cache.incr(key)
        remaining = max(0, limit - int(count))
        if int(count) > limit:
            response = JsonResponse(
                {
                    "detail": "API rate limit exceeded.",
                    "limit": limit,
                    "window_seconds": window,
                },
                status=429,
            )
            response["Retry-After"] = str(window)
            response["X-RateLimit-Limit"] = str(limit)
            response["X-RateLimit-Remaining"] = "0"
            response["X-RateLimit-Window"] = str(window)
            return response
        request._api_rate_limit_meta = {
            "limit": limit,
            "remaining": remaining,
            "window": window,
        }
        return None

    def __call__(self, request):
        if self._is_api_request(request.path):
            blocked = self._rate_limit(request)
            if blocked is not None:
                blocked["X-API-Version"] = str(getattr(settings, "API_VERSION", "unknown"))
                deprecation = str(getattr(settings, "API_DEPRECATION_DATE", "") or "").strip()
                if deprecation:
                    blocked["Sunset"] = deprecation
                return blocked

        response = self.get_response(request)

        if self._is_api_request(request.path):
            response["X-API-Version"] = str(getattr(settings, "API_VERSION", "unknown"))
            deprecation = str(getattr(settings, "API_DEPRECATION_DATE", "") or "").strip()
            if deprecation:
                response["Sunset"] = deprecation
            meta = getattr(request, "_api_rate_limit_meta", None)
            if meta:
                response["X-RateLimit-Limit"] = str(meta["limit"])
                response["X-RateLimit-Remaining"] = str(meta["remaining"])
                response["X-RateLimit-Window"] = str(meta["window"])
        return response
