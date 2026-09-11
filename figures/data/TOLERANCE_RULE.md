# Final 1% boundary rule

The user authorized a 1% tolerance on the target mean absolute error of 0.1
and asked for a fixed rule to finish the integer colors. This is an absolute
mean-error margin of 0.001, not a fractional move count.

Keep every already resolved integer or established cutoff. For each of the
six remaining adjacent pairs [h,h+1], take the upper endpoint of the retained
sample mean-error interval at h. Choose h if this is at most 0.101; otherwise
choose h+1. This fixed rule gives five smaller-budget choices and one larger
choice at the display cutoff. The colors remain single integers throughout.

These six boundary choices are approximate. They do not claim that the
strict population threshold at 0.1 has been identified. The original strict
confidence brackets remain in the CSV, separately from `display_h` and
`display_status`. The other 240 cells retain their original simultaneous
95% confidence decisions, conditional on valid guarded numerical enclosures.
The tolerance is a display convention based on the empirical error bounds;
it is not an additional 95% guarantee for all six boundary assignments.

The CSV also retains sequential comparisons with 0.099 and 0.101. Four of
the boundary choices pass these stricter simultaneous-confidence checks;
two use the empirical tolerance rule alone. For fixed tail cutoffs and
mixture weights, lower-test factors decrease with their null threshold,
while upper-test factors increase. The possible false-rejection events
at 0.099/0.1 or 0.1/0.101 are therefore nested within each direction, so
those four confidence-qualified comparisons need no extra error allocation.
They are additional diagnostics, not a requirement of the final rule.

The long fresh control-variate run (cohort 07) was stopped and its entire
output is excluded from the publication analysis. Cohort 08 adds a small
ordinary-game check for the final two cells. Every published sample keeps
a contiguous seed prefix and all its difficult draws; repeated numerical
refinements only intersect the interval for an existing draw.
