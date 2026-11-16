# Regression tests for short_qa.py's frozen-span detection (issue #13).
#
# short_qa.py only records a frozen span when a later frame resumes motion,
# so a freeze that runs to the last frame was silently dropped from the
# report. These tests build tiny synthetic videos with ffmpeg and run the
# real script end to end, then read the "frozen spans" line of report.md.
#
# Usage: python3 templates/scripts/test_short_qa.py
# Requires ffmpeg + numpy (the same deps short_qa.py itself needs).
import ast
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SHORT_QA = os.path.join(HERE, "short_qa.py")
W, H = 180, 320


def frame(kind):
    """Three visually distinct patterns; identical kinds decode identically."""
    if kind == "A":
        g = np.linspace(20, 60, W, dtype=np.uint8)
        img = np.tile(g, (H, 1))
    elif kind == "B":
        g = np.linspace(180, 220, W, dtype=np.uint8)
        img = np.tile(g, (H, 1))
    elif kind == "C":
        g = np.linspace(100, 140, H, dtype=np.uint8)[:, None]
        img = np.tile(g, (1, W))
    else:
        raise ValueError(kind)
    return np.stack([img, img, img], axis=-1)


def write_video(path, kinds):
    frames = np.stack([frame(k) for k in kinds])
    proc = subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{W}x{H}", "-r", "30", "-i", "-",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-qp", "0", path],
        input=frames.tobytes(), capture_output=True)
    assert proc.returncode == 0, proc.stderr.decode()


def frozen_spans(video):
    """Run short_qa.py on `video` and parse the frozen-span list from report.md."""
    with tempfile.TemporaryDirectory() as tmp:
        outdir = os.path.join(tmp, "out")
        proc = subprocess.run([sys.executable, SHORT_QA, video, outdir],
                              capture_output=True, text=True)
        assert proc.returncode == 0, proc.stderr
        with open(os.path.join(outdir, "report.md"), encoding="utf-8") as f:
            report = f.read()
    m = re.search(r"frozen spans >=12f (\[.*?\])", report)
    assert m, f"no frozen-span line in report:\n{report}"
    return ast.literal_eval(m.group(1))


@unittest.skipUnless(shutil.which("ffmpeg"), "ffmpeg not on PATH")
class TestFrozenSpans(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def video(self, name, kinds):
        path = os.path.join(self.tmp.name, name)
        write_video(path, kinds)
        return path

    def test_trailing_freeze_is_reported(self):
        # Issue #13, case 2: diff [1.0] + [0.0]*12 ends in a freeze.
        self.assertEqual(frozen_spans(self.video("tail.mp4", ["A"] + ["B"] * 13)),
                         [(1, 13)])

    def test_mid_video_freeze_still_reported(self):
        # Control: a freeze followed by resumed motion.
        self.assertEqual(frozen_spans(self.video("mid.mp4", ["A"] + ["B"] * 13 + ["C"])),
                         [(1, 13)])

    def test_short_trailing_freeze_stays_below_threshold(self):
        # Issue #13, case 3: diff [1.0] + [0.0]*11 is below the 12-diff threshold.
        self.assertEqual(frozen_spans(self.video("short.mp4", ["A"] + ["B"] * 12)), [])


if __name__ == "__main__":
    unittest.main()
