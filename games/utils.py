from typing import Tuple
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from PIL import Image, ImageOps


def optimize_image(
    image_field: UploadedFile,
    max_size: Tuple[int, int] = (1200, 1200),
    format: str = "WEBP",
    quality: int = 85,
) -> ContentFile:
    """
    Optimizes an image by resizing and converting it to the specified format.
    Returns a ContentFile suitable for saving to an ImageField.

    Args:
        image_field: The image file to optimize
        max_size: Tuple of (width, height) for maximum dimensions
        format: Image format to convert to (default: WEBP)
        quality: Image quality 1-100 (default: 85)

    Returns:
        ContentFile: Optimized image as ContentFile

    Raises:
        ValidationError: If image processing fails
    """
    try:
        img = Image.open(image_field)
        img = ImageOps.exif_transpose(img)  # Correct orientation
        img = ImageOps.contain(
            img, max_size, Image.Resampling.LANCZOS
        )  # Resize, preserve aspect ratio
        buffer = BytesIO()
        img.save(buffer, format=format, quality=quality)
        buffer.seek(0)
        return ContentFile(buffer.read())
    except Exception as e:
        raise ValidationError(
            f"Failed to optimize image: {str(e)}. Please ensure the file is a valid image."
        ) from e
