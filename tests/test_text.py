from simpdf import Text, TextStyle

def test_text_init():
    style = TextStyle()
    line = Text(content_left="Left", content_center="Center", content_right="Right", style=style)
    assert line.content_left == "Left"
    assert line.content_center == "Center"
    assert line.content_right == "Right"
    assert line.style == style

def test_text_properties():
    line = Text(content_left="Test")
    assert line.ascent > 0
    assert line.descent < 0
    assert line.space_top >= 0
    assert line.space_bottom >= 0
    assert line.line_height_upper > 0
    assert line.line_height_lower > 0
