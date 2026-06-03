from simpdf import InlineImage

def test_image_init(generate_image):
    left_img = generate_image(width=50, height=50)
    img = InlineImage(image_height=50.0, image_path_left=left_img, image_path_center=None, image_path_right=None)
    assert img.image_height == 50.0
    assert img.image_path_left == left_img
    assert img.image_path_center is None
    assert img.image_path_right is None
    assert img.line_spacing == 10.0

def test_image_properties():
    img = InlineImage(image_height=100.0, image_path_left=None, image_path_center=None, image_path_right=None, line_spacing=20.0)
    assert img.space_top == 10.0
    assert img.space_bottom == 10.0
    assert img.ascent == 100.0
    assert img.descent == 0.0
    assert img.line_height_upper == 110.0
    assert img.line_height_lower == 10.0
    assert img.line_height == 120.0

from simpdf.inline_image import _scale_image
from PIL import Image

def test_scale_image_box_combines_n_pixels():
    """
    Test that _scale_image correctly finds the max divider `k` instead of halving,
    keeps the remainder logic, and uses BOX which combines `k` pixels.
    """
    # Create a 10x10 image. target_height_px = 3. 
    # Max divider k: 10 // k >= 3 => k=3. 
    # Remainder 10 % 3 = 1.
    # Cropped size: 9x9.
    # Scaled size: 3x3.
    img = Image.new("L", (10, 10), 0)
    
    # Fill the center 3x3 block with white pixels.
    # The remainder is 1, so left=0, top=0, right=9, bottom=9 is cropped.
    # The 9x9 image is divided into 3x3 blocks.
    # Let's set block (1, 1) (pixels x:3..5, y:3..5) to 255
    for x in range(3, 6):
        for y in range(3, 6):
            img.putpixel((x, y), 255)
            
    scaled_img = _scale_image(img, 3)
    
    assert scaled_img.size == (3, 3)
    
    # Check that BOX combined the 3x3 pixels. 
    # The center pixel of the scaled image should be mostly white, 
    # and the other pixels should be mostly black, but we can verify it's the max value.
    center_val = scaled_img.getpixel((1, 1))
    edge_val = scaled_img.getpixel((0, 0))
    
    # Center pixel should have combined the 255s
    assert center_val == 255
    # Edge pixel should have combined the 0s
    assert edge_val == 0


