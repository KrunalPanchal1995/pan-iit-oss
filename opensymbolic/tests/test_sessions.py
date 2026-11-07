"""Run every lesson and checkpoint headless."""
import os
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
ENV = dict(os.environ, MPLBACKEND="Agg", PYTHONIOENCODING="utf-8")


@pytest.mark.parametrize("n", ["01", "02", "03"])
@pytest.mark.parametrize("script", ["lesson.py", "checkpoint.py"])
def test_session(n, script):
    path = ROOT / "sessions" / f"session-{n}" / script
    res = subprocess.run([sys.executable, str(path)], capture_output=True, text=True,
                         env=ENV, cwd=ROOT, timeout=180)
    assert res.returncode == 0, res.stdout + res.stderr
    if script == "checkpoint.py":
        assert "PASS" in res.stdout


def test_session_1_cooling_law():
    import importlib.util

    path = ROOT / "sessions" / "session-01" / "lesson.py"
    spec = importlib.util.spec_from_file_location("lesson1_cooling", path)
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    assert "c * exp(-t)" in lesson.LIBRARY, f"missing cooling candidate: {list(lesson.LIBRARY)}"
    t, temperature = lesson.cooling_data()
    c, mse = lesson.fit_c(lesson.LIBRARY["c * exp(-t)"](t), temperature)
    assert abs(c - 60.0) < 1e-12 and mse < 1e-20
