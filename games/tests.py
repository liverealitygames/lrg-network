from datetime import date
from django.forms import ValidationError
from django.test import TestCase
from django.urls import reverse
from .models import Game, GameDate, Season
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
        game = Game.objects.create(
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
        self.assertEqual(game.location_display(), "Los Angeles, CA, US")

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
        self.season = Season.objects.create(
            game=self.game,
            number=1,
            name="Borneo",
            link="http://example.com",
        )

    def test_season(self):
        self.season.full_clean()
        self.assertEqual(self.season.number, 1)
        self.assertEqual(self.season.name, "Borneo")
        self.assertEqual(self.season.link, "http://example.com")
        self.assertEqual(str(self.season), "Test Game - Season 1 (Borneo)")


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

    def test_view_returns_all_games(self):
        response = self.client.get(reverse("game_list"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.game1, response.context["games"])
        self.assertIn(self.game2, response.context["games"])

    def test_view_handles_no_games(self):
        Game.objects.all().delete()  # Remove all games
        response = self.client.get(reverse("game_list"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context["games"], [])
