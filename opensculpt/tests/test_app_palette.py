from pathlib import Path
from urllib.parse import quote

import pytest

# This browser test needs Selenium and Chrome; CI and most laptops skip it.
webdriver = pytest.importorskip("selenium.webdriver")
Options = pytest.importorskip("selenium.webdriver.chrome.options").Options


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "sessions" / "session-01" / "app.html"
SCREENSHOT = ROOT / "docs" / "session-01-field-colour-contrast.png"


def test_rendered_field_has_grayscale_contrast_in_both_themes():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)
    try:
        driver.set_window_size(1000, 900)
        driver.get("file:///" + quote(str(APP).replace("\\", "/"), safe="/:"))

        for scheme in ("light", "dark"):
            driver.execute_cdp_cmd(
                "Emulation.setEmulatedMedia",
                {"features": [{"name": "prefers-color-scheme", "value": scheme}]},
            )
            driver.execute_script("draw()")
            values = driver.execute_script("""
                const image = ctx.getImageData(0, 0, W, H);
                const luminanceAt = (x, y) => {
                  const i = (y * W + x) * 4;
                  const [r, g, b] = image.data.slice(i, i + 3).map(v => v / 255);
                  const linear = v => v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
                  return 0.2126 * linear(r) + 0.7152 * linear(g) + 0.0722 * linear(b);
                };
                return [luminanceAt(260, 210), luminanceAt(60, 210)];
            """)
            gap = abs(values[0] - values[1])
            assert gap >= 0.2, f"rendered inside/outside grayscale luminance gap in {scheme} mode was {gap:.3f}"

        SCREENSHOT.parent.mkdir(exist_ok=True)
        driver.save_screenshot(str(SCREENSHOT))
    finally:
        driver.quit()
