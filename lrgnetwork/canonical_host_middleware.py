"""
Middleware that redirects non-canonical hosts to the canonical host (e.g. bare domain → www).

Only runs when CANONICAL_HOST is set (production). Redirects only hosts listed in
REDIRECT_TO_CANONICAL_HOSTS so fly.dev and internal hosts are left alone.
Uses 301 so search engines treat the canonical URL as the primary one.
"""

from django.http import HttpResponsePermanentRedirect
from django.conf import settings


class CanonicalHostMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        canonical_host = getattr(settings, "CANONICAL_HOST", None)
        redirect_hosts = getattr(settings, "REDIRECT_TO_CANONICAL_HOSTS", ())
        self._canonical_host = canonical_host
        self._redirect_hosts_lower = (
            frozenset(h.lower() for h in redirect_hosts)
            if redirect_hosts
            else frozenset()
        )

    def __call__(self, request):
        if not self._canonical_host or not self._redirect_hosts_lower:
            return self.get_response(request)

        request_host = request.get_host().split(":")[0].lower()
        if request_host in self._redirect_hosts_lower:
            current_url = request.build_absolute_uri()
            canonical_url = current_url.replace(request_host, self._canonical_host, 1)
            return HttpResponsePermanentRedirect(canonical_url)

        return self.get_response(request)
