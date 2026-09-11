"""Shared heatmap style and retained ensemble-table validation."""
import csv
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.patches import Rectangle
import numpy as np

BG = "#ffffff"
INK = "#29232e"
MUTED = "#655f69"
UNKNOWN = "#e6e5e3"
HATCH = "#c1bebf"
CMAP = plt.get_cmap("magma")
EXPONENT_CMAP = plt.get_cmap("Blues")
# Keep the heatmap's physical dimensions while removing title/caption margins.
FIGURE_SIZE = (14.4, 3.85)
MAP_RECT = [.065, .22, .79, .735]
COLORBAR_RECT = [.885, .22, .016, .735]
# Both budget maps display h = |K|-1, capped at 500 moves per debater.
COLOR_CAP = 500
NORM = Normalize(0, math.log1p(COLOR_CAP), clip=True)


def read_csv(path):
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def setup():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                         "text.color": INK, "axes.labelcolor": INK,
                         "xtick.color": MUTED, "ytick.color": MUTED,
                         "figure.facecolor": BG, "axes.facecolor": BG,
                         "hatch.linewidth": .6})


def new_panel(config):
    fig = plt.figure(figsize=FIGURE_SIZE)
    ax = fig.add_axes(MAP_RECT)
    ticks = range(0, len(config["sigmas"]), 4)
    labels = ["1/32", "1/16", "1/8", "1/4", "1/2", "1", "2", "4", "8", "16", "32"]
    ax.set_xticks(list(ticks), labels)
    ax.set_yticks(range(len(config["degrees"])), config["degrees"])
    ax.set_xlim(-.5, len(config["sigmas"]) - .5)
    ax.set_ylim(-.5, len(config["degrees"]) - .5)
    ax.set_xlabel("Edge-table standard deviation σ", labelpad=12)
    ax.set_ylabel("Degree d", labelpad=10)
    ax.tick_params(length=0, pad=9)
    for spine in ax.spines.values():
        spine.set_color("#d0cbce")
        spine.set_linewidth(.6)
    return fig, ax


def matrix(config, rows, value):
    lookup = {(r["d"], r["sigma"]): r for r in rows}
    return np.array([[value(lookup[d, s]) for s in config["sigmas"]] for d in config["degrees"]])


def add_hatching(ax, mask):
    for y in range(mask.shape[0]):
        indices = np.flatnonzero(mask[y])
        for group in np.split(indices, np.where(np.diff(indices) != 1)[0] + 1):
            if len(group):
                ax.add_patch(Rectangle((group[0] - .5, y - .5), len(group), 1,
                                       facecolor=UNKNOWN, hatch="////", edgecolor=HATCH, linewidth=0))


def colorbar(fig):
    cax = fig.add_axes(COLORBAR_RECT)
    cb = fig.colorbar(plt.cm.ScalarMappable(norm=NORM, cmap=CMAP), cax=cax)
    ticks = [0, 1, 5, 10, 50, 100, COLOR_CAP]
    cb.set_ticks(np.log1p(ticks), labels=[str(t) if t != COLOR_CAP else "≥500" for t in ticks])
    cb.ax.tick_params(length=0, pad=7, labelsize=10)
    cb.outline.set_visible(False)
    cb.set_label("h · moves per debater", labelpad=13)


def save(fig, dest, stem):
    fig.savefig(dest / f"{stem}.png", dpi=200)
    plt.close(fig)


def upper_color_value(row):
    if row["status"] != "finite":
        return float("nan")
    # Compute log(1+h) without overflowing at h = 10^954 and beyond.
    return float(np.logaddexp(0, math.log(10) * row["log10_h"]))
