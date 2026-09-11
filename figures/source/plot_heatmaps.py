"""The four heatmaps (03, 04, 07, 09), using only the bundled plotting data."""
import json
import math

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.patches import Rectangle
import numpy as np

import heatmap_style as style


def panel(config, values, dest, stem, censored=None, log_values=False,
          hatch_note="Colored hatching: at least the displayed h."):
    fig, ax = style.new_panel(config)
    ax.imshow(values if log_values else np.log1p(values), origin="lower", aspect="auto",
              interpolation="nearest", norm=style.NORM, cmap=style.CMAP)
    style.add_hatching(ax, np.isnan(values))
    if censored is not None:
        for y, row in enumerate(censored):
            indices = np.flatnonzero(row)
            for group in np.split(indices, np.where(np.diff(indices) != 1)[0] + 1):
                if len(group):
                    ax.add_patch(Rectangle((group[0]-.5, y-.5), len(group), 1,
                                          facecolor="none", hatch="////",
                                          edgecolor=style.HATCH, linewidth=0))
        if hatch_note is not None:
            fig.text(.065, .025, hatch_note, color=style.MUTED, fontsize=10)
    if np.isnan(values).any():
        fig.text(.855, .025, "Gray hatching: no finite bound.",
                 ha="right", color=style.MUTED, fontsize=10)
    style.colorbar(fig)
    style.save(fig, dest, stem)


def render(data, dest):
    config = json.loads((data / "grid.json").read_text())
    expected = {(d, s) for d in config["degrees"] for s in config["sigmas"]}

    def grid(rows, value):
        assert len(rows) == len(expected)
        assert {(r["d"], r["sigma"]) for r in rows} == expected
        return style.matrix(config, rows, value)

    core = json.loads((data / "core_mean.json").read_text())
    for row in core:
        row["d"] = row["degree"]
        assert row["numerical_resolved"] and row["clipped_at"] == style.COLOR_CAP
    style.setup()
    values = grid(core, lambda r: r["h_upper"])
    panel(config, values, dest, "03_core_mean", values >= style.COLOR_CAP)

    debate = style.read_csv(data / "alternating_debate.csv")
    for row in debate:
        row["d"], row["sigma"] = int(row["degree"]), float(row["sigma"])
        row["lo"] = int(row["population_h_lower"])
        row["hi"] = int(row["population_h_upper"])
        assert int(row["cap"]) == 10
        assert row["display_status"] in ("exact", "capped", "boundary_lower", "boundary_upper")
        row["display"] = int(row["display_h"])
        row["censored"] = row["display"] == 10
    values = grid(debate, lambda r: r["display"])
    panel(config, values, dest, "04_alternating_debate",
          grid(debate, lambda r: r["censored"]),
          hatch_note=None)

    upper = style.read_csv(data / "ensemble.csv")
    for row in upper:
        for key in row:
            if key in ("status", "h_approx"):
                continue
            row[key] = (None if row[key] == "" else int(row[key])
                        if key in ("d", "maximizing_m", "h_min") else float(row[key]))
        assert row["epsilon"] == .1
        assert (row["status"] == "finite") == (row["rho"] < 1)
        if row["status"] == "finite" and row["h_min"] is not None:
            h = row["h_min"]
            assert row["log_C"] - row["gamma"] * math.log(h) <= math.log(.1) + 1e-10
            if h > 1:
                assert row["log_C"] - row["gamma"] * math.log(h-1) > math.log(.1) - 1e-10
    values = grid(upper, style.upper_color_value)
    panel(config, values, dest, "07_ensemble_bound",
          values >= np.log1p(style.COLOR_CAP), log_values=True)

    lower = json.loads((data / "lower_exponents.json").read_text())
    values = grid(lower, lambda r: np.nan if r["delta"] is None else r["delta"])
    fig, ax = style.new_panel(config)
    im = ax.imshow(values, origin="lower", aspect="auto", interpolation="nearest",
                   cmap=style.EXPONENT_CMAP, norm=LogNorm(.9, 10, clip=True))
    style.add_hatching(ax, ~np.isfinite(values))
    cb = fig.colorbar(im, cax=fig.add_axes(style.COLORBAR_RECT))
    cb.set_ticks([1, 1.5, 2.5, 5, 10], labels=["1", "1.5", "2.5", "5", "≥10"])
    cb.ax.minorticks_off()
    cb.ax.tick_params(length=0, pad=7, labelsize=10)
    cb.outline.set_visible(False)
    cb.set_label("δ · RMS lower-bound exponent", labelpad=13)
    style.save(fig, dest, "09_lower_exponents")
