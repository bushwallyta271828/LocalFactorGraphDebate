"""Shared graph for the diagram figures.

The first eight vertices form the core K = {t,a,b,c} and the outer ring
w,x,y,z.  The periphery p1..p14 attaches only to the outer ring and to
itself, never to the core, so every route and gate of K is determined by
the first eight vertices.  Coordinates are in the frame
of routing-graph.tex (t at the origin, c at (6,0)).
"""

CORE = ("t", "a", "b", "c")
RING = ("w", "x", "y", "z")
PERIPHERY = tuple(f"p{i}" for i in range(1, 15))
VERTS = list(CORE + RING + PERIPHERY)

POS = {
    "t": (0.0, 0.0), "a": (3.0, 2.0), "b": (3.0, -2.0), "c": (6.0, 0.0),
    "w": (-2.5, 1.3), "x": (2.1, 4.15), "y": (9.15, 1.5), "z": (9.15, -1.8),
    "p1": (-5.4, -0.2), "p2": (-4.8, 3.5), "p3": (-1.7, 6.1), "p4": (2.3, 7.1),
    "p5": (5.7, 6.3), "p6": (8.7, 4.7), "p7": (12.2, 3.6), "p8": (12.6, -0.3),
    "p9": (11.7, -4.1), "p10": (7.9, -5.1), "p11": (3.7, -5.7), "p12": (-0.9, -4.5),
    "p13": (-4.2, -2.9), "p14": (10.5, 6.9),
}

EDGES = [
    # core and outer ring
    ("t", "a"), ("t", "b"), ("a", "b"), ("b", "c"),
    ("t", "w"), ("a", "x"), ("c", "y"), ("c", "z"), ("w", "x"), ("y", "z"),
    # periphery
    ("w", "p1"), ("w", "p2"), ("p1", "p2"), ("x", "p3"), ("p2", "p3"), ("x", "p4"),
    ("p3", "p4"), ("p4", "p5"), ("x", "p5"), ("y", "p6"), ("p5", "p6"), ("p6", "p7"),
    ("y", "p7"), ("y", "p8"), ("z", "p8"), ("p7", "p8"), ("z", "p9"), ("p8", "p9"),
    ("z", "p10"), ("p9", "p10"), ("p10", "p11"), ("p11", "p12"), ("p12", "p13"),
    ("p1", "p13"), ("p6", "p14"), ("p7", "p14"),
]

assert all(u in POS and v in POS for u, v in EDGES)
assert all(not ({u, v} & set(CORE)) for u, v in EDGES if u in PERIPHERY or v in PERIPHERY)


def bounds(scale=1.0):
    xs = [scale * x for x, _ in POS.values()]
    ys = [scale * y for _, y in POS.values()]
    return min(xs), max(xs), min(ys), max(ys)
