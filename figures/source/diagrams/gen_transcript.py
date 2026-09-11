"""Transcript figure: hidden factor graph (graph_data.py) -> sub-factor-graph
induced by a transcript S.  S = t plus six revealed claims (three per debater
over h = 3 rounds); it uses a from the core but wanders off through w, x into
the periphery.  Writes transcript-induced.tex.
"""
import math
from pathlib import Path
from graph_data import VERTS, EDGES, POS, CORE, RING, bounds

S = ("t", "a", "w", "x", "p1", "p2", "p3")
GS = 0.8
UN = 0.72          # unary factor stub length (cm)
R = 0.5            # vertex radius at GS (1.0cm vertices)
LABEL_DIR = {"a": 15, "b": 270, "c": 90}   # where the outside labels a, b, c sit

P = {v: (GS * x, GS * y) for v, (x, y) in POS.items()}
nbrs = {v: [] for v in VERTS}
for u, v in EDGES:
    nbrs[u].append(v); nbrs[v].append(u)
cx = sum(x for x, _ in P.values()) / len(P); cy = sum(y for _, y in P.values()) / len(P)


def angdist(a, b):
    d = abs((a - b + 180) % 360 - 180)
    return d


def unary_angle(v, verts):
    """Angle for v's unary stub: far from incident edges and other vertices, preferring outward."""
    x, y = P[v]
    edge_angs = [math.degrees(math.atan2(P[u][1]-y, P[u][0]-x)) for u in nbrs[v] if u in verts]
    outward = math.degrees(math.atan2(y - cy, x - cx))
    if v in LABEL_DIR:                       # keep clear of the outside label
        edge_angs.append(LABEL_DIR[v])
    best, bestscore = 0, -1e9
    for a in range(0, 360, 5):
        score = min([angdist(a, e) for e in edge_angs] + [90])
        ex, ey = x + UN * math.cos(math.radians(a)), y + UN * math.sin(math.radians(a))
        near = min(math.hypot(ex - P[u][0], ey - P[u][1]) for u in verts if u != v)
        if near < R + 0.35:
            score -= 100
        score -= 0.05 * angdist(a, outward)
        if score > bestscore:
            best, bestscore = a, score
    return best


UNARY = {v: unary_angle(v, VERTS) for v in VERTS}   # same stub angle in both panels


def pairfac(style, u, v):
    return f"\\pairfac{{{style}}}{{{u}}}{{{v}}}"


def panel(verts, tag, shift):
    out = [f"\\begin{{scope}}[shift={{({shift[0]:.3f},{shift[1]:.3f})}}]"]
    for v in verts:
        st = "target" if v == "t" else ("seen" if v in S else "hidden")
        lab = "$t$" if v == "t" else ""
        out.append(f"\\node[{st}] ({tag}{v}) at ({P[v][0]:.3f},{P[v][1]:.3f}) {{{lab}}};")
    out.append(r"\begin{scope}[on background layer]")
    for u, v in EDGES:
        if u in verts and v in verts:
            out.append(pairfac("seen" if (u in S and v in S) else "hidden", tag+u, tag+v))
    for v in verts:
        out.append(f"\\unfac{{{'seen' if v in S else 'hidden'}}}{{{tag}{v}}}{{{UNARY[v]}}}")
    out.append(r"\end{scope}")
    out.append(r"\end{scope}")
    return "\n".join(out) + "\n"


x0, x1, y0, y1 = bounds(GS)
left = panel(VERTS, "", (0, 0))
rx0 = min(P[v][0] for v in S); rx1 = max(P[v][0] for v in S)
ry0 = min(P[v][1] for v in S); ry1 = max(P[v][1] for v in S)
RSHIFT = (x1 - rx0 + 4.6, (y0 + y1) / 2 - (ry0 + ry1) / 2)
right = panel(S, "r", RSHIFT)
arrow_y = (y0 + y1) / 2
TOP = y1 + 1.1

tex = r"""\documentclass[tikz,border=10pt]{standalone}
\usetikzlibrary{arrows.meta,backgrounds,calc}
\definecolor{route}{RGB}{31,78,121}
\definecolor{corefill}{RGB}{233,239,247}
\definecolor{outside}{RGB}{120,120,120}
\begin{document}
\begin{tikzpicture}[
  >={Stealth[length=7pt,width=6pt]},
  var/.style={circle,minimum size=1.0cm,inner sep=0pt,font=\large,line width=0.8pt},
  seen/.style={var,draw=route!45,fill=white!65!corefill},
  target/.style={var,draw=route,fill=route,text=white},
  hidden/.style={var,draw=outside!55,fill=white,text=outside},
  fac/.style={rectangle,minimum size=0.26cm,inner sep=0pt,line width=0.6pt},
  seenfac/.style={fac,draw=route,fill=route},
  hiddenfac/.style={fac,draw=outside!60,fill=outside!25},
  seenedge/.style={route,line width=1.4pt},
  hiddenedge/.style={outside!45,line width=0.9pt},
  vlabel/.style={font=\large,text=route,inner sep=2pt},
  title/.style={font=\small,text=black!70}
]
\newcommand{\pairfac}[3]{\draw[#1edge] (#2)--(#3);\node[#1fac] at ($(#2)!0.5!(#3)$) {};}
\newcommand{\unfac}[3]{\draw[#1edge] (#2)--++(#3:%.2f);\node[#1fac] at ($(#2)+(#3:%.2f)$) {};}
""" % (UN, UN)
tex += "% ================= left: hidden factor graph =================\n" + left
tex += f"\\node[title] at ({(x0+x1)/2:.3f},{TOP:.3f}) {{hidden factor graph}};\n"
tex += f"\\draw[->,line width=1.2pt,black!50] ({x1+1.2:.3f},{arrow_y:.3f}) -- ({x1+3.0:.3f},{arrow_y:.3f});\n"
tex += "% ================= right: induced sub-factor-graph =================\n" + right
tex += (f"\\node[title] at ({RSHIFT[0]+(rx0+rx1)/2:.3f},{TOP:.3f}) "
        "{visible sub-factor-graph};\n")
tex += "\\end{tikzpicture}\n\\end{document}\n"
Path(__file__).with_name("transcript-induced.tex").write_text(tex)
