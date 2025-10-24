from django import template
from django.contrib.staticfiles import finders
from django.contrib.staticfiles.storage import staticfiles_storage

register = template.Library()


@register.filter
def safe_static(path):
    """Return static URL if exists, otherwise blank (avoids manifest errors)."""
    if finders.find(path):
        return staticfiles_storage.url(path)
    return ""
