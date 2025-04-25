from datetime import date
from django.forms import ValidationError
from django.test import TestCase
from .models import Game, GameDate, Season
from django.contrib.auth import get_user_model
from cities_light.models import Country


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
