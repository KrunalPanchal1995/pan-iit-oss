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


def test_session1_rounded_box_and_capsule():
    import importlib.util

    import numpy as np

    spec = importlib.util.spec_from_file_location("lesson1", ROOT / "sessions" / "session-01" / "lesson.py")
    lesson = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lesson)
    c0 = (0.0, 0.0)

    # rounded box: core half-sizes (1, 1) grown by r = 0.5, so the outer edge sits at 1.5
    assert abs(float(lesson.sd_round_box(c0, c0, (1, 1), 0.5)) + 1.5) < 1e-12  # centre is inside
    assert abs(float(lesson.sd_round_box((1.5, 0), c0, (1, 1), 0.5))) < 1e-12  # side surface
    corner = (1.0 + 0.5 * np.sqrt(0.5), 1.0 + 0.5 * np.sqrt(0.5))
    assert abs(float(lesson.sd_round_box(corner, c0, (1, 1), 0.5))) < 1e-12  # rounded corner surface
    assert abs(float(lesson.sd_round_box((2.5, 0), c0, (1, 1), 0.5)) - 1.0) < 1e-12  # outside

    # capsule: segment from (-1, 0) to (1, 0) grown by r = 0.5
    seg = ((-1.0, 0.0), (1.0, 0.0))
    assert abs(float(lesson.sd_capsule(c0, *seg, 0.5)) + 0.5) < 1e-12  # on the axis: inside
    assert abs(float(lesson.sd_capsule((0, 0.5), *seg, 0.5))) < 1e-12  # along the side: on surface
    assert abs(float(lesson.sd_capsule((1.5, 0), *seg, 0.5))) < 1e-12  # end cap: on surface
    assert abs(float(lesson.sd_capsule((2.0, 0), *seg, 0.5)) - 0.5) < 1e-12  # outside past the end
    pts = np.array([[0.0, 0.0], [0.0, 2.0], [-1.0, 0.0]])
    assert np.allclose(lesson.sd_capsule(pts, *seg, 0.5), [-0.5, 1.5, -0.5])  # arrays of points
