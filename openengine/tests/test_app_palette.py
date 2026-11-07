"""Static checks that the live apps stay readable for colour-blind readers and in grayscale.

No browser is needed: the test reads the colour tokens and drawing code in each app.html.
"""
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
APPS = sorted((ROOT / "sessions").glob("session-*/app.html"))
OKABE_ITO = {"#000000", "#e69f00", "#56b4e9", "#009e73", "#f0e442", "#0072b2", "#d55e00", "#cc79a7"}
SERIES = ("--s1", "--s2", "--s3")


def luminance(hex_colour):
    h = hex_colour.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    rgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def themes(html):
    """Return the light and dark colour tokens as two dicts (dark inherits what it does not override)."""
    light_block = re.search(r":root\s*\{(.*?)\}", html, re.S).group(1)
    dark_block = re.search(r"prefers-color-scheme:\s*dark\)\s*\{\s*:root\s*\{(.*?)\}", html, re.S).group(1)
    tok = lambda block: dict(re.findall(r"(--[\w-]+)\s*:\s*(#[0-9a-fA-F]{3,6})", block))
    light = tok(light_block)
    return light, {**light, **tok(dark_block)}


def test_every_session_has_an_app():
    assert len(APPS) >= 3


@pytest.mark.parametrize("app", APPS, ids=lambda p: p.parent.name)
def test_series_colours_are_okabe_ito_with_contrast(app):
    html = app.read_text(encoding="utf-8")
    for name, theme in zip(("light", "dark"), themes(html)):
        for s in SERIES:
            assert s in theme, f"{app.parent.name}: {s} missing in {name} theme"
            assert theme[s].lower() in OKABE_ITO, f"{app.parent.name}: {s} = {theme[s]} is not an Okabe-Ito colour"
            ratio = contrast(theme[s], theme["--card"])
            assert ratio >= 3.0, f"{app.parent.name}: {s} contrast {ratio:.2f} against the plot background in {name} mode"


@pytest.mark.parametrize("app", APPS, ids=lambda p: p.parent.name)
def test_no_colour_only_meaning(app):
    html = app.read_text(encoding="utf-8")
    # legends must not rely on colour words, and plots must not use the old blue/red pair or a hue-only map
    assert not re.search(r'"(blue|red|green|grey|gray): ', html), f"{app.parent.name}: legend names a colour"
    drawing = html.split("function draw()")[1]
    for status in ("C.bad", "C.good", "C.accent"):
        assert status not in drawing, f"{app.parent.name}: plot draws with the UI colour {status}; use --s1..--s3"
    assert '"hsl("' not in html, f"{app.parent.name}: hue-only colour map"


def test_otto_and_diesel_differ_by_line_style():
    html = (ROOT / "sessions" / "session-02" / "app.html").read_text(encoding="utf-8")
    assert re.search(r"legend\(A, \[\[C\.s1, SOLID, \"Otto[^\"]*\"\], \[C\.s2, DASHED, \"Diesel", html)
    # every Diesel stroke (s2) on the efficiency and P-V plots is dashed
    for line in html.splitlines():
        for call in re.findall(r"(?:curve|seg)\([^;]*C\.s2[^;]*\)", line):
            assert "DASHED" in call, call


def test_temperature_map_brightens_with_temperature():
    html = (ROOT / "sessions" / "session-03" / "app.html").read_text(encoding="utf-8")
    stops = re.search(r"const HEAT = (\[\[.*?\]\]);", html).group(1)
    rgb = [tuple(int(v) for v in m) for m in re.findall(r"\[(\d+), (\d+), (\d+)\]", stops)]
    lum = [luminance("#%02x%02x%02x" % c) for c in rgb]
    assert lum == sorted(lum) and lum[-1] - lum[0] >= 0.5, lum
