"""Core-oscillation figure for the post, on the larger graph of graph_data.py.

Core K = {t,a,b,c}, Gaussian tables with a fixed seed, exact log-odds L_S;
the graph has 14 periphery vertices hanging off the outer ring.  Exact L_S uses
variable elimination (factor_model.py); all 2^18 supersets S of K are
enumerated for the extremes, and a random sample of them is drawn as dots.
Writes core-oscillation-A.tex; build with tectonic, pdftocairo for PNG.
"""
import itertools, random
from pathlib import Path
from graph_data import VERTS, EDGES, POS, CORE, RING, bounds
from factor_model import draw_tables, make_L

SEED, SIGMA, FIELD = 248, 1.3, 1.0
NDOTS = 60
R, PAD = 0.65, 0.3
K = CORE

theta, phi = draw_tables(SEED, SIGMA, FIELD)
L = make_L(theta, phi)


def supersets(K):
    rest = [v for v in VERTS if v not in K]
    for r in range(len(rest) + 1):
        for extra in itertools.combinations(rest, r):
            yield tuple(sorted(K + extra))


allS = list(supersets(K))
vals = [L(S) for S in allS]
order = sorted(range(len(allS)), key=vals.__getitem__)
lo, hi = vals[order[0]], vals[order[-1]]
Smin, Smax = allS[order[0]], allS[order[-1]]
LV = L(tuple(sorted(VERTS)))


def component(S):
    """Vertices of S reachable from t within S; the rest cannot affect L_S."""
    S = set(S); seen = {"t"}; stack = ["t"]
    while stack:
        u = stack.pop()
        for a_, b_ in EDGES:
            for p_, q_ in ((a_, b_), (b_, a_)):
                if p_ == u and q_ in S and q_ not in seen:
                    seen.add(q_); stack.append(q_)
    return tuple(sorted(seen))


Smax, Smin = component(Smax), component(Smin)
assert abs(L(Smax) - hi) < 1e-9 and abs(L(Smin) - lo) < 1e-9
rng = random.Random(SEED)
dots = sorted(rng.sample(vals, NDOTS)) + [lo, hi]

PREAMBLE = r"""\documentclass[tikz,border=10pt]{standalone}
\usepackage{amsmath}
\usetikzlibrary{arrows.meta,backgrounds,calc,positioning,decorations.pathreplacing}
\definecolor{route}{RGB}{31,78,121}
\definecolor{gate}{RGB}{196,64,44}
\definecolor{corefill}{RGB}{233,239,247}
\definecolor{outside}{RGB}{120,120,120}
\definecolor{setfill}{RGB}{242,246,251}
\begin{document}
\begin{tikzpicture}[
  >={Stealth[length=6pt,width=5pt]},
  title/.style={font=\normalsize,text=black!60,anchor=south},
  note/.style={font=\footnotesize,text=black!60},
]
"""
POSTAMBLE = "\\end{tikzpicture}\n\\end{document}\n"


def hull(pts):
    pts = sorted(set(pts))
    if len(pts) <= 2:
        return pts
    def cross(o, a, b):
        return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])
    lo_, up = [], []
    for p in pts:
        while len(lo_) >= 2 and cross(lo_[-2], lo_[-1], p) <= 0: lo_.pop()
        lo_.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0: up.pop()
        up.append(p)
    return lo_[:-1] + up[:-1]


def graph(S, K, origin, s, labels=True, corelabel=None, tag="", plain=False):
    """TikZ for the graph with core K and transcript S, drawn at scale s.

    plain: every vertex drawn as present (the 'graph with core K' panel).
    Otherwise vertices in S are solid and lightly filled, others dashed."""
    ox, oy = origin
    P = {v: (ox + s*x, oy + s*y) for v, (x, y) in POS.items()}
    pt = lambda v: f"({P[v][0]:.3f},{P[v][1]:.3f})"
    size = 1.3 * s
    lw = 0.8 * (s ** 0.5)
    font = {True: r"\large", False: r"\scriptsize"}[s > 0.6]
    out = [f"\\begin{{scope}}[vertex/.style={{circle,minimum size={size:.3f}cm,inner sep=0pt,font={font}}}]",
           r"\begin{scope}[on background layer]"]
    hp = hull([P[v] for v in K])
    pad = 2 * (R + PAD) * s
    poly = " -- ".join(f"({x:.3f},{y:.3f})" for x, y in hp) + " -- cycle"
    out.append(f"\\fill[corefill] {poly};")
    out.append(f"\\draw[corefill,line width={pad:.3f}cm,line join=round] {poly};")
    for u, v in EDGES:
        inK = u in K and v in K
        inS = u in S and v in S
        if inS or plain:
            col = "route!45" if inK else "outside!55"
            out.append(f"\\draw[{col},line width={lw:.2f}pt] {pt(u)} -- {pt(v)};")
        else:
            out.append(f"\\draw[outside!30,line width={lw*0.8:.2f}pt,dash pattern=on 2pt off 2pt] {pt(u)} -- {pt(v)};")
    for v in VERTS:
        lab = "$t$" if labels and v == "t" else ""
        if v == "t":
            st = f"draw=route,fill=route,text=white,line width={lw:.2f}pt"
        elif v in K:
            st = f"draw=route!45,fill=white!65!corefill,line width={lw:.2f}pt"
        elif plain:
            st = f"draw=outside!60,fill=white,text=outside,line width={lw:.2f}pt"
        elif v in S:
            st = f"draw=outside!60,fill=corefill,line width={lw:.2f}pt"
        else:
            st = f"draw=outside!45,fill=white,text=outside!70,line width={lw*0.8:.2f}pt,dash pattern=on 2pt off 2pt"
        out.append(f"\\node[vertex,{st}] ({tag}{v}) at {pt(v)} {{{lab}}};")
    out.append(r"\end{scope}")
    if labels:
        out.append(f"\\node[note,anchor=north] at ($({tag}t.south)+(0,-2pt)$) {{target}};")
    if corelabel:
        cx, cy = ox + s*4.75, oy + s*1.4
        out.append(f"\\node[note,text=route!80] at ({cx:.3f},{cy:.3f}) {{{corelabel}}};")
    out.append(r"\end{scope}")
    return "\n".join(out) + "\n"


