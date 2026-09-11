#!/usr/bin/env python3
"""Validate and compile the release manuscript using only local inputs."""
import argparse
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
FIGURES = re.compile(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}")


def validate(source):
    text = source.read_text()
    for marker in (r"\documentclass", r"\begin{document}", r"\end{document}"):
        if text.count(marker) != 1:
            raise ValueError(f"Expected exactly one {marker}")
    if re.search(r"\\(?:input|include|bibliography|addbibresource)\b", text):
        raise ValueError("The manuscript must be self-contained apart from figures")
    labels = re.findall(r"\\label\{([^}]+)\}", text)
    if len(labels) != len(set(labels)):
        raise ValueError("Duplicate labels")
    refs = re.findall(r"\\(?:eqref|ref|pageref)\{([^}]+)\}", text)
    missing = set(refs)-set(labels)
    if missing:
        raise ValueError(f"Undefined source references: {sorted(missing)}")
    citations = {x for group in re.findall(r"\\cite\{([^}]+)\}", text) for x in group.split(',')}
    if citations-set(re.findall(r"\\bibitem\{([^}]+)\}", text)):
        raise ValueError("Missing bibliography entries")
    files = []
    for name in FIGURES.findall(text):
        relative = Path(name)
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError(f"Figure escapes source directory: {name}")
        figure = source.parent/relative
        if not figure.is_file() or figure.is_symlink():
            raise ValueError(f"Missing or linked figure: {figure}")
        files.append(relative)
    return files


def build(source, work):
    files = validate(source)
    work.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, work/source.name)
    for relative in files:
        target = work/relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source.parent/relative, target)
    env = os.environ.copy()
    env.update(SOURCE_DATE_EPOCH='1789084800', FORCE_SOURCE_DATE='1',
               TEXMFVAR=str(work/'texmf-var'), TEXMFCONFIG=str(work/'texmf-config'))
    pdflatex = shutil.which('pdflatex')
    tectonic = shutil.which('tectonic')
    beside_python = Path(sys.executable).parent/'tectonic'
    if tectonic is None and beside_python.is_file():
        tectonic = str(beside_python)
    if pdflatex:
        command = [pdflatex, '-no-shell-escape', '-interaction=nonstopmode', '-halt-on-error', source.name]
        runs = 3
    elif tectonic:
        command = [tectonic, '--only-cached', '--keep-logs', source.name]
        runs = 1
    else:
        raise RuntimeError('Install pdfLaTeX or Tectonic with its TeX packages cached; see README.md')
    for _ in range(runs):
        completed = subprocess.run(command, cwd=work, env=env, text=True, capture_output=True)
        (work/'build.stdout').write_text(completed.stdout+completed.stderr)
        if completed.returncode:
            raise RuntimeError(f"TeX failed; see {work/'build.stdout'}\n"+completed.stdout[-3000:]+completed.stderr[-1000:])
    log = (work/source.with_suffix('.log').name).read_text(errors='replace')
    if re.search(r'undefined references|Citation .* undefined|Reference .* undefined|multiply defined|Rerun to get cross-references right', log):
        raise RuntimeError('Unresolved TeX references; see build log')
    if 'Overfull' in log:
        raise RuntimeError('Overfull TeX boxes; inspect and fix the build log')
    pdf = source.with_suffix('.pdf')
    shutil.copyfile(work/pdf.name, pdf)
    print(f'Built {pdf}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT/'manuscript.tex')
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    source = args.source.resolve()
    validate(source)
    print(f'Validated {source}')
    if not args.check_only:
        build(source, source.parent/'.build/manuscript')


if __name__ == '__main__':
    main()
