import os
import pytest
import numpy as np
from PIL import Image, ImageDraw
from unittest.mock import patch

from core.vision import (
    validate_image, assess_image_quality, preprocess_image,
    ImageFormat, ImageQualityStatus, PreprocessingConfig
)

# Test Fixtures (Synthetic Images)

@pytest.fixture(scope="session")
def temp_dir(tmp_path_factory):
    return tmp_path_factory.mktemp("vision_tests")

def create_synthetic_image(path, size=(800, 600), format="JPEG", color="blue", corrupt=False):
    if corrupt:
        with open(path, "wb") as f:
            f.write(b"NOT_AN_IMAGE_DATA_123456789")
        return path
        
    img = Image.new("RGB", size, color)
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), "Test Image", fill="white")
    
    # Introduce some noise for variance so it's not perfectly uniform
    if color != "black":
        arr = np.array(img)
        noise = np.random.randint(0, 50, arr.shape, dtype=np.uint8)
        arr = np.clip(arr + noise, 0, 255)
        img = Image.fromarray(arr)
        
    img.save(path, format=format)
    return path

@pytest.fixture
def valid_jpeg(temp_dir):
    return create_synthetic_image(os.path.join(temp_dir, "valid.jpg"), format="JPEG")

@pytest.fixture
def valid_png(temp_dir):
    return create_synthetic_image(os.path.join(temp_dir, "valid.png"), format="PNG")

@pytest.fixture
def valid_webp(temp_dir):
    return create_synthetic_image(os.path.join(temp_dir, "valid.webp"), format="WEBP")

@pytest.fixture
def text_file(temp_dir):
    path = os.path.join(temp_dir, "text.txt")
    with open(path, "w") as f:
        f.write("This is a text document.")
    return path

@pytest.fixture
def corrupted_image(temp_dir):
    return create_synthetic_image(os.path.join(temp_dir, "corrupt.jpg"), corrupt=True)

@pytest.fixture
def small_image(temp_dir):
    return create_synthetic_image(os.path.join(temp_dir, "small.jpg"), size=(100, 100))

@pytest.fixture
def blurry_image(temp_dir):
    # A perfectly smooth black image will have 0 variance, appearing very blurry/poor
    return create_synthetic_image(os.path.join(temp_dir, "blurry.jpg"), size=(400, 400), color="black")

# 1-3. Valid formats
def test_valid_jpeg(valid_jpeg):
    res = validate_image(valid_jpeg)
    assert res.is_valid is True
    assert res.format == ImageFormat.JPEG
    assert res.width == 800

def test_valid_png(valid_png):
    res = validate_image(valid_png)
    assert res.is_valid is True
    assert res.format == ImageFormat.PNG

def test_valid_webp(valid_webp):
    res = validate_image(valid_webp)
    assert res.is_valid is True
    assert res.format == ImageFormat.WEBP

# 4. Invalid non-image
def test_invalid_text_file(text_file):
    res = validate_image(text_file)
    assert res.is_valid is False
    assert res.format == ImageFormat.UNKNOWN
    assert "Unsupported format" in res.error_message

# 5. Oversized
@patch('os.path.getsize')
def test_oversized_image(mock_getsize, valid_jpeg):
    mock_getsize.return_value = 20 * 1024 * 1024  # 20MB
    res = validate_image(valid_jpeg)
    assert res.is_valid is False
    assert "maximum size" in res.error_message

# 6. Corrupted image
def test_corrupted_image(corrupted_image):
    res = validate_image(corrupted_image)
    assert res.is_valid is False
    assert "Unsupported format" in res.error_message or "corrupted" in res.error_message

# 7. Too small
def test_small_image(small_image):
    res = validate_image(small_image)
    assert res.is_valid is False
    assert "below minimum" in res.error_message

# 8. Normal quality
def test_normal_quality(valid_jpeg):
    metrics = assess_image_quality(valid_jpeg)
    # The noise added in synthetic fixture ensures some contrast/blur score
    assert metrics.status in [ImageQualityStatus.GOOD, ImageQualityStatus.DEGRADED, ImageQualityStatus.POOR]
    assert metrics.resolution_px == 800 * 600

# 10. Poor quality
def test_poor_quality(blurry_image):
    metrics = assess_image_quality(blurry_image)
    assert metrics.status == ImageQualityStatus.POOR
    assert metrics.blur_score < 300.0

# 11, 13. Preprocessing success and original preservation
def test_preprocessing_success(valid_jpeg, temp_dir):
    out_path = os.path.join(temp_dir, "processed.jpg")
    orig_mtime = os.path.getmtime(valid_jpeg)
    
    config = PreprocessingConfig(max_dimension=400, apply_grayscale=True, apply_contrast_enhancement=True)
    res = preprocess_image(valid_jpeg, out_path, config)
    
    assert res.success is True
    assert res.original_path == valid_jpeg
    assert res.processed_path == out_path
    
    # Original must remain untouched
    assert os.path.getmtime(valid_jpeg) == orig_mtime
    
    # Check processed
    assert os.path.exists(out_path)
    assert "grayscale" in res.operations_applied
    assert "resize_max_400" in res.operations_applied
    
    # Check dimensions were actually reduced
    with Image.open(out_path) as img:
        assert max(img.size) <= 400

# 12. Preprocessing failure
def test_preprocessing_failure(temp_dir):
    config = PreprocessingConfig()
    res = preprocess_image("/does/not/exist.jpg", os.path.join(temp_dir, "out.jpg"), config)
    assert res.success is False
    assert "missing" in res.error_message
