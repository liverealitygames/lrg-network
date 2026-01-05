from datetime import date
from django.forms import ValidationError
from django.test import TestCase
from django.urls import reverse
from .models import Game, GameDate, Season
from .form import GameAdminForm
from django.contrib.auth import get_user_model
from cities_light.models import Country, Region, City


class CoreModelFieldsTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = get_user_model().objects.create_user(
            username="testuser", password="password"
        )

        # Create a Country instance for testing
        self.country = Country.objects.create(name="Test Country")

    def test_created_by_and_modified_by(self):
        # Create a Game instance with created_by and modified_by
        game = Game.objects.create(
            name="Test Game",
            game_format=Game.GameFormat.AMAZING_RACE,
            active=True,
            country=self.country,
            created_by=self.user,
            modified_by=self.user,
        )

        # Validate the created_by and modified_by fields
        self.assertEqual(game.created_by, self.user)
        self.assertEqual(game.modified_by, self.user)

    def test_auto_populated_timestamps(self):
        # Create a Game instance
        game = Game.objects.create(
            name="Test Game",
            game_format=Game.GameFormat.SURVIVOR,
            active=True,
            country=self.country,
            created_by=self.user,
        )

        # Initially, created and modified should be the same
        self.assertEqual(game.created, game.modified)

        # Update the Game instance
        game.name = "Updated Test Game"
        game.save()

        # Reload the instance from the database to get updated timestamps
        game.refresh_from_db()

        # Assert that created and modified are now different
        self.assertNotEqual(game.created, game.modified)
        self.assertEqual(game.name, "Updated Test Game")

    def test_soft_delete(self):
        # Create a Game instance
        game = Game.objects.create(
            name="Test Game",
            game_format=Game.GameFormat.THE_MOLE,
            active=True,
            country=self.country,
            created_by=self.user,
        )

        # Soft delete the instance
        game.delete()

        # Validate that the instance is marked as removed
        self.assertTrue(game.is_removed)

        # Validate that the instance is excluded from the default queryset
        self.assertEqual(Game.objects.filter(is_removed=False).count(), 0)


class GameModelTest(TestCase):
    def setUp(self):
        # Create a Country instance for testing
        self.country = Country.objects.create(name="Test Country")

        # Create a Game instance

    def test_basic_game(self):
        game = self.game = Game.objects.create(
            name="Test Game",
            game_format=Game.GameFormat.AMAZING_RACE,
            active=True,
            country=self.country,
            for_charity=False,
            friends_and_family=False,
            college_game=False,
        )
        game.full_clean()
        self.assertEqual(self.game.name, "Test Game")
        self.assertEqual(self.game.game_format, Game.GameFormat.AMAZING_RACE)
        self.assertTrue(self.game.active)
        self.assertEqual(str(self.game), "Test Game")

    def test_invalid_game_format(self):
        game = Game(
            name="Invalid Game",
            game_format="INVALID_FORMAT",  # Invalid format
            active=True,
            country=self.country,
            for_charity=False,
            friends_and_family=False,
            college_game=False,
        )
        with self.assertRaises(ValidationError):
            game.full_clean()  # This will raise a ValidationError for invalid choices


class GameDateModelTest(TestCase):
    def setUp(self):
        self.game = Game.objects.create(
            name="Test Game",
            game_format=Game.GameFormat.SURVIVOR,
            active=True,
            country=Country.objects.create(name="Test Country"),
        )

    def test_single_date(self):
        game_date = self.game_date = GameDate.objects.create(
            game=self.game,
            start_date=date(2025, 4, 1),
        )
        game_date.full_clean()
        self.assertEqual(self.game_date.start_date.strftime("%Y-%m-%d"), "2025-04-01")
        self.assertEqual(str(self.game_date), "April 01, 2025")

    def test_date_range(self):
        game_date = self.game_date = GameDate.objects.create(
            game=self.game,
            start_date=date(2025, 4, 1),
            end_date=date(2025, 4, 5),
        )
        game_date.full_clean()
        self.assertEqual(self.game_date.start_date.strftime("%Y-%m-%d"), "2025-04-01")
        self.assertEqual(self.game_date.end_date.strftime("%Y-%m-%d"), "2025-04-05")
        self.assertEqual(str(self.game_date), "April 01–05, 2025")

    def test_generic_timeframe(self):
        game_date = self.game_date = GameDate.objects.create(
            game=self.game,
            display_text="Spring 2025",
        )
        game_date.full_clean()
        self.assertEqual(self.game_date.display_text, "Spring 2025")
        self.assertEqual(str(self.game_date), "Spring 2025")


