from django.db import models
from django.utils.translation import gettext_lazy as _
from cities_light.models import Country, Region, City
from smart_selects.db_fields import ChainedForeignKey

class Game(models.Model):
    name = models.CharField(max_length=200)
    class GameFormat(models.TextChoices):
        AMAZING_RACE = 'AR', _('Amazing Race')
        BIG_BROTHER = 'BB', _('Big Brother')
        SURVIVOR = 'SU', _('Survivor')
        TASK_MASTER = 'TM', _('Task Master')
        THE_CHALLENGE = 'CH', _('The Challenge')
        THE_MOLE = 'MO', _('The Mole')
        THE_TRAITORS = 'TR', ('The Traitors')
        ORIGINAL_FORMAT = 'OF', _('Original Format')
        VARIOUS = 'VA', _('Various')
    game_format = models.CharField(max_length=2, choices=GameFormat)
    active = models.BooleanField(null=True)
    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    region = ChainedForeignKey(
        Region,
        chained_field="country",           # field on this model
        chained_model_field="country",     # field on Region model
        show_all=False,
        auto_choose=True,
        sort=True,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )
    city = ChainedForeignKey(
        City,
        chained_field="region",            # field on this model
        chained_model_field="region",      # field on City model
        show_all=False,
        auto_choose=True,
        sort=True,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )
    

