import json
from decimal import InvalidOperation
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .security import authorize
from .quotes import quote

@csrf_exempt
@require_POST
def quote_view(request):
    error = authorize(request)
    if error: return JsonResponse({"ok":False,"error":error},status=403)
    try:
        payload=json.loads(request.body)
        result=quote(payload)
        return JsonResponse({"ok":True, **result})
    except (ValueError, TypeError, InvalidOperation, AttributeError) as exc:
        return JsonResponse({"ok":False,"error":str(exc)},status=422)
