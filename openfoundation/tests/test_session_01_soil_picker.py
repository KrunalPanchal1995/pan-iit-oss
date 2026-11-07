import pathlib
import re
import json
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class SoilPickerTest(unittest.TestCase):
    def test_app_offers_soil_midpoint_presets_with_teaching_note(self):
        html = (ROOT / "sessions" / "session-01" / "app.html").read_text(encoding="utf-8")
        presets = json.loads(re.search(r"const PRESETS = (\[.*?\]);", html).group(1))
        soil_presets = {preset["label"]: preset["values"]["qa"] for preset in presets}

        for soil, pressure in (("Soft clay", 75), ("Firm clay", 150), ("Dense sand", 300)):
            with self.subTest(soil=soil):
                self.assertEqual(soil_presets.get(soil), pressure)

        self.assertIn('for (const pr of PRESETS)', html)
        self.assertIn('b.textContent = pr.label', html)
        self.assertIn('b.addEventListener("click", () => setAll(pr.values))', html)

        self.assertRegex(
            html,
            r'<p class="note">.*(?:teaching|typical).*not for design.*</p>',
            "visible note should say soil pressures are teaching values, not for design",
        )


if __name__ == "__main__":
    unittest.main()
