#!/usr/bin/env python3
"""
Optimize images in static/resources/images/ that are larger than 500KB.

This script:
- Converts PNG files to JPEG (better compression for photos)
- Resizes images to max 1200px on the longest side
- Applies 85% JPEG quality for optimal balance of size and quality
- Only processes files larger than 500KB
"""

import os
import sys
import subprocess
from pathlib import Path


def get_file_size(filepath):
    """Get file size in bytes."""
    return os.path.getsize(filepath)


def format_size(size_bytes):
    """Format file size in human-readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f}TB"


def optimize_image(input_path, output_path=None, max_dimension=1200, quality=85):
    """
    Optimize an image using macOS sips command.

    Args:
        input_path: Path to input image
        output_path: Path to output image (if None, overwrites input)
        max_dimension: Maximum width or height in pixels
        quality: JPEG quality (1-100)
    """
    input_path = Path(input_path)

    # Determine output path
    if output_path is None:
        output_path = input_path
    else:
        output_path = Path(output_path)

    try:
        # If PNG, convert to JPEG first
        if input_path.suffix.lower() == ".png":
            jpeg_path = input_path.with_suffix(".jpg")

            # Convert PNG to JPEG
            subprocess.run(
                [
                    "sips",
                    "-s",
                    "format",
                    "jpeg",
                    "-s",
                    "formatOptions",
                    str(quality),
                    str(input_path),
                    "--out",
                    str(jpeg_path),
                ],
                check=True,
                capture_output=True,
            )

            # Resize the JPEG
            subprocess.run(
                ["sips", "-Z", str(max_dimension), str(jpeg_path)],
                check=True,
                capture_output=True,
            )

            # Remove original PNG
            input_path.unlink()
            print(f"  ✓ Converted {input_path.name} → {jpeg_path.name}")
            return str(jpeg_path)

        # For JPEG files, optimize in place
        else:
            # Set quality
            subprocess.run(
                ["sips", "-s", "formatOptions", str(quality), str(input_path)],
                check=True,
                capture_output=True,
            )

            # Resize
            subprocess.run(
                ["sips", "-Z", str(max_dimension), str(input_path)],
                check=True,
                capture_output=True,
            )

            print(f"  ✓ Optimized {input_path.name}")
            return str(input_path)

    except subprocess.CalledProcessError as e:
        print(f"  ✗ Error optimizing {input_path.name}: {e}", file=sys.stderr)
        return None


def main():
    """Main function to optimize images in static/resources/images/."""
    # Define image directory
    script_dir = Path(__file__).parent.parent
    image_dir = script_dir / "static" / "resources" / "images"

    if not image_dir.exists():
        print(f"Error: Image directory not found: {image_dir}", file=sys.stderr)
        sys.exit(1)

    # Find all image files
    image_files = []
    for ext in [".jpg", ".jpeg", ".png"]:
        image_files.extend(image_dir.glob(f"*{ext}"))
        image_files.extend(image_dir.glob(f"*{ext.upper()}"))

    if not image_files:
        print(f"No image files found in {image_dir}")
        return

    print(f"Checking {len(image_files)} image(s) in {image_dir}...")
    print()

    optimized_count = 0
    skipped_count = 0
    error_count = 0

    # Process each image
    for image_path in sorted(image_files):
        size = get_file_size(image_path)
        size_formatted = format_size(size)

        # Only optimize files larger than 500KB
        if size > 512000:  # 500KB in bytes
            print(f"Optimizing {image_path.name} ({size_formatted})...")
            result = optimize_image(image_path)
            if result:
                optimized_count += 1
                new_size = get_file_size(Path(result))
                new_size_formatted = format_size(new_size)
                print(f"  Size: {size_formatted} → {new_size_formatted}")
            else:
                error_count += 1
        else:
            print(f"Skipping {image_path.name} (already optimized: {size_formatted})")
            skipped_count += 1

    print()
    print(
        f"Complete! Optimized: {optimized_count}, Skipped: {skipped_count}, Errors: {error_count}"
    )


if __name__ == "__main__":
    main()
