from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from games.models import Game


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return [
            "home",
            "game_list",
            "gallery",
            "community",
            "resources",
            "resources_guided_questions",
            "resources_building_team",
            "resources_budgets",
            "resources_casting",
            "resources_rules_expectations",
            "resources_challenge_ideas",
            "resources_art_department",
            "resources_social_media",
            "resources_player_care",
            "resources_editing",
        ]

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        if item == "home":
            return 1.0
        if item == "game_list":
            return 0.9
        return 0.5


class GameSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Game.objects.filter(is_removed=False).order_by("name")

    def location(self, obj):
        return reverse("game_detail", args=[obj.slug])

    def lastmod(self, obj):
        return obj.modified
