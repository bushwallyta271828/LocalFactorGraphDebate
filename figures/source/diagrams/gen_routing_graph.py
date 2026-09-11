"""Generate the routing graph with route strands ending in arrowheads.

The periphery vertices of graph_data.py are drawn (unlabelled) around the
outer ring; they do not change the routes or gates of the core.

All vertices are the same size. Each selected route is one continuous blue
strand that ends in an arrowhead at its endpoint vertex; a dashed red gate
departs from that arrowhead tip and ends on the boundary of the vertex it
would step to. Build with tectonic or pdflatex, then export with pdftocairo
(-r 300 for PNG).
"""
from math import hypot
from pathlib import Path
from graph_data import POS, EDGES, PERIPHERY, RING

# ---------------------------------------------------------------- geometry
R = 0.65                                # common vertex radius (cm)
LANE = 0.2                              # spacing between parallel strands
PAD = 0.3                               # core region margin around vertex disks
T, A, B, C = (0.0, 0.0), (3.0, 2.0), (3.0, -2.0), (6.0, 0.0)
W, X, Y, Z = (-2.5, 1.3), (2.1, 4.15), (9.15, 1.5), (9.15, -1.8)


def unit(p, q):
    dx, dy = q[0] - p[0], q[1] - p[1]
    n = hypot(dx, dy)
    return dx / n, dy / n


def perp(d):
    return -d[1], d[0]


def lane_point(origin, d, k, s):
    """Point at arclength s along the lane offset k*perp(d) from origin."""
    n = perp(d)
    return origin[0] + k * n[0] + s * d[0], origin[1] + k * n[1] + s * d[1]


def lane_at_x(origin, d, k, x):
    n = perp(d)
    s = (x - origin[0] - k * n[0]) / d[0]
    return lane_point(origin, d, k, s)


def lane_cross(o1, d1, k1, o2, d2, k2):
    """Intersection of lane (o1,d1,k1) with lane (o2,d2,k2)."""
    n1, n2 = perp(d1), perp(d2)
    p = (o1[0] + k1 * n1[0], o1[1] + k1 * n1[1])
    q = (o2[0] + k2 * n2[0], o2[1] + k2 * n2[1])
    det = d1[0] * (-d2[1]) - d1[1] * (-d2[0])
    rx, ry = q[0] - p[0], q[1] - p[1]
    s = (rx * (-d2[1]) - ry * (-d2[0])) / det
    return p[0] + s * d1[0], p[1] + s * d1[1]


D1 = unit(T, A)          # t -> a (also b -> c)
D2 = unit(T, B)          # t -> b
FAN = 0.45               # strands start here, just inside t's disk
X_TAB, X_TABC = 3.15, 3.35  # the two verticals through a and b
BC0 = (3.0, -2.15)       # centre line of the b -> c pair passes here

# t -> a lanes: ta on top, tabc in the middle, tab at the bottom.
ta_fan = lane_point(T, D1, +LANE, FAN)
ta_tip = lane_point(T, D1, +LANE, 3.45)
tabc_fan = lane_point(T, D1, 0.0, FAN)
tabc_c1 = lane_at_x(T, D1, 0.0, X_TABC)
tab_fan = lane_point(T, D1, -LANE, FAN)
tab_c1 = lane_at_x(T, D1, -LANE, X_TAB)
tab_tip = (X_TAB, -1.88)
# t -> b lanes: tb above, tbc below.
tb_fan = lane_point(T, D2, +LANE / 2, FAN)
tb_tip = lane_point(T, D2, +LANE / 2, 3.25)
tbc_fan = lane_point(T, D2, -LANE / 2, FAN)
tbc_c1 = lane_cross(T, D2, -LANE / 2, BC0, D1, -LANE / 2)
tbc_tip = lane_at_x(BC0, D1, -LANE / 2, 5.8)
tabc_c2 = lane_at_x(BC0, D1, +LANE / 2, X_TABC)
tabc_tip = lane_at_x(BC0, D1, +LANE / 2, 6.2)


PER_NODES = "\n".join(f"\\node[outer] ({v}) at ({POS[v][0]:.3f},{POS[v][1]:.3f}) {{}};" for v in PERIPHERY)
PER_EDGES = "\\draw[outside!55,line width=0.8pt] " + " ".join(
    f"({u}) -- ({v})" for u, v in EDGES if u in PERIPHERY or v in PERIPHERY) + ";"
periphery = PER_NODES + "\n" + PER_EDGES


def pt(p):
    return f"({p[0]:.3f},{p[1]:.3f})"


def path(*pts):
    return " -- ".join(pt(p) for p in pts)


