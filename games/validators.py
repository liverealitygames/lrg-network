from typing import Union
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings
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
    content_file: ContentFile, max_size: int = None
) -> None:
    """
    Checks the size of the optimized ContentFile. Raises ValidationError if too large.

    Args:
        content_file: The ContentFile to check
        max_size: Maximum allowed size in bytes (defaults to IMAGE_MAX_FILE_SIZE setting)
    """
    max_size = max_size or settings.IMAGE_MAX_FILE_SIZE
    if content_file.size > max_size:
        raise ValidationError(
            "Optimized image file too large (max 2MB after optimization)."
        )


def validate_social_handle(value: str, platform: str = "social media") -> None:
    """
    Validates social media handle format.
    Basic validation: no spaces, no special characters that would break URLs.

    Args:
        value: The handle value to validate
        platform: Name of the platform for error messages

    Raises:
        ValidationError: If handle contains invalid characters
    """
    if not value:
        return

    # Check for spaces (not allowed in handles)
    if " " in value:
        raise ValidationError(f"{platform} handle cannot contain spaces.")

    # Check for characters that would break URL construction
    invalid_chars = ["/", "\\", "?", "#", "@"]
    for char in invalid_chars:
        if char in value:
            raise ValidationError(
                f"{platform} handle cannot contain '{char}'. "
                f"Enter just the handle/username without the full URL."
            )
