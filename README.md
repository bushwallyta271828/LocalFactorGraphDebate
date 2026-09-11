# Local Factor Graph Debate

Start with the [manuscript](manuscript.pdf), the mathematical companion to
the post. Its [LaTeX source](manuscript.tex) develops the
model, cores and oscillation, factor-specific bounds, Gaussian ensemble
bounds, and regular-tree lower bounds in that order. Proofs follow the
ideas they justify; the longer quantitative refinements are in appendices.

The [figure kit](figures/README.md) contains all ten post images, their
editable generators, and retained plotting data. Upload-ready PNGs are in
[figures/images/](figures/images/). Figures are distributed and rebuilt as
PNGs; the manuscript PDF is compiled using these same PNGs.
[Captions](figures/CAPTIONS.md) state the metrics, sample sizes, numerical
uncertainty, and cutoff conventions.

## Reproduce

The manuscript uses standard LaTeX packages: `amsmath`, `amssymb`, `amsthm`,
`mathtools`, `booktabs`, `graphicx`, `microtype`, and `hyperref`. A basic
pdfLaTeX installation with those packages is sufficient. Tectonic is also
supported if its packages are already cached.

```bash
python3 build.py --check-only
python3 build.py
```

To redraw the images, create a local Python virtual environment (Python
3.14 was used for validation) and install the pinned plotting dependencies:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r figures/requirements.txt
.venv/bin/python figures/reproduce.py --verify-only
.venv/bin/python figures/reproduce.py
```

The three diagrams additionally need Tectonic with cached TikZ/standalone
packages, or pdfLaTeX with TikZ/standalone, and Poppler's `pdftocairo`.
`--plots-only` skips the diagrams. The commands work without access to the
development repository or cloud services. Build products stay in local
`.build/` and `figures/reproduced/` directories. TeX/font versions may change
diagram rendering; the checked-in images remain the publication assets.

To check every distributed file using only the Python standard library:

```bash
python3 verify.py
```

The manifest describes the distributed files. Rebuilding or editing a file
can change its hash; verification then reports that difference.

## What the numerical reproduction covers

These commands compile the manuscript and redraw all figures from retained
results. They do not rerun the original Monte Carlo, optimization, or
distributed game-solving campaigns. The [methods](figures/data/METHODS.md)
describe those computations.

The figures distinguish finite-sample estimates, statistical brackets
conditional on floating-point enclosures, and numerical evaluations of
proved formulas. The release includes no claim that all decimals or all
proofs were machine-verified. The manuscript acknowledges the use of Codex
and Claude in proof development.

This directory is the complete public package; it contains no development
history or earlier drafts. No reuse license has been selected for it.
