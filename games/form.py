from django import forms
from dal import autocomplete
from .models import Game


class GameFilterForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = "__all__"
        widgets = {
            "country": autocomplete.ModelSelect2(url="country-autocomplete"),
            "region": autocomplete.ModelSelect2(
                url="region-autocomplete",
                forward=["country"],
            ),
            "city": autocomplete.ModelSelect2(
                url="city-autocomplete",
                forward=["region"],
            ),
        }

    class Media:
        js = ("games/js/disable_empty_autocomplete.js",)
