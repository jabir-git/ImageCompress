"""Image processing utilities for compression and format conversion."""

from PIL import Image
import io

# Default image processing settings
DEFAULT_QUALITY = 85
# "Maximum compression" for lossy formats (lower = smaller file)
DEFAULT_COMPRESS_QUALITY = 1
DEFAULT_MAX_WIDTH = 1920
DEFAULT_MAX_HEIGHT = 1080


def compress_image(
    image: Image.Image,
    quality: int = DEFAULT_COMPRESS_QUALITY,
    max_width: int = DEFAULT_MAX_WIDTH,
    max_height: int = DEFAULT_MAX_HEIGHT,
) -> Image.Image:
    """
    Compress image by reducing dimensions if necessary.

    Args:
        image: PIL Image object
        quality: Compression quality (1-100)
        max_width: Maximum width in pixels
        max_height: Maximum height in pixels

    Returns:
        Compressed PIL Image object
    """
    if image.width > max_width or image.height > max_height:
        image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
    return image


def convert_rgba_to_rgb(img: Image.Image, output_format: str) -> Image.Image:
    """
    Convert RGBA/LA/P images to RGB if needed for output format.

    Args:
        img: PIL Image object
        output_format: Target image format (jpg, webp, etc.)

    Returns:
        Converted PIL Image object or original if conversion not needed
    """
    if img.mode in ("RGBA", "LA", "P"):
        if output_format.lower() in ["jpg", "jpeg"]:
            rgb_img = Image.new("RGB", img.size, (255, 255, 255))
            mask = img.split()[-1] if img.mode == "RGBA" else None
            rgb_img.paste(img, mask=mask)
            return rgb_img
    return img


def save_image(
    image: Image.Image, output_format: str, quality: int = DEFAULT_QUALITY
) -> tuple[io.BytesIO, int]:
    """
    Save image to BytesIO buffer with specified format and quality.

    Args:
        image: PIL Image object
        output_format: Output image format (jpg, webp, png, gif, bmp)
        quality: Image quality (1-100) for lossy formats

    Returns:
        Tuple of (BytesIO buffer, final position)

    Raises:
        ValueError: If format is not supported
    """
    output = io.BytesIO()
    save_format = output_format.upper() if output_format.lower() != "jpg" else "JPEG"

    safe_quality = max(1, min(int(quality), 100))

    format_config = {
        "JPEG": {
            "format": "JPEG",
            "quality": safe_quality,
            "optimize": True,
            "progressive": True,
            "subsampling": 2,
        },
        "JPG": {
            "format": "JPEG",
            "quality": safe_quality,
            "optimize": True,
            "progressive": True,
            "subsampling": 2,
        },
        "WEBP": {
            "format": "WEBP",
            "quality": safe_quality,
            "method": 6,
        },
        "PNG": {"format": "PNG", "optimize": True, "compress_level": 9},
        "GIF": {"format": "GIF", "optimize": True},
        "BMP": {"format": "BMP"},
    }

    if save_format not in format_config:
        raise ValueError(f"Unsupported format: {output_format}")

    config = format_config[save_format]
    save_kwargs = {k: v for k, v in config.items() if k != "format"}
    image.save(output, format=config["format"], **save_kwargs)

    output.seek(0)
    return output, output.tell()


def calculate_compression_ratio(original_size: int, compressed_size: int) -> float:
    """
    Calculate compression ratio as a percentage.

    Args:
        original_size: Original file size in bytes
        compressed_size: Compressed file size in bytes

    Returns:
        Compression ratio as percentage (0-100)
    """
    if original_size == 0:
        return 0.0
    return round((1 - compressed_size / original_size) * 100, 2)
