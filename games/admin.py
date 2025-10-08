from django.contrib import admin

from core.admin_mixins import AuditAdminMixin
from cities_light.models import Country, Region, City, SubRegion

from games.form import GameAdminForm
from .models import Game, GameDate, GameImages, Season

admin.site.unregister(Country)
admin.site.unregister(Region)
admin.site.unregister(City)
admin.site.unregister(SubRegion)


class SeasonInline(admin.TabularInline):
    model = Season
    extra = 1
    can_delete = False  # disables hard delete
    fields = ["number", "name", "link", "is_removed"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_removed=False)


class GameDateInline(admin.TabularInline):
    model = GameDate
    extra = 1
    can_delete = False  # disables hard delete
    fields = ["start_date", "end_date", "display_text", "is_removed"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_removed=False)


class GameImagesInline(admin.TabularInline):
    model = GameImages
    extra = 1
    fields = ["image", "description"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_removed=False)


@admin.register(Game)
class GameAdmin(AuditAdminMixin):
    form = GameAdminForm
    inlines = [GameDateInline, SeasonInline, GameImagesInline]
    exclude = ("slug",)

    list_display = (
        "name",
        "game_format",
        "created",
        "created_by",
        "modified",
        "modified_by",
    )
    list_filter = (
        "game_format",
        "created_by",
        "modified_by",
    )
    search_fields = ("name",)
    ordering = ("name",)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for field_name in ["country", "region", "city"]:
            if field_name in form.base_fields:
                form.base_fields[field_name].widget.can_add_related = False
                form.base_fields[field_name].widget.can_change_related = False
                form.base_fields[field_name].widget.can_delete_related = False
                form.base_fields[field_name].widget.can_view_related = False
        return form

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_removed=False)
