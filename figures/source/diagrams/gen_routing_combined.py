"""Combine routing-graph.tex and routing-tree.tex into one side-by-side figure.

Reads the two standalone sources, drops each picture's own legend (its last
scope block), and places both bodies as shifted scopes inside a single
tikzpicture (nested pictures break the background layer), with one shared
legend. Run gen_routing_graph.py first if the graph changed.
"""
import re
from pathlib import Path

HERE = Path(__file__).parent
TREE_SCALE = 1.25
TREE_SHIFT = (20.6, 5.2)        # puts the tree right of the (larger) graph


def picture(name):
    """Return (options, body) of the tikzpicture in name.tex, legend removed."""
    src = (HERE / f"{name}.tex").read_text()
    m = re.search(r"\\begin\{tikzpicture\}\[(.*?)\n\]\n(.*)\\end\{tikzpicture\}", src, re.S)
    opts, body = m.group(1).strip("\n"), m.group(2)
    i = body.rfind(r"\begin{scope}")
    j = body.rfind(r"\end{scope}") + len(r"\end{scope}")
    return opts, body[:i] + body[j:]


def colors():
    src = (HERE / "routing-graph.tex").read_text()
    return "\n".join(re.findall(r"\\definecolor\{.*?\}\{RGB\}\{.*?\}", src))


g_opts, g_body = picture("routing-graph")
t_opts, t_body = picture("routing-tree")

tex = rf"""\documentclass[tikz,border=10pt]{{standalone}}
\usetikzlibrary{{arrows.meta,backgrounds,calc,positioning}}
{colors()}
\begin{{document}}
\begin{{tikzpicture}}[
  title/.style={{font=\normalsize,text=black!60,anchor=south}},
  legendnote/.style={{font=\footnotesize,text=black!60}}
]
% ---- left panel: the graph
\begin{{scope}}[local bounding box=G,
{g_opts}
]
{g_body}\end{{scope}}
% ---- right panel: the routing tree
\begin{{scope}}[local bounding box=T,shift={{{TREE_SHIFT}}},
  scale={TREE_SCALE},transform shape,
{t_opts}
]
{t_body}\end{{scope}}

\node[title] at ([yshift=4pt]G.north) {{graph with core $K$}};
\node[title] at ([yshift=4pt]T.north |- G.north) {{routing tree of $K$}};

% One shared legend, centred under both panels.
\coordinate (L) at ($(G.south west)!0.5!(T.south east |- G.south)+(-3.4,-0.9)$);
\begin{{scope}}[shift={{(L)}},>={{Stealth[length=6pt,width=5pt]}}]
\draw[route,line width=1.6pt,->] (0,0) -- (0.95,0);
\node[legendnote,anchor=west] at (1.1,0) {{selected route}};
\draw[gate,line width=1.3pt,dash pattern=on 4pt off 2.6pt,->] (4.2,0) -- (5.15,0);
\node[legendnote,anchor=west] at (5.3,0) {{gate}};
\end{{scope}}
\end{{tikzpicture}}
\end{{document}}
"""
(HERE / "routing-combined.tex").write_text(tex)
