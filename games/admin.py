from django.contrib import admin

from core.admin_mixins import AuditAdminMixin
from .models import Game, GameDate, Season


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


@admin.register(Game)
class GameAdmin(AuditAdminMixin):
    inlines = [GameDateInline, SeasonInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_removed=False)
