from typing import Union
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile
from PIL import Image


def validate_image(file: UploadedFile) -> None:
    # Only check that the file is a valid image and has a supported extension
    try:
        img = Image.open(file)
        img.verify()  # Verify that it's a valid image
    except Exception:
        raise ValidationError("Uploaded file is not a valid image.")

    valid_extensions = ["jpg", "jpeg", "png", "webp"]
    ext = file.name.split(".")[-1].lower()
    if ext not in valid_extensions:
        raise ValidationError(f"Unsupported file extension: {ext}")


def validate_optimized_file_size(
    content_file: ContentFile, max_size: int = 2 * 1024 * 1024
) -> None:
    """
    Checks the size of the optimized ContentFile. Raises ValidationError if too large.
    """
    if content_file.size > max_size:
        raise ValidationError(
            "Optimized image file too large (max 2MB after optimization)."
        )
