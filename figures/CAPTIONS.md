# Figure captions

The numbers match the filenames in `images/` and the post order. All error
curves use h moves **per player**, hence 2h total debate moves.

## 01 — Hidden graph and transcript

Circles represent variables and squares represent factors. The target is t.
The debaters see the full factor graph on the left; the judge sees the
subgraph induced by the revealed variables on the right.

## 02 — Core oscillation

A connected core K and several transcripts containing it. The judge's
target log-odds vary with the transcript; the full range over transcripts
containing K is the core's completion oscillation.

## 03 — Mean core budget

Minimum fixed budget h whose sample mean minimum connected-core completion
oscillation is at most 0.1. Each cell uses 1,000 Gaussian edge-table draws
on a 50,000-vertex partially filled regular degree-d tree, with zero unary
factors. Cores have at most h+1 vertices including the target. The image
uses the upper numerical crossing, clipped at 500; colored hatching marks
budgets at least that large. This is a finite-sample estimate of a crossing
of the mean oscillation, not the mean of per-draw crossing budgets.

## 04 — Alternating debate budget

Moves per player needed for mean absolute root-logit error below 0.1 on
finite regular tree balls with Gaussian edge tables. Colors show midpoints
of the retained population-threshold brackets when bounded, and the known
lower endpoint when the upper endpoint is unknown. Hatching denotes such
lower bounds at the measurement cutoff: most mean h≥9, while boundary
cells mean h≥8. The statistical inference assumes the guarded floating-point
game enclosures are valid. The color scale is shared with figures 03 and 07.

## 05 — Debate error and optimal core

Ordinary Max-first alternating debate on regular degree-four tree balls of
depth 8 (13,121 vertices), with σ=0.35 and zero unary factors. Blue shows
mean absolute logit error over 64 Gaussian-table draws; orange shows the
mean minimum completion oscillation among connected cores of size h+1,
optimized separately on the same draws. Bars enclose the empirical debate
mean using numerical strategy bounds. Shading adds approximate pointwise
95% sampling uncertainty. Core minima use exact combinatorial dynamic
programming with floating-point evaluation.

Seeds are 7–70, shared across budgets. Debate horizons are
1,2,3,5,7,10,15,20,30,40,50,65,80,100; cores cover every h=1,…,100.
Error is measured against each tree's own full-information root logit.
These finite numerical results are not outward certificates.

## 06 — Core routing

A graph with core K and a routing tree for that core. Blue arrows trace
selected self-avoiding routes from the target; dashed red arrows mark
gates: omitted self-avoiding extensions, including internal extensions if the routing omits them.

## 07 — Ensemble budget bound

Smallest integer h≥1 for which the uniform Gaussian ensemble upper bound
C(d,σ)h^(−γ(d,σ)) is at most 0.1. The grid and color scale match figures
03 and 04. Colored hatching means the formula's sufficient budget is at
least 500; gray hatching means the formula supplies no finite sufficient
budget. This theorem calculation is uniform over bounded-degree graph
size and has no sampled graph size or random seed.

## 08 — Debate error and upper bounds

The same debate and optimal-core curves as figure 05, with the uniform
ensemble upper bound 14.57957 h^(−0.9013297) in green. The theoretical curve
uses its stated normalization, with no fitting to the empirical curves.
Bars show numerical uncertainty; shading adds approximate pointwise 95%
sampling uncertainty for the 64 draws.

## 09 — RMS lower-bound exponents

Numerically evaluated exponents δ in the lower bound
(E|debate error|²)^(1/2) ≥ c(d,σ)h^(−δ), on sufficiently deep regular
degree-d tree balls with zero unary factors. Colors show the best retained
Gaussian certificates, with a logarithmic scale capped at δ=10. Hatched cells fail the
simple condition A₀>1 of the explicit lower-bound theorem and were not
evaluated with the stronger certificates. The 193
populated cells are numerical evaluations of proved formulas, not globally
optimal exponents or outward-certified decimal values. The required depth
grows with log h; this is an RMS bound, not an expected-absolute-error bound.

## 10 — Debate error and upper/lower bounds

The same curves and parameters as figure 08, with a population lower bound
on E|D_(2h)−L_V| for the depth-eight trees in purple. It evaluates the
finite-depth RMS certificate and converts it to expected absolute error
using the optimized root-envelope tail split. At h=1,10,100 the lower
bound is approximately 0.00550, 6.79×10^−8, and 1.30×10^−12. It is not a
confidence limit for the sample mean. The calculation uses numerical
quadrature, not outward certification; its per-budget cutoffs, selected
levels, and tail thresholds are retained in `data/curves.lower.csv`.
