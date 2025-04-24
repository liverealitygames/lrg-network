from django.contrib import admin
from .models import Game, GameDate, Season

class SeasonInline(admin.TabularInline):
    model = Season
    extra = 1

class GameDateInline(admin.TabularInline):
    model = GameDate
    extra = 1

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    inlines = [GameDateInline, SeasonInline]