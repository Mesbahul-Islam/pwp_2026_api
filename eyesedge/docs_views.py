"""Views to serve manually maintained OpenAPI documentation."""

from pathlib import Path

from django.conf import settings
from django.http import Http404, HttpResponse
from django.shortcuts import render


def openapi_yaml(request):
    """Serve the root-level openapi.yaml file."""
    spec_path = settings.BASE_DIR / "openapi.yaml"

    if not spec_path.exists():
        raise Http404("openapi.yaml not found")

    content = spec_path.read_text(encoding="utf-8")
    return HttpResponse(content, content_type="application/yaml; charset=utf-8")


def swagger_ui(request):
    """Render Swagger UI bound to the served YAML schema endpoint."""
    return render(request, "eyesedge/swagger_ui.html")


def client(request):
    """Render the single-page management console at the API root."""
    return render(request, "eyesedge/client.html")
