from simpdf import TextStyle

def test_textstyle_defaults():
    style = TextStyle()
    assert style.font == "Helvetica"
    assert style.font_size == 11.0
    assert style.line_height_factor == 1.2
    assert style.char_space_factor == 0.0
    assert style.word_space_factor == 0.0

def test_textstyle_custom():
    style = TextStyle(font="Times-Roman", font_size=12.0, line_height_factor=1.5)
    assert style.font == "Times-Roman"
    assert style.font_size == 12.0
    assert style.line_height == 18.0
