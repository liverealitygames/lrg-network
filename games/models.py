from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.forms import ValidationError
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from cities_light.models import Country, Region, City
from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image

from lrgnetwork.storage_backends import MediaStorage
from .validators import validate_image, validate_optimized_file_size
from .utils import optimize_image

from core.models import CoreModel


class Game(CoreModel):
    name = models.CharField(max_length=200)
    logo = models.ImageField(
        upload_to="game_logos/",
        storage=MediaStorage,
        validators=[validate_image],
        blank=True,
        null=True,
    )
    slug = models.SlugField(blank=True, db_index=True)

    class GameFormat(models.TextChoices):
        AMAZING_RACE = "AR", _("Amazing Race")
        BIG_BROTHER = "BB", _("Big Brother")
        SURVIVOR = "SU", _("Survivor")
        TASK_MASTER = "TM", _("Task Master")
        THE_CHALLENGE = "CH", _("The Challenge")
        THE_GENIUS = "GE", _("The Genius")
        THE_MOLE = "MO", _("The Mole")
        THE_TRAITORS = "TR", ("The Traitors")
        ORIGINAL_FORMAT = "OF", _("Original Format")
        VARIOUS_FORMATS = "VF", _("Various Formats")

    game_format = models.CharField(max_length=2, choices=GameFormat, db_index=True)
    active = models.BooleanField(null=True, db_index=True)
    country = models.ForeignKey(Country, on_delete=models.PROTECT, db_index=True)
    region = models.ForeignKey(
        Region, blank=True, null=True, on_delete=models.PROTECT, db_index=True
    )
    city = models.ForeignKey(
        City, blank=True, null=True, on_delete=models.PROTECT, db_index=True
    )

    class GameDuration(models.TextChoices):
        SINGLE_DAY = "SD", _("Single Day")
        MULTIPLE_DAYS = "MD", _("Multiple Days")
        SEMESTER = "SE", _("Semester")

    game_duration = models.CharField(
        max_length=2, choices=GameDuration.choices, blank=True, null=True
    )

    class FilmingStatus(models.TextChoices):
        FILMED = "FI", _("Filmed")
        NOT_FILMED = "NF", _("Not Filmed")
        EPISODES = "EP", _("Episodes")
        LIVESTREAMED = "LI", _("Livestreamed")

    filming_status = models.CharField(
        max_length=2, choices=FilmingStatus.choices, blank=True, null=True
    )
    for_charity = models.BooleanField(null=True)
    friends_and_family = models.BooleanField(null=True)
    college_game = models.BooleanField(null=True)
    college_name = models.CharField(max_length=200, blank=True, null=True)
    # Eventually we may want to connect this to a user, but starting with just a string field for host(s)
    host = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    instagram_handle = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Enter just the handle (e.g. www.instagram.com/<b>handle</b>)",
    )
    facebook_link = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Enter just the page name (e.g. www.facebook.com/<b>pagename</b>)",
    )
    youtube_link = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Enter any valid youtube path (e.g. www.youtube.com/<b>channelname</b>)",
    )
    lrg_wiki_page = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Enter just the page name (e.g. https://live-reality-games.fandom.com/wiki/<b>Page_Name</b>)",
    )
    discord_link = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Enter just the part after discord.gg/ (e.g. https://discord.gg/<b>invitecode</b>)",
    )
    tiktok_handle = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Enter just the username (e.g. https://www.tiktok.com/@<b>username</b>)",
    )
    casting_link = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Game"
        verbose_name_plural = "Games"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["slug"],
                condition=models.Q(is_removed=False),
                name="unique_slug_for_active_games",
            )
        ]

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        """
        Generate a unique slug by finding the next available number suffix.
        More efficient than looping - uses a single query to find all existing slugs.
        """
        import re
        import uuid

        base_slug = slugify(self.name)

        # If slug is already set and name hasn't changed, keep it
        if self.pk and self.slug:
            try:
                existing = Game.objects.get(pk=self.pk)
                if existing.name == self.name and existing.slug:
                    # Name unchanged, keep existing slug
                    super().save(*args, **kwargs)
                    return
            except Game.DoesNotExist:
                pass

        # Get all existing slugs that match the base pattern (excluding current instance)
        # This single query gets all slugs that start with base_slug or base_slug-N
        existing_slugs = set(
            Game.objects.filter(slug__startswith=base_slug, is_removed=False)
            .exclude(pk=self.pk)
            .values_list("slug", flat=True)
        )

        # If base slug is available, use it
        if base_slug not in existing_slugs:
            self.slug = base_slug
        else:
            # Extract all used numbers from existing slugs
            # Pattern matches: base_slug or base_slug-123
            pattern = re.compile(rf"^{re.escape(base_slug)}(?:-(\d+))?$")
            used_numbers = set()

            for existing_slug in existing_slugs:
                match = pattern.match(existing_slug)
                if match:
                    number_str = match.group(1)
                    if number_str:
                        try:
                            used_numbers.add(int(number_str))
                        except ValueError:
                            # Skip invalid numbers
                            continue

            # Find the first available number
            counter = 1
            while counter in used_numbers:
                counter += 1

            # Safety check: if we somehow get a very high number, use UUID fallback
            if counter > 1000:
                self.slug = f"{base_slug}-{uuid.uuid4().hex[:8]}"
            else:
                self.slug = f"{base_slug}-{counter}"

        if self.logo:
            try:
                optimized = optimize_image(self.logo)
                validate_optimized_file_size(optimized)
                self.logo.save(self.logo.name, optimized, save=False)
            except ValidationError:
                # Re-raise validation errors as-is (they already have good messages)
                raise
            except Exception as e:
                raise ValidationError(
                    f"Unexpected error processing logo for {self.name}: {str(e)}"
                ) from e

        super().save(*args, **kwargs)

    def location_display(self):
        city_name = self.city.name if self.city else None
        region_part = self.region.name if self.region else None

        # If we have a city, we won't use the country. If we have a region, but no city
        # we'll use the ISO country code. If we just have a country we'll use the full name
        if city_name:
            country_part = None
        elif region_part and self.country:
            country_part = (
                self.country.code2 if self.country.code2 else self.country.name
            )
        else:
            country_part = self.country.name

        # Combine parts, prioritizing city, then region, then country
        parts = [city_name, region_part, country_part]
        return ", ".join(part for part in parts if part)

    def get_default_logo_url(self):
        """
        Get the URL for the default logo based on game format.
        Returns None if no default logo exists.
        """
        from django.contrib.staticfiles import finders
        from django.contrib.staticfiles.storage import staticfiles_storage

        logo_path = f"games/images/default_logos/{self.game_format.lower()}.png"
        if finders.find(logo_path):
            return staticfiles_storage.url(logo_path)
        return None


