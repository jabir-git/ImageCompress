"""Image processing utilities."""

from PIL import Image
import io


def compress_image(
    image: Image.Image, quality: int = 30, max_width: int = 1920, max_height: int = 1080
) -> Image.Image:
    """Aggressively compress image by reducing quality and dimensions."""
    # Resize if dimensions exceed max
    if image.width > max_width or image.height > max_height:
        image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

    return image


def convert_rgba_to_rgb(img: Image.Image, output_format: str) -> Image.Image:
    """Convert RGBA/LA/P images to RGB if needed for output format."""
    if img.mode in ("RGBA", "LA", "P"):
        if output_format.lower() in ["jpg", "jpeg"]:
            rgb_img = Image.new("RGB", img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
            return rgb_img
    return img


def save_image(
    image: Image.Image, output_format: str, quality: int = 85
) -> tuple[io.BytesIO, int]:
    """Save image to BytesIO with specified format."""
    output = io.BytesIO()
    save_format = output_format.upper() if output_format.lower() != "jpg" else "JPEG"

    if save_format in ["JPEG", "JPG"]:
        image.save(output, format="JPEG", quality=quality, optimize=True)
    elif save_format == "WEBP":
        image.save(output, format="WEBP", quality=quality, method=6)
    elif save_format == "PNG":
        image.save(output, format="PNG", optimize=True)
    elif save_format == "GIF":
        image.save(output, format="GIF", optimize=True)
    elif save_format == "BMP":
        image.save(output, format="BMP")
    else:
        raise ValueError(f"Unsupported format: {output_format}")

    output.seek(0)
    return output, output.tell()


def calculate_compression_ratio(original_size: int, compressed_size: int) -> float:
    """Calculate compression ratio as percentage."""
    if original_size == 0:
        return 0.0
    return round((1 - compressed_size / original_size) * 100, 2)
