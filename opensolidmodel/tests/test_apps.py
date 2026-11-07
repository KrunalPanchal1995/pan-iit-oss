"""Check every live app: no NaN or Infinity at min, default and max, no dead sliders, challenge works.

Needs Node.js (preinstalled on GitHub runners); the test is skipped if Node is missing.
"""
import pathlib
import shutil
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
HARNESS = ROOT / "tests" / "app_harness.mjs"


@pytest.mark.skipif(shutil.which("node") is None, reason="Node.js is not installed")
@pytest.mark.parametrize("n", ["01", "02", "03"])
def test_app(n):
    app = ROOT / "sessions" / f"session-{n}" / "app.html"
    res = subprocess.run(["node", str(HARNESS), str(app)], capture_output=True, text=True, timeout=60)
    assert res.returncode == 0, res.stdout + res.stderr
    assert "APP OK" in res.stdout
