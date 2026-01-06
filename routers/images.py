"""Image processing routes."""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from PIL import Image
import io
import json
import zipfile
import tempfile
import os

from utils import (
    compress_image,
    convert_rgba_to_rgb,
    DEFAULT_COMPRESS_QUALITY,
    save_image,
    calculate_compression_ratio,
)

router = APIRouter(prefix="/api", tags=["images"])

# Constants
MAX_FILES = 100
TEMP_SUFFIX = ".zip"
ZIP_COMPRESSION = zipfile.ZIP_DEFLATED


def validate_file(file: UploadFile) -> bool:
    """Validate if file is an image."""
    return file.content_type and file.content_type.startswith("image/")


def get_output_filename(input_filename: str, output_format: str) -> str:
    """Generate output filename with new extension."""
    name_without_ext = os.path.splitext(input_filename)[0]
    return f"{name_without_ext}.{output_format}"


def create_response_headers(data: dict) -> dict:
    """Create response headers with metadata."""
    return {"X-File-Data": json.dumps(data)}


def process_single_image(
    image_bytes: bytes,
    output_format: str,
    quality: int = DEFAULT_COMPRESS_QUALITY,
) -> tuple[bytes, dict]:
    """Process a single image and return processed data with metadata."""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img = convert_rgba_to_rgb(img, output_format)
        output, _ = save_image(img, output_format, quality)
        return output.getvalue(), {"format": output_format.upper()}
    except Exception as e:
        raise Exception(str(e))


async def process_batch_images(
    files: list[UploadFile], output_format: str, processing_func
) -> tuple[str, list]:
    """Process multiple images and create a ZIP file."""
    temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=TEMP_SUFFIX)
    temp_zip_path = temp_zip.name
    temp_zip.close()

    results = []

    try:
        with zipfile.ZipFile(
            temp_zip_path, "w", ZIP_COMPRESSION, compresslevel=9
        ) as zipf:
            for file in files:
                if not validate_file(file):
                    continue

                try:
                    result = await processing_func(file, zipf, output_format)
                    results.append(result)
                except Exception as e:
                    results.append({"filename": file.filename, "error": str(e)})

        return temp_zip_path, results
    except Exception as e:
        os.unlink(temp_zip_path)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/convert")
async def convert_image_endpoint(
    file: UploadFile = File(...), output_format: str = Form("webp")
):
    """Convert single image to specified format."""
    try:
        if not validate_file(file):
            raise HTTPException(status_code=400, detail="File must be an image")

        contents = await file.read()
        converted_data, metadata = process_single_image(contents, output_format)

        response = StreamingResponse(
            io.BytesIO(converted_data), media_type=f"image/{output_format}"
        )
        response.headers.update(create_response_headers(metadata))
        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-convert")
async def batch_convert(
    files: list[UploadFile] = File(...), output_format: str = Form("webp")
):
    """Convert multiple images and return as ZIP."""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    if len(files) > MAX_FILES:
        raise HTTPException(
            status_code=400, detail=f"Maximum {MAX_FILES} files allowed"
        )

    async def process_file(file, zipf, fmt):
        contents = await file.read()
        converted_data, _ = process_single_image(contents, fmt)

        output_filename = get_output_filename(file.filename, fmt)
        zipf.writestr(output_filename, converted_data)

        return {
            "filename": output_filename,
            "format": fmt.upper(),
        }

    try:
        temp_zip_path, results = await process_batch_images(
            files, output_format, process_file
        )

        with open(temp_zip_path, "rb") as f:
            zip_data = f.read()

        os.unlink(temp_zip_path)

        response = StreamingResponse(io.BytesIO(zip_data), media_type="application/zip")
        response.headers["Content-Disposition"] = (
            "attachment; filename=converted_images.zip"
        )
        response.headers.update(create_response_headers({"results": results}))
        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