class GameLocationDisplayTests(TestCase):
    def setUp(self):
        self.country = Country.objects.create(name="United States", code2="US")
        self.region = Region.objects.create(
            name="California", geoname_code="CA", country=self.country
        )
        self.city = City.objects.create(
            name="Los Angeles", region=self.region, country=self.country
        )

    def test_location_display_with_city_region_country(self):
        game = Game.objects.create(
            name="Test Game", country=self.country, region=self.region, city=self.city
        )
        self.assertEqual(game.location_display(), "Los Angeles, California")

    def test_location_display_with_region_country(self):
        game = Game.objects.create(
            name="Test Game", country=self.country, region=self.region
        )
        self.assertEqual(game.location_display(), "California, US")

    def test_location_display_with_country_only(self):
        game = Game.objects.create(name="Test Game", country=self.country)
        self.assertEqual(game.location_display(), "United States")


class SeasonModelTest(TestCase):
    def setUp(self):
        self.game = Game.objects.create(
            name="Test Game",
            game_format=Game.GameFormat.THE_MOLE,
            active=True,
            country=Country.objects.create(name="Test Country"),
        )

    def test_season(self):
        self.season = Season.objects.create(
            game=self.game,
            number=1,
            name="Borneo",
            link="http://example.com",
        )
        self.assertEqual(self.season.number, 1)
        self.assertEqual(self.season.name, "Borneo")
        self.assertEqual(self.season.link, "http://example.com")
        self.assertEqual(str(self.season), "Borneo")

    def test_season_no_name(self):
        self.season = Season.objects.create(
            game=self.game,
            number=1,
        )
        self.assertEqual(str(self.season), "Season 1")


