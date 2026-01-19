from django import forms
from dal import autocomplete
from .models import Game
from .validators import validate_social_handle


class GameAdminForm(forms.ModelForm):
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

    def clean_instagram_handle(self):
        value = self.cleaned_data.get("instagram_handle")
        if value:
            validate_social_handle(value, "Instagram")
        return value

    def clean_facebook_link(self):
        value = self.cleaned_data.get("facebook_link")
        if value:
            validate_social_handle(value, "Facebook")
        return value

    def clean_youtube_link(self):
        value = self.cleaned_data.get("youtube_link")
        return value

    def clean_lrg_wiki_page(self):
        value = self.cleaned_data.get("lrg_wiki_page")
        if value:
            validate_social_handle(value, "LRG Wiki")
        return value

    def clean_discord_link(self):
        value = self.cleaned_data.get("discord_link")
        if value:
            validate_social_handle(value, "Discord")
        return value

    def clean_tiktok_handle(self):
        value = self.cleaned_data.get("tiktok_handle")
        if value:
            validate_social_handle(value, "TikTok")
        return value
