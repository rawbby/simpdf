from simpdf import Separator

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
