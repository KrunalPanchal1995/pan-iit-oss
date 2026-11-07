"""The Target reproduction reaches the published efficiencies (no animation is written here)."""
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def test_target_efficiencies():
    res = subprocess.run([sys.executable, str(ROOT / "target" / "target.py"), "--check"], capture_output=True, text=True,
                         env=dict(os.environ, MPLBACKEND="Agg", PYTHONIOENCODING="utf-8"), cwd=ROOT, timeout=120)
    assert res.returncode == 0, res.stdout + res.stderr
    assert res.stdout.strip().endswith("PASS")
    for want in ("shown as 0.585", "shown as 0.624", "shown as 0.867"):
        assert want in res.stdout
