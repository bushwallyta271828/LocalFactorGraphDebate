# Retained plotting inputs

[Methods and numerical qualifications](METHODS.md) are self-contained.
The [statistical debate protocol](DEBATE_STATISTICS.md) gives the conditional
simultaneous-confidence argument used for the alternating-debate heatmap.

| Input | Meaning |
|---|---|
| `grid.json` | Shared 246-cell parameter grid and debate sampling declaration |
| `core_mean.json` | 1,000-draw empirical mean-core crossing brackets per cell |
| `alternating_debate.csv` | Population crossing brackets, sample sizes, censoring |
| `ensemble.csv` | Uniform mean-error theorem and sufficient-budget evaluations |
| `curves.json` | Complete 64-board paired-curve report, constants, seeds, and bounds |
| `curves*.csv` | Tabular exports of the debate, core, upper, and lower curves |
| `lower_exponents.json` | 246 selected lower-certificate rows; 193 populated |
| `endpoint_certificates.json` | Outward-verified Gaussian mixtures for the endpoint cells (5,4) and (6,8) |

The release redraws archived results; full Monte Carlo and optimization
reruns require the development archive.