def test_box_vs_manual_average():
    """
    Test that BOX scaling is comparable to a manual implementation
    that simply takes the average of n times n pixels.
    """
    orig_w, orig_h = 40, 40
    target_h = 10
    k = orig_h // target_h  # 4
    
    img = Image.new("L", (orig_w, orig_h))
    for x in range(orig_w):
        for y in range(orig_h):
            # Gradient pattern to ensure varied but smooth pixel values
            val = int(255 * (x / orig_w) * (y / orig_h))
            img.putpixel((x, y), val)
            
    scaled_img = _scale_image(img, target_h)
    
    manual_w, manual_h = orig_w // k, orig_h // k
    manual_img = Image.new("L", (manual_w, manual_h))
    
    # Manual average of n x n pixels
    for out_x in range(manual_w):
        for out_y in range(manual_h):
            s = 0
            for dx in range(k):
                for dy in range(k):
                    s += img.getpixel((out_x * k + dx, out_y * k + dy))
            manual_img.putpixel((out_x, out_y), (s + (k*k)//2) // (k * k))
            
    max_diff = 0
    for x in range(manual_w):
        for y in range(manual_h):
            diff = abs(scaled_img.getpixel((x, y)) - manual_img.getpixel((x, y)))
            max_diff = max(max_diff, diff)
            
    # The box reduction should match the exact arithmetic average
    assert max_diff == 0

from unittest.mock import MagicMock
import pytest

def test_inline_image_no_dpi(generate_image):
    img_path = generate_image(width=100, height=100)
    canvas = MagicMock()
    canvas.drawInlineImage.return_value = (50, 50)
    
    img = InlineImage(
        image_height=50.0,
        image_path_left=img_path,
        image_path_center=None,
        image_path_right=None,
        dpi=None
    )
    
    img.draw(canvas, baseline=0.0, start=0.0, end=100.0)
    
    canvas.drawInlineImage.assert_called_once()
    args, kwargs = canvas.drawInlineImage.call_args
    assert args[0] == str(img_path)

def test_inline_image_dpi_image_too_small(generate_image):
    # image_height = 72, dpi = 72 => min_height = 72
    img_path = generate_image(width=50, height=50) # height < 72
    canvas = MagicMock()
    canvas.drawInlineImage.return_value = (50, 50)
    
    img = InlineImage(
        image_height=72.0,
        image_path_left=img_path,
        image_path_center=None,
        image_path_right=None,
        dpi=72.0
    )
    
    img.draw(canvas, baseline=0.0, start=0.0, end=100.0)
    
    canvas.drawInlineImage.assert_called_once()
    args, kwargs = canvas.drawInlineImage.call_args
    assert args[0] == str(img_path)

def test_inline_image_dpi_image_k_is_1(generate_image):
    # image_height = 72, dpi = 72 => min_height = 72
    img_path = generate_image(width=100, height=100) # height > 72 but 100 // 2 = 50 < 72 => k=1
    canvas = MagicMock()
    canvas.drawInlineImage.return_value = (50, 50)
    
    img = InlineImage(
        image_height=72.0,
        image_path_left=img_path,
        image_path_center=None,
        image_path_right=None,
        dpi=72.0
    )
    
    img.draw(canvas, baseline=0.0, start=0.0, end=100.0)
    
    canvas.drawInlineImage.assert_called_once()
    args, kwargs = canvas.drawInlineImage.call_args
    assert args[0] == str(img_path)

def test_inline_image_dpi_image_scales(generate_image):
    # image_height = 72, dpi = 72 => min_height = 72
    img_path = generate_image(width=200, height=200) # 200 // 2 = 100 >= 72 => k=2
    canvas = MagicMock()
    canvas.drawInlineImage.return_value = (50, 50)
    
    img = InlineImage(
        image_height=72.0,
        image_path_left=img_path,
        image_path_center=None,
        image_path_right=None,
        dpi=72.0
    )
    
    img.draw(canvas, baseline=0.0, start=0.0, end=100.0)
    
    canvas.drawInlineImage.assert_called_once()
    args, kwargs = canvas.drawInlineImage.call_args
    passed_img = args[0]
    
    assert isinstance(passed_img, Image.Image)
    assert passed_img.size == (100, 100) # 200 // 2 = 100

def test_inline_image_draw_positions_and_widths(generate_image):
    left_path = generate_image(width=10, height=10)
    center_path = generate_image(width=10, height=10)
    right_path = generate_image(width=10, height=10)
    
    canvas = MagicMock()
    canvas.drawInlineImage.side_effect = [(10, 10), (10, 10), (10, 10)]
    
    img = InlineImage(
        image_height=10.0,
        image_path_left=left_path,
        image_path_center=center_path,
        image_path_right=right_path,
        dpi=None
    )
    
    img.draw(canvas, baseline=5.0, start=10.0, end=110.0) # line_width = 100
    
    assert canvas.drawInlineImage.call_count == 3
    calls = canvas.drawInlineImage.call_args_list
    
    # Left
    assert calls[0][0][0] == str(left_path)
    assert calls[0][0][1] == 10.0
    assert calls[0][1]["anchor"] == "sw"
    
    # Center
    assert calls[1][0][0] == str(center_path)
    assert calls[1][0][1] == 60.0 # start + 0.5 * line_width = 10 + 50 = 60
    assert calls[1][1]["anchor"] == "s"
    
    # Right
    assert calls[2][0][0] == str(right_path)
    assert calls[2][0][1] == 110.0 # start + line_width = 10 + 100 = 110
    assert calls[2][1]["anchor"] == "se"

def test_inline_image_asserts_widths(generate_image):
    left_path = generate_image(width=60, height=10)
    
    canvas = MagicMock()
    canvas.drawInlineImage.return_value = (60, 10)
    
    img = InlineImage(
        image_height=10.0,
        image_path_left=left_path,
        image_path_center=None,
        image_path_right=None,
        dpi=None
    )
    
    with pytest.raises(AssertionError):
        # 60 > line_width (50) -> should raise
        img.draw(canvas, baseline=0.0, start=0.0, end=50.0)
