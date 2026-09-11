#!/usr/bin/env python3
"""Rebuild the ten post figures locally from this self-contained folder."""
import argparse
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

BUNDLE = Path(__file__).resolve().parent
os.environ.setdefault("MPLCONFIGDIR", str(BUNDLE / ".build/matplotlib"))
sys.path.insert(0, str(BUNDLE / "source"))

DIAGRAMS = {
    "transcript-induced": "01_transcript",
    "core-oscillation-A": "02_core_oscillation",
    "routing-combined": "06_core_routing",
}
STEMS = ["01_transcript", "02_core_oscillation", "03_core_mean",
         "04_alternating_debate", "05_debate_core", "06_core_routing",
         "07_ensemble_bound", "08_debate_upper", "09_lower_exponents",
         "10_debate_bounds"]


def check_images():
    expected = {f"{stem}.png" for stem in STEMS}
    actual = {p.name for p in (BUNDLE / "images").iterdir()}
    if actual != expected:
        raise ValueError(f"Expected only the ten PNG images; missing: {sorted(expected - actual)}, "
                         f"unexpected: {sorted(actual - expected)}")


def refresh_manifest():
    check_images()
    files = [BUNDLE / name for name in ("README.md", "CAPTIONS.md", "reproduce.py", "requirements.txt", "numerics-requirements.txt", ".gitignore", ".gitattributes")]
    for directory in ("source", "data", "images"):
        files.extend(p for p in (BUNDLE / directory).rglob("*")
                     if p.is_file() and "__pycache__" not in p.parts)
    manifest = {"version": 1, "files": {
        str(p.relative_to(BUNDLE)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(files)}}
    (BUNDLE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Recorded {len(files)} bundled files.")


def verify():
    check_images()
    manifest = json.loads((BUNDLE / "manifest.json").read_text())
    expected_images = {f"images/{stem}.png" for stem in STEMS}
    recorded_images = {p for p in manifest["files"] if p.startswith("images/")}
    if recorded_images != expected_images:
        raise ValueError("The figure manifest must contain exactly the ten PNG images")
    for relative, expected in manifest["files"].items():
        actual = hashlib.sha256((BUNDLE / relative).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"Changed bundle file: {relative}")
    print(f"Verified {len(manifest['files'])} bundled files.")


def run(command, cwd):
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(f"Failed: {' '.join(map(str, command))}\n{result.stdout}\n{result.stderr}")


def diagrams(dest):
    """Regenerate TikZ in a scratch directory, then compile and export it."""
    tectonic = shutil.which("tectonic")
    venv_tectonic = Path(sys.executable).parent / "tectonic"
    if tectonic is None and venv_tectonic.is_file():
        tectonic = str(venv_tectonic)
    for command in (("pdftocairo",) if tectonic else ("pdflatex", "pdftocairo")):
        if not shutil.which(command):
            raise RuntimeError(f"Diagram rebuild needs {command}; see README.md.")
    work = BUNDLE / ".build/diagrams"
    shutil.copytree(BUNDLE / "source/diagrams", work, dirs_exist_ok=True)
    for script in ("gen_transcript.py", "gen_core_oscillation.py",
                   "gen_routing_graph.py", "gen_routing_combined.py"):
        run([sys.executable, script], work)
    for source, stem in DIAGRAMS.items():
        command = ([tectonic, "--only-cached", source + ".tex"] if tectonic else
                   ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", source + ".tex"])
        run(command, work)
        pdf = work / (source + ".pdf")
        run(["pdftocairo", "-png", "-singlefile", "-r", "300", str(pdf), str(dest / stem)], work)


def plots(dest):
    from plot_curves import plot
    from plot_heatmaps import render
    import matplotlib.pyplot as plt

    report = json.loads((BUNDLE / "data/curves.json").read_text())
    for stem, upper, lower in [("05_debate_core", False, False),
                               ("08_debate_upper", True, False),
                               ("10_debate_bounds", True, True)]:
        panel = deepcopy(report)
        if not upper:
            panel.pop("ensemble_bound")
        if not lower:
            panel.pop("absolute_lower_bound")
            panel.pop("lower_curve")
        with plt.rc_context(plt.rcParamsDefault):
            plot(panel, dest / (stem + ".png"))
    with plt.rc_context(plt.rcParamsDefault):
        render(BUNDLE / "data", dest)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=BUNDLE / "reproduced",
                        help="destination (default: reproduced/ inside this folder)")
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--verify-only", action="store_true", help="check the release SHA-256 manifest")
    actions.add_argument("--refresh-manifest", action="store_true",
                         help="record new release hashes after intentional edits; does not rebuild")
    parser.add_argument("--plots-only", action="store_true", help="skip the three TikZ diagrams")
    args = parser.parse_args()
    if args.verify_only:
        verify()
        return
    if args.refresh_manifest:
        refresh_manifest()
        return
    dest = args.output.resolve()
    dest.mkdir(parents=True, exist_ok=True)
    plots(dest)
    if not args.plots_only:
        diagrams(dest)
    print(f"Rebuilt {7 if args.plots_only else 10} figures in PNG: {dest}")


if __name__ == "__main__":
    main()
