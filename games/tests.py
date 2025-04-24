from datetime import date
from django.forms import ValidationError
from django.test import TestCase
from .models import Game, GameDate, Season
from cities_light.models import Country


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
