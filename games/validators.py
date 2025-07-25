from django.core.exceptions import ValidationError
from PIL import Image


def validate_image(file):
    max_size = 2 * 1024 * 1024  # 2MB limit
    if file.size > max_size:
        raise ValidationError("Image file too large (max 2MB).")

    try:
        img = Image.open(file)
        img.verify()  # Verify that it's a valid image
    except Exception:
        raise ValidationError("Uploaded file is not a valid image.")

    # Optionally check file extension if you want
    valid_extensions = ["jpg", "jpeg", "png", "webp"]
    ext = file.name.split(".")[-1].lower()
    if ext not in valid_extensions:
        raise ValidationError(f"Unsupported file extension: {ext}")
