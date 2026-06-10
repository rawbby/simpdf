import pytest
from reportlab.lib.colors import Color as ReportlabColor
from simpdf.rgb import RGB

def test_color_from_reportlab():
    rl_color = ReportlabColor(0.1, 0.2, 0.3)
    c = RGB(rl_color)
    assert c.red == pytest.approx(0.1)
    assert c.green == pytest.approx(0.2)
    assert c.blue == pytest.approx(0.3)

def test_color_from_reportlab_ignores_alpha():
    rl_color = ReportlabColor(0.1, 0.2, 0.3, alpha=0.5)
    c = RGB(rl_color)
    assert c.red == pytest.approx(0.1)
    assert c.green == pytest.approx(0.2)
    assert c.blue == pytest.approx(0.3)
    # The new reportlab color should have default alpha (1.0)
    assert getattr(c, 'alpha', 1.0) == 1.0

def test_color_from_scalar_int():
    c = RGB(128)
    # 128 / 255 = 0.50196
    expected = 128 / 255.0
    assert c.red == pytest.approx(expected)
    assert c.green == pytest.approx(expected)
    assert c.blue == pytest.approx(expected)

def test_color_from_scalar_float():
    c = RGB(0.5)
    assert c.red == pytest.approx(0.5)
    assert c.green == pytest.approx(0.5)
    assert c.blue == pytest.approx(0.5)

def test_color_from_tuple_int():
    c = RGB((255, 128, 0))
    assert c.red == pytest.approx(1.0)
    assert c.green == pytest.approx(128 / 255.0)
    assert c.blue == pytest.approx(0.0)

def test_color_from_tuple_float():
    c = RGB((1.0, 0.5, 0.0))
    assert c.red == pytest.approx(1.0)
    assert c.green == pytest.approx(0.5)
    assert c.blue == pytest.approx(0.0)

def test_color_from_tuple_mixed():
    c = RGB((255, 0.5, 0))
    assert c.red == pytest.approx(1.0)
    assert c.green == pytest.approx(0.5)
    assert c.blue == pytest.approx(0.0)

def test_color_from_color():
    c1 = RGB(0.5)
    c2 = RGB(c1)
    assert c2.red == pytest.approx(0.5)
    assert c1 == c2

def test_color_normalization_bounds():
    c1 = RGB(300)
    assert c1.red == pytest.approx(1.0)
    
    c2 = RGB(-10)
    assert c2.red == pytest.approx(0.0)
    
    c3 = RGB(1.5)
    assert c3.red == pytest.approx(1.0)
    
    c4 = RGB(-0.5)
    assert c4.red == pytest.approx(0.0)

def test_color_invalid_type():
    with pytest.raises(TypeError):
        RGB("red")

    with pytest.raises(TypeError):
        # noinspection PyTypeChecker
        RGB((1, 2))
