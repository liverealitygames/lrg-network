"""
Middleware that responds to health-check requests before any host validation.

Fly.io (and other platforms) may hit the app with an internal Host header.
By handling /health/ before CommonMiddleware runs, we avoid DisallowedHost
and always return 200 as long as the app is running.
"""

from django.http import HttpResponse


class HealthCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path in ("/health/", "/health"):
            return HttpResponse("ok")
        return self.get_response(request)
