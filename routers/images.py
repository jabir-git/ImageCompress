"""Image processing routes."""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from PIL import Image
import io
import json

from utils import (
    compress_image,
    convert_rgba_to_rgb,
    save_image,
    calculate_compression_ratio,
)

router = APIRouter(prefix="/api", tags=["images"])


@router.post("/compress")
async def compress_image_endpoint(
    file: UploadFile = File(...),
    quality: int = 30,
    max_width: int = 1920,
    max_height: int = 1080,
    output_format: str = "webp",
):
    """Compress image with aggressive settings and return as binary."""
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Read and open image
        contents = await file.read()
        img = Image.open(io.BytesIO(contents))

        # Convert RGBA to RGB if necessary
        img = convert_rgba_to_rgb(img, output_format)

        # Compress
        img = compress_image(img, quality, max_width, max_height)

        # Save to bytes
        output, _ = save_image(img, output_format, quality)
        compressed_data = output.getvalue()

        # Calculate compression ratio
        original_size = len(contents)
        compressed_size = len(compressed_data)
        ratio = calculate_compression_ratio(original_size, compressed_size)

        # Prepare response with metadata in header
        response = StreamingResponse(
            io.BytesIO(compressed_data), media_type="image/" + output_format
        )
        response.headers["X-Original-Size"] = str(original_size)
        response.headers["X-Compressed-Size"] = str(compressed_size)
        response.headers["X-Compression-Ratio"] = str(ratio)
        response.headers["X-File-Data"] = json.dumps(
            {
                "original_size": original_size,
                "compressed_size": compressed_size,
                "compression_ratio": ratio,
            }
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/convert")
async def convert_image_endpoint(
    file: UploadFile = File(...), output_format: str = "webp"
):
    """Convert image between formats and return as binary."""
    try:
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")

        contents = await file.read()
        img = Image.open(io.BytesIO(contents))

        # Convert RGBA to RGB if necessary
        img = convert_rgba_to_rgb(img, output_format)

        # Save to bytes
        output, _ = save_image(img, output_format)
        converted_data = output.getvalue()

        response = StreamingResponse(
            io.BytesIO(converted_data), media_type="image/" + output_format
        )
        response.headers["X-File-Data"] = json.dumps(
            {
                "message": f"Successfully converted to {output_format.upper()}",
                "format": output_format.upper(),
            }
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compress-and-convert")
async def compress_and_convert(
    file: UploadFile = File(...), quality: int = 30, output_format: str = "webp"
):
    """Compress and convert image in one operation and return as binary."""
    try:
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")

        contents = await file.read()
        img = Image.open(io.BytesIO(contents))

        # Convert RGBA to RGB if necessary
        img = convert_rgba_to_rgb(img, output_format)

        # Compress
        img = compress_image(img, quality)

        # Save to bytes
        output, _ = save_image(img, output_format, quality)
        compressed_data = output.getvalue()

        # Calculate compression ratio
        original_size = len(contents)
        compressed_size = len(compressed_data)
        ratio = calculate_compression_ratio(original_size, compressed_size)

        response = StreamingResponse(
            io.BytesIO(compressed_data), media_type="image/" + output_format
        )
        response.headers["X-File-Data"] = json.dumps(
            {
                "original_size": original_size,
                "compressed_size": compressed_size,
                "compression_ratio": ratio,
                "format": output_format.upper(),
            }
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