def vaxis(x, y0, y1, lo, hi, vals, bx=0.45):
    m = 0.18 * (hi - lo)
    f = lambda v: y0 + (y1 - y0) * (v - (lo - m)) / ((hi + m) - (lo - m))
    out = [f"\\fill[corefill] ({x-0.28:.3f},{f(lo):.3f}) rectangle ({x+0.28:.3f},{f(hi):.3f});",
           f"\\draw[black!50,line width=0.8pt,->] ({x:.3f},{y0:.3f}) -- ({x:.3f},{y1+0.35:.3f});",
           f"\\node[note,anchor=south] at ({x:.3f},{y1+0.4:.3f}) {{$L_S$}};"]
    for v in vals:
        out.append(f"\\fill[route] ({x:.3f},{f(v):.3f}) circle (1.6pt);")
    out.append(f"\\draw[route,line width=0.9pt] ({x-0.28:.3f},{f(hi):.3f}) -- ({x+0.28:.3f},{f(hi):.3f});")
    out.append(f"\\draw[route,line width=0.9pt] ({x-0.28:.3f},{f(lo):.3f}) -- ({x+0.28:.3f},{f(lo):.3f});")
    out.append(f"\\node[note,anchor=west,text=route] at ({x+0.36:.3f},{f(hi):.3f}) {{$\\max L_S$}};")
    out.append(f"\\node[note,anchor=west,text=route] at ({x+0.36:.3f},{f(lo):.3f}) {{$\\min L_S$}};")
    out.append(f"\\draw[decorate,decoration={{brace,amplitude=5pt}},route,line width=0.8pt] ({x+bx:.3f},{f(hi):.3f}) -- ({x+bx:.3f},{f(lo):.3f}) node[midway,xshift=10pt,anchor=west,font=\\normalsize,text=route] {{$\\osc(K)$}};")
    return "\n".join(out) + "\n", f


# ================================================================ layout
GS = 0.8
x0, x1, y0, y1 = bounds(GS)
TOP = y1 + 0.9                         # title baseline
body = graph(K, K, (0, 0), GS, labels=True, corelabel="core $K$", plain=True)
body += f"\\node[title] at ({(x0+x1)/2:.3f},{TOP:.3f}) {{graph with core $K$}};\n"

TS = 0.22
tx0, tx1, ty0, ty1 = bounds(TS)
tx = x1 + 1.6 - tx0                    # thumbnail origin x
ys = [2.9, -1.9]
AX = tx + tx1 + 2.4
thumbs = [Smax, Smin]
caps = ["$S$ attaining $\\max L_S$", "$S$ attaining $\\min L_S$"]
ax, f = vaxis(AX, -2.6, 4.2, lo, hi, dots, bx=1.5)
for i, (S, y, cap) in enumerate(zip(thumbs, ys, caps)):
    body += graph(S, K, (tx, y), TS, labels=False, tag=f"s{i}")
    body += f"\\node[note,anchor=north] at ({tx+TS*(x0+x1)/2/GS:.3f},{y+ty0-0.1:.3f}) {{{cap}}};\n"
    body += (f"\\draw[black!35,line width=0.6pt,dash pattern=on 2pt off 2pt] ({tx+tx1+0.35:.3f},{y:.3f}) "
             f".. controls ({tx+tx1+1.3:.3f},{y:.3f}) and ({AX-1.2:.3f},{f(L(S)):.3f}) .. ({AX-0.3:.3f},{f(L(S)):.3f});\n")
body += f"\\node[title] at ({tx+TS*(x0+x1)/2/GS:.3f},{TOP:.3f}) {{transcripts $S\\supseteq K$}};\n"
body += f"\\node[title] at ({AX:.3f},{TOP:.3f}) {{judge's log-odds}};\n"
body += ax
tex = PREAMBLE + r"\providecommand{\osc}{\operatorname{osc}}" + "\n" + body + POSTAMBLE
(Path(__file__).parent / "core-oscillation-A.tex").write_text(tex)
print(f"osc(K)={hi-lo:.3f} lo={lo:.3f} hi={hi:.3f} LV={LV:.3f}  |supersets|={len(allS)}")
print("Smax extras:", [v for v in Smax if v not in K])
print("Smin extras:", [v for v in Smin if v not in K])
