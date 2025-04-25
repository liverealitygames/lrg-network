from django import forms
from django.contrib import admin


class AuditAdminMixin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.modified_by = request.user
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if obj:  # Editing → show as read-only
            self.readonly_fields = getattr(self, "readonly_fields", ()) + (
                "created_by",
                "modified_by",
            )
        else:  # Creating → hide the fields
            for field in ("created_by", "modified_by"):
                if field in form.base_fields:
                    form.base_fields[field].widget = forms.HiddenInput()
                    form.base_fields[field].required = False

        return form
