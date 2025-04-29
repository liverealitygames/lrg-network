from django import forms
from django.contrib import admin


class AuditAdminMixin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.modified_by = request.user
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        # Show as read-only only when editing
        if obj:
            return getattr(self, "readonly_fields", ()) + ("created_by", "modified_by")
        return getattr(self, "readonly_fields", ())

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if not obj:  # Creating → hide the fields
            for field in ("created_by", "modified_by"):
                if field in form.base_fields:
                    form.base_fields[field].widget = forms.HiddenInput()
                    form.base_fields[field].required = False

        return form
