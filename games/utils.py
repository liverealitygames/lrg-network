from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image


def optimize_image(image_field, max_size=(1200, 1200), format="WEBP", quality=85):
    """
    Optimizes an image by resizing and converting it to the specified format.
    Returns a ContentFile suitable for saving to an ImageField.
    """
    img = Image.open(image_field)
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    buffer = BytesIO()
    img.save(buffer, format=format, quality=quality)
    buffer.seek(0)
    return ContentFile(buffer.read())
