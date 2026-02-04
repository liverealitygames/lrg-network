from .views import game_list, game_detail, map_view, map_data, map_location_games
from django.urls import path
from . import autocomplete

urlpatterns = [
    path(
        "country-autocomplete/",
        autocomplete.CountryAutocomplete.as_view(),
        name="country-autocomplete",
    ),
    path(
        "region-autocomplete/",
        autocomplete.RegionAutocomplete.as_view(),
        name="region-autocomplete",
    ),
    path(
        "city-autocomplete/",
        autocomplete.CityAutocomplete.as_view(),
        name="city-autocomplete",
    ),
    path("map/data/", map_data, name="game_map_data"),
    path("map/games/", map_location_games, name="game_map_location_games"),
    path("map/", map_view, name="game_map"),
    path("", game_list, name="game_list"),
    path("<slug:slug>/", game_detail, name="game_detail"),
]