tex = rf"""\documentclass[tikz,border=10pt]{{standalone}}
\usetikzlibrary{{arrows.meta,backgrounds,calc}}
\definecolor{{route}}{{RGB}}{{31,78,121}}
\definecolor{{gate}}{{RGB}}{{196,64,44}}
\definecolor{{corefill}}{{RGB}}{{233,239,247}}
\definecolor{{outside}}{{RGB}}{{120,120,120}}
\begin{{document}}
\begin{{tikzpicture}}[
  >={{Stealth[length=6pt,width=5pt]}},
  vertex/.style={{circle,minimum size={2*R}cm,inner sep=0pt,font=\large}},
  core/.style={{vertex,draw=route!45,fill=white!65!corefill,line width=0.8pt}},
  target/.style={{vertex,draw=route,fill=route,text=white,line width=0.8pt}},
  outer/.style={{vertex,draw=outside!60,fill=white,text=outside,line width=0.8pt}},
  strand/.style={{route,line width=1.6pt,rounded corners=5pt,->}},
  gateedge/.style={{gate,line width=1.3pt,dash pattern=on 4pt off 2.6pt,->,
                   shorten <=2pt,shorten >=1pt}},
  vlabel/.style={{font=\large,text=route,inner sep=2pt}},
  glabel/.style={{font=\small,text=gate,inner sep=2pt}},
  note/.style={{font=\footnotesize,text=black!60}}
]
% Vertices (all the same size) sit behind the strands.
\begin{{scope}}[on background layer]
% Core region: the convex hull of the core vertices, padded by PAD.
\fill[corefill] {pt(T)} -- {pt(A)} -- {pt(C)} -- {pt(B)} -- cycle;
\draw[corefill,line width={2*(R+PAD)}cm,line join=round]
  {pt(T)} -- {pt(A)} -- {pt(C)} -- {pt(B)} -- cycle;
\node[target] (t) at {pt(T)} {{$t$}};
\node[core]   (a) at {pt(A)} {{}};
\node[core]   (b) at {pt(B)} {{}};
\node[core]   (c) at {pt(C)} {{}};
\node[outer]  (w) at {pt(W)} {{$w$}};
\node[outer]  (x) at {pt(X)} {{$x$}};
\node[outer]  (y) at {pt(Y)} {{$y$}};
\node[outer]  (z) at {pt(Z)} {{$z$}};
\draw[outside!55,line width=0.8pt] (w) -- (x)  (y) -- (z);
{periphery}
\end{{scope}}
\node[note,text=route!80] at (4.75,1.4) {{core $K$}};
\node[note,anchor=north] at ($(t.south)+(0,-2pt)$) {{target}};
\node[vlabel,anchor=west]  at ($(a.east)+(3pt,4pt)$) {{$a$}};
\node[vlabel,anchor=north] at ($(b.south)+(0,-2pt)$) {{$b$}};
\node[vlabel,anchor=south] at ($(c.north)+(0,2pt)$) {{$c$}};

% Each blue strand is one selected route; the arrowhead marks its endpoint.
\draw[strand] {path(ta_fan, ta_tip)};
\draw[strand] {path(tab_fan, tab_c1, tab_tip)};
\draw[strand] {path(tabc_fan, tabc_c1, tabc_c2, tabc_tip)};
\draw[strand] {path(tb_fan, tb_tip)};
\draw[strand] {path(tbc_fan, tbc_c1, tbc_tip)};

% Gates leave from the arrowhead of the route that owns them and
% end on the boundary of the vertex they would step to.
\draw[gateedge] (t) -- (w) node[glabel,pos=0.55,above=3pt] {{$g_1$}};
\draw[gateedge] {pt(ta_tip)} -- (x) node[glabel,pos=0.6,left=3pt] {{$g_2$}};
\draw[gateedge] {pt(tb_tip)} .. controls (2.45,-0.7) and (2.45,0.6) .. (a.-100)
  node[glabel,pos=0.5,left=4pt] {{$g_3$}};
\draw[gateedge] {pt(tabc_tip)} .. controls (6.8,0.9) and (8.2,1.5) .. (y.195)
  node[glabel,pos=0.6,above=3pt] {{$g_5$}};
\draw[gateedge] {pt(tabc_tip)} .. controls (7.45,0.4) and (8.15,-1.2) .. (z.145)
  node[glabel,pos=0.72,above right=1pt] {{$g_7$}};
\draw[gateedge] {pt(tbc_tip)} .. controls (6.7,-1.1) and (8.2,-1.85) .. (z.175)
  node[glabel,pos=0.6,below=3pt] {{$g_6$}};
\draw[gateedge] {pt(tbc_tip)} .. controls (7.45,-0.8) and (8.15,0.9) .. (y.225)
  node[glabel,pos=0.7,below=3pt] {{$g_4$}};

\begin{{scope}}[shift={{(1.4,-7.2)}}]
\draw[strand] (0,0) -- (0.95,0);
\node[note,anchor=west] at (1.1,0) {{selected route}};
\draw[gateedge] (4.2,0) -- (5.15,0);
\node[note,anchor=west] at (5.3,0) {{gate}};
\end{{scope}}
\end{{tikzpicture}}
\end{{document}}
"""

Path(__file__).with_name("routing-graph.tex").write_text(tex)
