"""
URL configuration for lrgnetwork project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import include, path
from django.views.generic import TemplateView

from games.views import gallery
from lrgnetwork.seo import build_website_jsonld
from lrgnetwork.sitemaps import GameSitemap, StaticViewSitemap

sitemaps = {
    "static": StaticViewSitemap,
    "games": GameSitemap,
}


def health(request):
    return HttpResponse("ok", content_type="text/plain", status=200)


def home(request):
    return render(
        request,
        "static_pages/about.html",
        {"website_jsonld": build_website_jsonld(request)},
    )


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        "",
        f"Sitemap: {request.scheme}://{request.get_host()}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def test_sentry(request):
    """Temporary: raise to verify Sentry in prod. Remove after testing."""
    raise ValueError("Sentry test – remove this route after verifying.")


urlpatterns = [
    path("robots.txt", robots_txt, name="robots_txt"),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("health/", health, name="health"),
    path("test-sentry/", test_sentry, name="test_sentry"),
    path("", home, name="home"),
    path("game-management/", admin.site.urls),
    path("games/", include("games.urls")),
    path("gallery/", gallery, name="gallery"),
    path(
        "community/",
        TemplateView.as_view(template_name="static_pages/community.html"),
        name="community",
    ),
    path(
        "resources/",
        TemplateView.as_view(template_name="static_pages/resources_index.html"),
        name="resources",
    ),
    path(
        "resources/guided-questions/",
        TemplateView.as_view(
            template_name="static_pages/resources_guided_questions.html"
        ),
        name="resources_guided_questions",
    ),
    path(
        "resources/building-team/",
        TemplateView.as_view(template_name="static_pages/resources_building_team.html"),
        name="resources_building_team",
    ),
    path(
        "resources/budgets/",
        TemplateView.as_view(template_name="static_pages/resources_budgets.html"),
        name="resources_budgets",
    ),
    path(
        "resources/casting/",
        TemplateView.as_view(template_name="static_pages/resources_casting.html"),
        name="resources_casting",
    ),
    path(
        "resources/rules-expectations/",
        TemplateView.as_view(
            template_name="static_pages/resources_rules_expectations.html"
        ),
        name="resources_rules_expectations",
    ),
    path(
        "resources/challenge-ideas/",
        TemplateView.as_view(
            template_name="static_pages/resources_challenge_ideas.html"
        ),
        name="resources_challenge_ideas",
    ),
    path(
        "resources/art-department/",
        TemplateView.as_view(
            template_name="static_pages/resources_art_department.html"
        ),
        name="resources_art_department",
    ),
    path(
        "resources/social-media/",
        TemplateView.as_view(template_name="static_pages/resources_social_media.html"),
        name="resources_social_media",
    ),
    path(
        "resources/player-care/",
        TemplateView.as_view(template_name="static_pages/resources_player_care.html"),
        name="resources_player_care",
    ),
    path(
        "resources/editing/",
        TemplateView.as_view(template_name="static_pages/resources_editing.html"),
        name="resources_editing",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
