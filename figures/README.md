# Figure kit

All ten figures of the post, in post order. Upload-ready PNG files are in
[images/](images/).

| # | Image | Editable source | Plotting input |
|---|---|---|---|
| 01 | [Hidden graph and transcript](images/01_transcript.png) | [gen_transcript.py](source/diagrams/gen_transcript.py) | graph_data.py |
| 02 | [Core oscillation](images/02_core_oscillation.png) | [gen_core_oscillation.py](source/diagrams/gen_core_oscillation.py) | factor_model.py, graph_data.py |
| 03 | [Mean core budget](images/03_core_mean.png) | [plot_heatmaps.py](source/plot_heatmaps.py) | [core_mean.json](data/core_mean.json) |
| 04 | [Alternating debate budget](images/04_alternating_debate.png) | plot_heatmaps.py | [alternating_debate.csv](data/alternating_debate.csv) |
| 05 | [Debate error and optimal core](images/05_debate_core.png) | [plot_curves.py](source/plot_curves.py) | [curves.json](data/curves.json) |
| 06 | [Core routing](images/06_core_routing.png) | [gen_routing_combined.py](source/diagrams/gen_routing_combined.py) | graph_data.py, routing-tree.tex |
| 07 | [Ensemble budget bound](images/07_ensemble_bound.png) | plot_heatmaps.py | [ensemble.csv](data/ensemble.csv) |
| 08 | [Debate error and upper bounds](images/08_debate_upper.png) | plot_curves.py | curves.json |
| 09 | [RMS lower-bound exponents](images/09_lower_exponents.png) | plot_heatmaps.py | [lower_exponents.json](data/lower_exponents.json) |
| 10 | [Debate error and upper/lower bounds](images/10_debate_bounds.png) | plot_curves.py | curves.json |

[CAPTIONS.md](CAPTIONS.md) supplies captions and interpretation notes.
[data/METHODS.md](data/METHODS.md) documents the statistics and finite
models. [manifest.json](manifest.json) records the files distributed in
this kit.

## Rebuild locally

From the release root, after installing [requirements.txt](requirements.txt)
in a virtual environment:

```bash
.venv/bin/python figures/reproduce.py --verify-only
.venv/bin/python figures/reproduce.py
```

The rebuild uses only local plotting data and writes all ten PNG
exports to `reproduced/`. Add `--plots-only` to redraw the seven numerical
plots without compiling the three diagrams. Diagram generation needs
Tectonic with cached TikZ/standalone packages, or pdfLaTeX with those
packages, and Poppler's `pdftocairo`. Scratch files, including intermediate
diagram PDFs, stay under `.build/`.
Paths are resolved from this folder, so the commands also work from another
working directory.

To intentionally replace publication assets, use `--output figures/images`,
inspect the result, then `--refresh-manifest`. Updating the outer release
manifest is a separate development step. Compiler and font differences may
change rendered bytes. The generator retains the original random seeds
and plotting constants.

## Numerical certificates

Most lower-exponent cells use the manuscript's analytic Gaussian
certificate. Two cells, (d,σ)=(5,4) and (6,8), use outward-verified
endpoint mixtures whose parameters are in
[endpoint_certificates.json](data/endpoint_certificates.json).
An optional, standalone [Arb verifier](source/numerics/endpoint_certificates.py)
retains the endpoint search and outward verification algorithm:

```bash
.venv/bin/python -m pip install -r numerics-requirements.txt
.venv/bin/python figures/source/numerics/endpoint_certificates.py --q 4
.venv/bin/python figures/source/numerics/endpoint_certificates.py --q 5
```

These are longer computations, roughly ten minutes per degree at the
default resolution, and are unnecessary for redrawing the figures. They
search for and verify a mixture, and can return different valid
coefficients with a different linear-programming library. Results go to
`.build/endpoint-certificates.json`; publication inputs are not overwritten.
The decimal heatmap exponents themselves are numerical quadrature results,
not outward certificates. See the manuscript for the truncation step that
converts an untruncated endpoint mixture into the plotted certificate.
