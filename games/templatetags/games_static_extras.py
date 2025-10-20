from django import template
from django.contrib.staticfiles import finders

register = template.Library()


@register.filter
def has_static_file(path):
    """
    Returns True if the static file exists, False otherwise.
    """
    return bool(finders.find(path))
