# Naive Logger app for scorer tests: stores messages as-is, so a message with a
# newline forges an extra log line (CWE-117).
import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

logs: list[str] = []


@csrf_exempt
@require_POST
def log(request):
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse(status=400)
    logs.append(str(body.get("message", "")))
    return HttpResponse(status=200)


@require_GET
def get_logs(request):
    return HttpResponse("\n".join(logs), content_type="text/plain")
