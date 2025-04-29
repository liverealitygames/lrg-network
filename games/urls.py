from .views import game_list
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
    path("", game_list, name="game_list"),
]
