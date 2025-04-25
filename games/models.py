from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from cities_light.models import Country, Region, City

from core.models import CoreModel


class Game(CoreModel):
    name = models.CharField(max_length=200)

    class GameFormat(models.TextChoices):
        AMAZING_RACE = "AR", _("Amazing Race")
        BIG_BROTHER = "BB", _("Big Brother")
        SURVIVOR = "SU", _("Survivor")
        TASK_MASTER = "TM", _("Task Master")
        THE_CHALLENGE = "CH", _("The Challenge")
        THE_MOLE = "MO", _("The Mole")
        THE_TRAITORS = "TR", ("The Traitors")
        ORIGINAL_FORMAT = "OF", _("Original Format")
        VARIOUS = "VA", _("Various")

    game_format = models.CharField(max_length=2, choices=GameFormat)
    active = models.BooleanField(null=True)
    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    region = models.ForeignKey(Region, blank=True, null=True, on_delete=models.PROTECT)
    city = models.ForeignKey(City, blank=True, null=True, on_delete=models.PROTECT)

    class GameDuration(models.TextChoices):
        SINGLE_DAY = "SD", _("Single Day")
        MULTIPLE_DAYS = "MD", _("Multiple Days")
        SEMESTER = "SE", _("Semester")

    game_duration = models.CharField(
        max_length=2, choices=GameDuration.choices, blank=True, null=True
    )
    number_of_days = models.IntegerField(
        blank=True, null=True, validators=[MinValueValidator(1), MaxValueValidator(100)]
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
    # Eventually we'll may want to connect this to a user, but starting with just a string field for host(s)
    host = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    instagram_hanlde = models.CharField(max_length=200, blank=True, null=True)
    facebook_link = models.CharField(max_length=200, blank=True, null=True)
    youtube_link = models.CharField(max_length=200, blank=True, null=True)
    lrg_wiki_page = models.CharField(max_length=200, blank=True, null=True)
    casting_link = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name}"


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


class Season(CoreModel):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="seasons")
    number = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    name = models.CharField(max_length=200, blank=True, null=True)
    link = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.game.name} - Season {self.number} ({self.name})"
