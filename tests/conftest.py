import pytest
import random
from pathlib import Path
from PIL import Image

@pytest.fixture
def generate_image(tmp_path):
    def _generate(width: int = 100, height: int = 100, color: tuple[int, int, int] | None = None, suffix: str = ".png") -> Path:
        if color is None:
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        img = Image.new("RGB", (width, height), color=color)
        file_path = tmp_path / f"test_image_{random.randint(1000, 9999)}{suffix}"
        img.save(file_path)
        return file_path
    return _generate