class GameListViewTest(TestCase):
    def setUp(self):
        # Create a Country instance for testing
        self.country = Country.objects.create(name="Test Country")

        # Create some Game instances
        self.game1 = Game.objects.create(
            name="Game 1",
            game_format=Game.GameFormat.AMAZING_RACE,
            active=True,
            country=self.country,
        )
        self.game2 = Game.objects.create(
            name="Game 2",
            game_format=Game.GameFormat.SURVIVOR,
            active=True,
            country=self.country,
        )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get("/games/")
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse("game_list"))
        self.assertTemplateUsed(response, "games/game_list.html")

    def test_view_returns_paginated_games(self):
        # Create additional games to exceed the pagination limit
        for i in range(10):
            Game.objects.create(
                name=f"Game {i + 3}",
                game_format=Game.GameFormat.AMAZING_RACE,
                active=True,
                country=self.country,
            )

        response = self.client.get(reverse("game_list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["page_obj"]), 10)
        self.assertIn(self.game1, response.context["page_obj"])
        self.assertIn(self.game2, response.context["page_obj"])

    def test_view_handles_no_games(self):
        Game.objects.all().delete()  # Remove all games
        response = self.client.get(reverse("game_list"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context["page_obj"], [])

    def test_view_handles_second_page(self):
        # Create additional games to exceed the pagination limit
        for i in range(15):
            Game.objects.create(
                name=f"Game {i + 3}",
                game_format=Game.GameFormat.AMAZING_RACE,
                active=True,
                country=self.country,
            )

        response = self.client.get(reverse("game_list") + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertGreater(
            len(response.context["page_obj"]), 0
        )  # Ensure second page has games

    def test_filters_work_and_persist_across_pages(self):
        # Create games with different formats and active/inactive status
        for i in range(15):
            Game.objects.create(
                name=f"Active Race {i}",
                game_format=Game.GameFormat.AMAZING_RACE,
                active=True,
                country=self.country,
            )
        for i in range(5):
            Game.objects.create(
                name=f"Inactive Survivor {i}",
                game_format=Game.GameFormat.SURVIVOR,
                active=False,
                country=self.country,
            )
        # Filter by game_format (AMAZING_RACE) and check page 1
        response = self.client.get(reverse("game_list") + "?game_format=amazing_race")
        self.assertEqual(response.status_code, 200)
        for game in response.context["page_obj"]:
            self.assertEqual(game.game_format, Game.GameFormat.AMAZING_RACE)
            self.assertTrue(game.active)
        # Go to page 2 with same filter
        response2 = self.client.get(
            reverse("game_list") + "?game_format=amazing_race&page=2"
        )
        self.assertEqual(response2.status_code, 200)
        for game in response2.context["page_obj"]:
            self.assertEqual(game.game_format, Game.GameFormat.AMAZING_RACE)
            self.assertTrue(game.active)
        # Filter by inactive games (include_inactive)
        # Collect all games across all pages
        all_names = []
        page = 1
        while True:
            resp = self.client.get(
                reverse("game_list") + f"?include_inactive=on&page={page}"
            )
            self.assertEqual(resp.status_code, 200)
            page_games = [game.name for game in resp.context["page_obj"]]
            all_names.extend(page_games)
            if not resp.context["page_obj"].has_next():
                break
            page += 1
        self.assertIn("Inactive Survivor 0", all_names)
        self.assertIn("Active Race 0", all_names)
        # Filter by search query
        response4 = self.client.get(reverse("game_list") + "?q=Inactive")
        self.assertEqual(response4.status_code, 200)
        for game in response4.context["page_obj"]:
            self.assertIn("Inactive", game.name)


class GameDetailViewTest(TestCase):
    def setUp(self):
        self.country = Country.objects.create(name="Test Country")
        self.game = Game.objects.create(
            name="Test Game Detail",
            game_format=Game.GameFormat.SURVIVOR,
            active=True,
            country=self.country,
        )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(f"/games/{self.game.slug}/")
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse("game_detail", args=[self.game.slug]))
        self.assertTemplateUsed(response, "games/game_detail.html")

    def test_view_returns_404_for_invalid_slug(self):
        response = self.client.get("/games/invalid-slug-12345/")
        self.assertEqual(response.status_code, 404)

    def test_view_context_contains_game(self):
        response = self.client.get(reverse("game_detail", args=[self.game.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertIn("game", response.context)
        self.assertEqual(response.context["game"], self.game)


class SocialMediaValidationTest(TestCase):
    def setUp(self):
        self.country = Country.objects.create(name="Test Country")
        self.game = Game.objects.create(
            name="Test Game",
            game_format=Game.GameFormat.AMAZING_RACE,
            active=True,
            country=self.country,
            for_charity=False,
            friends_and_family=False,
            college_game=False,
        )

    def test_valid_instagram_handle(self):
        """Test that valid Instagram handles are accepted."""
        form = GameAdminForm(
            {
                "name": "Test Game",
                "game_format": Game.GameFormat.AMAZING_RACE,
                "active": True,
                "country": self.country.id,
                "for_charity": False,
                "friends_and_family": False,
                "college_game": False,
                "instagram_handle": "testhandle",
            },
            instance=self.game,
        )
        self.assertTrue(form.is_valid())
        game = form.save()
        self.assertEqual(game.instagram_handle, "testhandle")

    def test_invalid_instagram_handle_with_space(self):
        """Test that handles with spaces are rejected."""
        form = GameAdminForm(
            {
                "name": "Test Game",
                "game_format": Game.GameFormat.AMAZING_RACE,
                "active": True,
                "country": self.country.id,
                "for_charity": False,
                "friends_and_family": False,
                "college_game": False,
                "instagram_handle": "test handle",
            },
            instance=self.game,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("instagram_handle", form.errors)

    def test_invalid_instagram_handle_with_slash(self):
        """Test that handles with slashes are rejected."""
        form = GameAdminForm(
            {
                "name": "Test Game",
                "game_format": Game.GameFormat.AMAZING_RACE,
                "active": True,
                "country": self.country.id,
                "for_charity": False,
                "friends_and_family": False,
                "college_game": False,
                "instagram_handle": "test/handle",
            },
            instance=self.game,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("instagram_handle", form.errors)

    def test_valid_tiktok_handle(self):
        """Test that valid TikTok handles are accepted."""
        form = GameAdminForm(
            {
                "name": "Test Game",
                "game_format": Game.GameFormat.AMAZING_RACE,
                "active": True,
                "country": self.country.id,
                "for_charity": False,
                "friends_and_family": False,
                "college_game": False,
                "tiktok_handle": "username123",
            },
            instance=self.game,
        )
        self.assertTrue(form.is_valid())
        game = form.save()
        self.assertEqual(game.tiktok_handle, "username123")

    def test_empty_handles_allowed(self):
        """Test that empty handles are allowed (blank=True)."""
        form = GameAdminForm(
            {
                "name": "Test Game",
                "game_format": Game.GameFormat.AMAZING_RACE,
                "active": True,
                "country": self.country.id,
                "for_charity": False,
                "friends_and_family": False,
                "college_game": False,
                "instagram_handle": "",
                "tiktok_handle": "",
            },
            instance=self.game,
        )
        self.assertTrue(form.is_valid())
        game = form.save()
        self.assertEqual(game.instagram_handle, "")
        self.assertEqual(game.tiktok_handle, "")


class GameSlugGenerationTest(TestCase):
    def setUp(self):
        self.country = Country.objects.create(name="Test Country")

    def test_unique_slug_generation(self):
        """Test that slugs are generated correctly for new games."""
        game1 = Game.objects.create(
            name="Test Game",
            game_format=Game.GameFormat.SURVIVOR,
            active=True,
            country=self.country,
        )
        self.assertEqual(game1.slug, "test-game")

        game2 = Game.objects.create(
            name="Test Game",
            game_format=Game.GameFormat.SURVIVOR,
            active=True,
            country=self.country,
        )
        self.assertEqual(game2.slug, "test-game-1")

    def test_slug_preserved_on_name_unchanged(self):
        """Test that slug is preserved when name doesn't change."""
        game = Game.objects.create(
            name="Original Name",
            game_format=Game.GameFormat.SURVIVOR,
            active=True,
            country=self.country,
        )
        original_slug = game.slug
        game.description = "Updated description"
        game.save()
        game.refresh_from_db()
        self.assertEqual(game.slug, original_slug)
