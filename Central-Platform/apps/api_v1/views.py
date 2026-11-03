from django.http import JsonResponse
from django.views.decorators.http import require_GET


@require_GET
def api_v1_health(request):
    return JsonResponse(
        {
            "ok": True,
            "api_version": "v1",
            "service": "central-platform",
            "status": "healthy",
        }
    )
