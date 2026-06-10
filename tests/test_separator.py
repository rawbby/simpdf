from simpdf import Separator
from unittest.mock import MagicMock
from reportlab.pdfgen.canvas import Canvas

def test_separator_init():
    sep = Separator(line_spacing=20.0, thickness=2.0)
    assert sep.line_spacing == 20.0
    assert sep.thickness == 2.0

def test_separator_properties():
    sep = Separator(line_spacing=10.0, thickness=1.0)
    assert sep.space_top == 5.0
    assert sep.space_bottom == 5.0
    assert sep.ascent == 0.5
    assert sep.descent == -0.5
    assert sep.line_height_upper == 5.5
    assert sep.line_height_lower == 5.5
    assert sep.line_height == 11.0

def test_separator_draw_default():
    sep = Separator()
    canvas = MagicMock(spec=Canvas)
    sep.draw(canvas, 100, 10, 110)
    canvas.line.assert_called_once_with(10, 100, 110, 100)

def test_separator_draw_lengths():
    # User's logic has a quirk where any None sets length_center=1.0, 
    # and right length uses left length internally. Providing all 3 avoids the None check.
    sep = Separator(length_left=0.2, length_center=0.5, length_right=0.1)
    canvas = MagicMock(spec=Canvas)
    sep.draw(canvas, 100, 0, 100)
    assert canvas.line.call_count == 3
    canvas.line.assert_any_call(0, 100, 20, 100)
    canvas.line.assert_any_call(25, 100, 75, 100)
    # NOTE: right length uses length_right = 0.1 * pt_total = 10
    canvas.line.assert_any_call(90, 100, 100, 100)

import pytest

def test_separator_draw_overlap_assertions():
    canvas = MagicMock(spec=Canvas)
    
    # Valid
    sep = Separator(length_left=0.2, length_center=0.5, length_right=0.2)
    sep.draw(canvas, 100, 0, 100)
    
    # Overlap left and center
    sep = Separator(length_left=0.6, length_center=0.5, length_right=None)
    with pytest.raises(AssertionError):
        sep.draw(canvas, 100, 0, 100)

    # Overlap center and right
    sep = Separator(length_left=None, length_center=0.5, length_right=0.6)
    with pytest.raises(AssertionError):
        sep.draw(canvas, 100, 0, 100)

    # Overlap left and right
    sep = Separator(length_left=0.6, length_center=None, length_right=0.6)
    with pytest.raises(AssertionError):
        sep.draw(canvas, 100, 0, 100)

    # Individual too large
    sep = Separator(length_left=1.5, length_center=None, length_right=None)
    with pytest.raises(AssertionError):
        sep.draw(canvas, 100, 0, 100)
