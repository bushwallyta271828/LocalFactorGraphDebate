# Methods and interpretation

These notes describe the retained campaigns. Rebuilding the figures reads
saved summaries; it does not rerun their original solvers. All numerical
errors are measured against the full logit of the declared **finite** tree.
The target is initially present, and h always means moves **per player**.
All four entries of every edge table are iid N(0,σ²); all unary factors in
the empirical panels are zero.

## Shared parameter grid

The heatmaps have 246 cells: d=3,…,8 and σ=2^(j/4), j=−20,…,20. The three
budget panels share a nonlinear color scale and a display cap of 500.
Equal colors mean equal displayed budgets, not equal statistical precision.
For the lower-exponent panel, the separate logarithmic scale runs from
δ=0.9 to δ=10, with all larger values sharing the last color.

## 03: mean optimal-core oscillation

Each cell has 1,000 paired Gaussian-table draws on a breadth-first regular
degree-d tree stopped at **50,000 vertices**, with a partially filled last
shell. The root has d children and other internal vertices at most d−1.
On each board the optimization ranges over connected cores containing t
with at most h non-target vertices. A core's completion interval is computed
by exact tree message recursions; budgeted optimization retains lower and
upper numerical bounds on the minimum interval width. The campaign uses
streaming Pareto/frontier optimization and progressively refined bound
representations for difficult boards. Every declared draw remains in the
means, including failed attempts represented by bounds.

The statistic is the first h for which the **sample mean of the optimal
oscillations** is at most 0.1, clipped at 500. It is not the mean of the
per-board first successful budgets. The stored `h_lower` and `h_upper` bracket
this empirical crossing numerically. The displayed color is `h_upper`.
All 246 cells met the campaign's numerical tolerance, which allowed a gap
of max(1,ceil(1% of h_lower)); it did not require a unique integer crossing.
The widest retained numerical bracket is five budget units.

The normal-approximation sampling columns in `core_mean.json` are separate,
descriptive, pointwise quantities. They are not simultaneous confidence
statements. `numerical_resolved` describes optimization precision and does
not establish that the population crossing is known. Hatching at 500 is
censoring, not a demonstrated phase boundary or a successful budget of 500.

## 04: alternating debate

Every board has exactly 50,000 vertices, matching figure 03. The next
complete degree-d ball is pruned by uniformly selecting the required number
of final-shell vertices. The depths for d=3,...,8 are 15, 10, 8, 7, 6, and 6.
The seed for draw i at degree d is `20250308+100000*d+i`, paired across
noise scales. The first 1,000 boards match figure 03 exactly. Additional
samples extend contiguous prefixes separately at each budget;
`alternating_debate.csv` records the resulting sample counts and decisions.

Max moves first, Min last, each naming h distinct vertices. Numerical
strategy bounds enclose each optimal game value. Exhaustive enumeration
handles one round; budgeted forcing and adaptive-ending strategies bound
longer games. Error lower/upper endpoints follow by taking distance from
the full-model logit to the game interval. The computations use guarded
double precision, **not** outward interval arithmetic.

The target statistic is the first integer h with population mean absolute
error **strictly below** 0.1, among legal budgets. Error monotonicity is not
assumed: an unresolved earlier budget cannot be skipped when determining
a first crossing. Sequential e-value tests combine bounded truncation with
an analytic Gaussian tail bound and allocate error across all 246 cells,
both tests, and budgets h=0,…,9. They give at least 95% simultaneous coverage
conditional on validity of the numerical enclosures. The complete argument
is retained in [DEBATE_STATISTICS.md](DEBATE_STATISTICS.md).

Every displayed value is an integer. Six boundary cells apply the 1%
mean-error tolerance described in [TOLERANCE_RULE.md](TOLERANCE_RULE.md). Hatching establishes h>=10: it does
not establish success at h=10. Every earlier budget must be excluded before
a minimum is identified, and no unresolved bracket receives a midpoint
color. An analytic Gaussian root-field bound resolves the zero-move case.
This population analysis differs from the core panel's sample-mean crossing;
both panels now use the same finite-tree ensemble.

## 05, 08, 10: paired error curves

All three plots use d=4, σ=0.35, depth 8, 13,121 vertices, and 64 boards with
seeds 7–70, paired across budgets and between debate and core optimization.
Debate horizons are 1,2,3,5,7,10,15,20,30,40,50,65,80,100; optimal cores
cover every integer h=1,…,100. Exact combinatorial core dynamic programming
is evaluated in floating point. The 6,400 core minima have relative numerical
gaps below 1.4×10^−8. Debate errors use numerical strategy enclosures; the
largest mean interval half-width is about 10.75% of its midpoint, at h=100.
No difficult board is omitted.

Bars describe numerical uncertainty in the empirical debate mean. Shading
adds approximate pointwise 95% sampling bands from 64 draws. Those bands
are not simultaneous over budgets. The orange curve averages optimized
core oscillations on the same boards, so the deterministic core inequality
has a direct paired interpretation here.

The green curve is the uniform bound 14.57957 h^(−0.9013297), with constants
computed by quadrature and no fitted normalization. The purple curve is a
**population mean absolute-error lower bound** on these depth-eight trees.
For every h it searches 81 cutoff candidates across linear/quadratic
truncations, refines quadrature from order 48 to 96, optimizes over the
available levels n=0,…,7, and then optimizes the root-envelope tail split.
The largest retained relative quadrature refinement change is about 6.1×10^−13.
Per-budget parameters and thresholds are in `curves.lower.csv`, also embedded
in `curves.json`. This is numerical evaluation of a proved inequality, not
outward certification and not a confidence limit on the sample mean.

## 07: ensemble sufficient budgets

`ensemble.csv` evaluates the manuscript's C(d,σ) h^(−γ(d,σ)) at each grid
point and stores the least integer h≥1 satisfying the 0.1 target whenever
ρ<1. Calculations use logarithms for extremely large budgets. The theorem
is uniform over finite bounded-degree graphs and arbitrary fixed unary
factors; no random graph or graph-size parameter is used here. A gray cell
means the formula supplies no decaying bound, not that debate fails.

## 09: lower-bound exponents

`lower_exponents.json` stores the 246 selected rows from the theorem-gallery
calculation. Of these, 191 populated cells use the analytic widening choice
τ=d+2/σ² and the recorded linear or quadratic cutoff. Two cells, (d,σ)=(5,4)
and (6,8), use the retained untruncated endpoint mixtures in
`endpoint_certificates.json`, reduced by the multiplicative truncation loss
proved in the manuscript. The other 53 cells fail the simple condition
A₀>1 of the explicit lower-bound theorem and were not evaluated with the
stronger certificates; that is not a mathematical impossibility result.

For every populated cell the recorded λ, a, B, cutoff, response variance,
and τ define δ=−log(B)/log(a). The interpretation is RMS≥c h^(−δ) on
sufficiently deep regular tree balls, with the required depth growing like
log h. These are the best retained choices in that calculation, not a global
optimization over all certificates. The endpoint parameters have archived
outward verification; the derived decimal exponents are numerical. A
smaller exponent is stronger asymptotically, but prefactors can reverse a
comparison at a given finite budget.
