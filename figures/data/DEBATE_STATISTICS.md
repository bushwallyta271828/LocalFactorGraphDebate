# Population precision for the alternating-debate heatmap

The target is `H = min {h >= 0: E |V_h - L_full| < 0.1}` on the declared
50,000-vertex partially filled regular tree. Max moves first, Min last, and each names
exactly h distinct vertices. The target is initially present. No monotonicity
of error in h is assumed. Displaying a cutoff C means `min(H,C)`; the last
color means **at least C**, not a demonstrated successful budget C.
The minimum ranges over legal budgets `0 <= h <= floor((N-1)/2)`, with
`H=infinity` if no budget succeeds.

## Numerical enclosures

The solver retains `lo <= V_h <= hi` for every draw. This gives the error
interval `[max(0,lo-L,L-hi), max(abs(lo-L),abs(hi-L))]`. Existing budgeted
forcing and short adaptive-ending algorithms provide legal strategy bounds.
Global arbitrary-completion forcing supplies additional bounds. One round
is evaluated by exhaustive enumeration of all distinct relevant moves,
with up to two real remote vertices representing irrelevant moves. The
full truth always uses the full ambient tree.

The policy-only tree omits unused search masks but keeps the full geometry
and the identical Gaussian generator. Independent small-game comparisons
check the sampling, one-round reduction, and strategy containment.

All computations use guarded double precision. They are not outward
interval-arithmetic certificates. The statistical guarantees below are
conditional on the numerical enclosures being valid.

## A deterministic Gaussian tail bound

For one root edge put `A=t10-t00`, `B=t11-t01`. Every present-edge message
lies between A and B, regardless of the selected descendants; an absent
edge sends zero. Hence every judge value, including full truth and every
minimax value, lies in the same root interval, of width

```
W = sum_root_edges [max(0,A,B) - min(0,A,B)].
```

In particular the actual absolute error X satisfies `0 <= X <= W`.
Each summand is the maximum of six centered Gaussian linear forms
`A,-A,B,-B,A-B,B-A`, each with variance at most `4 sigma^2`.
The sum is the maximum of `6^d` centered Gaussian forms of variance at
most `4 d sigma^2`. Independence is used only between distinct root-edge
tables. A Gaussian Chernoff bound and an integral bound give, for b>0,

```
P(W > b) <= 6^d exp(-b^2/(8 d sigma^2)),
E[(X-b)+] <= E[(W-b)+]
            <= 6^d (4 d sigma^2/b) exp(-b^2/(8 d sigma^2)).
```

This controls unseen Gaussian tails analytically; it does not assume that
the largest observed error is the population maximum. The code chooses b
to make the last expression at most each of four predeclared tail allowances
`0.01, 0.001, 0.0001, 0.000001`.

## Anytime-valid tests of the mean threshold

For iid errors X_i>=0, under the null `E X <= epsilon`, each fixed product

```
M_n(lambda) = product_i [1 + lambda (X_i-epsilon)],
0 <= lambda <= 1/epsilon,
```

is a nonnegative supermartingale starting at one: each new multiplier has
conditional expectation at most one. Thus the probability that it ever
reaches 1/alpha is at most alpha (the elementary maximal inequality for
nonnegative supermartingales). A fixed convex mixture has the same property.
The lower test uses equal weights on `lambda=rho/epsilon` with

```
rho = .000001,.000002,.000005,.00001,.00002,.00005,.0001,.0002,.0005,
      .001,.002,.005,.01,.02,.05,.1,.2,.4,.6,.8,.95.
```

To reject `E X >= epsilon`, use `Y=min(X,b)` and a tail allowance tau.
That null implies `E Y >= epsilon-tau`. The products

```
product_i [1 + lambda (Y_i-(epsilon-tau))],
lambda = -rho/(b-(epsilon-tau)),
```

are again nonnegative supermartingales under the null. Mix equally over
all four (b,tau) pairs and the 21 rho values. These are explicit tests
for the original unbounded mean, not for an altered clipped-error target.

The lower test substitutes numerical error lower endpoints into its
increasing multipliers. The upper test substitutes clipped upper endpoints
into its decreasing multipliers. Each computed e-value is consequently no
larger than the corresponding hypothetical e-value computed from the true
errors. This domination holds pointwise for every sample size, regardless
of how solver refinements were selected or timed. It permits adaptive
refinement without asserting that the solver endpoints themselves form an
iid observable. No board is removed because it is difficult or slow.

The declaration reserves a 246-cell grid (six degrees and 41 noise scales),
and both tests at every integer h=0,...,9.
Each test receives `alpha=0.05/(246*10*2)`.
A union bound gives simultaneous coverage at least 95% across the entire
grid, every tested budget, and every sample-prefix stopping time. Pairing
draws between scales does not invalidate the union bound. Larger sample
sizes are contiguous prefixes of the same independent cohort.
The replay retains the largest mixture e-value over every available sample
prefix, so a previously established rejection is not lost when more draws
arrive. Numerical refinements can retrospectively improve the endpoint
enclosures at those prefixes; pointwise domination still applies.

Population tests may use different prefix lengths at different budgets.
The separate empirical crossing columns use the smallest common sample
prefix across the available budgets, so they describe one actual cohort.

## Turning tests into a round-count interval

A successful lower test establishes mean error above 0.1 and excludes that
budget. A successful upper test establishes mean error below 0.1.
The lower endpoint for H is the earliest integer not excluded. Its upper
endpoint is the earliest established success. Clip both endpoints at C.
Unknown or missing budgets cannot be silently skipped. A later passing
budget does not establish that an earlier unresolved budget fails.

The final publication rule keeps the 240 strict decisions and assigns six
adjacent boundary cells approximately using a 1% empirical mean-error
tolerance. Choose the smaller budget when its sample mean-error upper
endpoint is at most 0.101; otherwise choose the larger budget. The strict
confidence brackets remain separate from `display_h`. This display rule
does not give a 95% confidence claim for all six approximate assignments.
See [TOLERANCE_RULE.md](TOLERANCE_RULE.md) for the full convention.

An additional deterministic Gaussian root-field argument resolves h=0;
its derivation is retained in [NO_DEBATE_BOUND.md](NO_DEBATE_BOUND.md).
This bound spends no statistical error probability. Game refinements include
longer adaptive endings and full-game threshold queries, always intersected
with the retained interval for the same draw.