class GameDate(CoreModel):
    game = models.ForeignKey(
        Game, on_delete=models.CASCADE, related_name="next_season_date"
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    display_text = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional custom label like 'Fall 2025' or 'August 2025'. Overrides automatic display.",
    )

    def __str__(self):
        if self.display_text:
            return self.display_text
        elif self.start_date and self.end_date:
            if self.start_date == self.end_date:
                return self.start_date.strftime("%B %d, %Y")
            elif self.start_date.month == self.end_date.month:
                return f"{self.start_date.strftime('%B %d')}–{self.end_date.strftime('%d, %Y')}"
            elif self.start_date.year == self.end_date.year:
                return f"{self.start_date.strftime('%B %d')} – {self.end_date.strftime('%B %d, %Y')}"
            else:
                return f"{self.start_date.strftime('%B %d, %Y')} – {self.end_date.strftime('%B %d, %Y')}"
        elif self.start_date:
            return self.start_date.strftime("%B %d, %Y")
        return "TBD"

    class Meta:
        verbose_name = "Game Date"
        verbose_name_plural = "Game Dates"
        ordering = ["-start_date", "-end_date"]


class GameImages(CoreModel):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(
        upload_to="game_images/", storage=MediaStorage, validators=[validate_image]
    )
    description = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.description if self.description else f"Image for {self.game.name}"

    def save(self, *args, **kwargs):
        if self.image:
            try:
                optimized = optimize_image(self.image)
                validate_optimized_file_size(optimized)
                self.image.save(self.image.name, optimized, save=False)
            except ValidationError:
                # Re-raise validation errors as-is (they already have good messages)
                raise
            except Exception as e:
                game_name = self.game.name if self.game else "unknown game"
                raise ValidationError(
                    f"Unexpected error processing image for {game_name}: {str(e)}"
                ) from e

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Game Image"
        verbose_name_plural = "Game Images"
        ordering = ["game", "created"]


class Season(CoreModel):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="seasons")
    number = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    name = models.CharField(max_length=200, blank=True, null=True)
    link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name if self.name else f"Season {self.number}"

    class Meta:
        verbose_name = "Season"
        verbose_name_plural = "Seasons"
        ordering = ["game", "number"]
