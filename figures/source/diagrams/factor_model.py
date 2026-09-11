"""Exact log-odds L_S on induced subgraphs via variable elimination (numpy)."""
import itertools, math, random
import numpy as np
from graph_data import VERTS, EDGES


def draw_tables(seed, sigma=1.0, field=1.0):
    rng = random.Random(seed)
    theta = {e: {(s, u): rng.gauss(0, sigma) for s in (-1, 1) for u in (-1, 1)} for e in EDGES}
    phi = {v: rng.gauss(0, field) / 2 for v in VERTS}   # phi(x)=l x/2, l~N(0,field^2)
    return theta, phi


def make_L(theta, phi):
    """Return L(S): the judge's log-odds that t = +1 given transcript S."""
    # pairwise tables as 2x2 arrays indexed by (x_u, x_v) with index 0 -> -1, 1 -> +1
    pair = {}
    for e, tab in theta.items():
        pair[e] = np.array([[tab[(-1, -1)], tab[(-1, 1)]], [tab[(1, -1)], tab[(1, 1)]]])
    un = {v: np.array([-phi[v], phi[v]]) for v in VERTS}
    cache = {}

    def L(S):
        S = tuple(sorted(S))
        if S in cache:
            return cache[S]
        Sset = set(S)
        # factors: list of (vars tuple, log-table array)
        facs = [((v,), un[v]) for v in S]
        facs += [(e, pair[e]) for e in EDGES if e[0] in Sset and e[1] in Sset]
        # eliminate everything except t, min-degree order
        adj = {v: set() for v in S}
        for vs, _ in facs:
            for u in vs:
                adj[u] |= set(vs) - {u}
        remaining = set(S) - {"t"}
        while remaining:
            v = min(remaining, key=lambda u: len(adj[u] & (remaining | {"t"})))
            remaining.discard(v)
            touch = [f for f in facs if v in f[0]]
            facs = [f for f in facs if v not in f[0]]
            # multiply (add logs) the touching factors over their union of vars
            allv = []
            for vs, _ in touch:
                for u in vs:
                    if u not in allv:
                        allv.append(u)
            acc = np.zeros((2,) * len(allv))
            for vs, tab in touch:
                idx = [allv.index(u) for u in vs]
                # broadcast tab into acc's axes
                shape = [1] * len(allv)
                for k, i in enumerate(idx):
                    shape[i] = 2
                perm = np.argsort(idx)
                t = np.transpose(tab, perm) if len(vs) > 1 else tab
                acc = acc + t.reshape(shape)
            ax = allv.index(v)
            m = acc.max(axis=ax, keepdims=True)
            new = (np.log(np.exp(acc - m).sum(axis=ax)) + m.squeeze(axis=ax))
            newv = tuple(u for u in allv if u != v)
            for u in newv:
                adj[u] |= set(newv) - {u}
            facs.append((newv, new))
        tot = np.zeros(2)
        for vs, tab in facs:
            tot = tot + tab
        val = float(tot[1] - tot[0])
        cache[S] = val
        return val
    return L


def brute_L(theta, phi, S):
    S = tuple(sorted(S))
    es = [e for e in EDGES if e[0] in S and e[1] in S]
    Z = {1: 0.0, -1: 0.0}
    for spins in itertools.product((-1, 1), repeat=len(S)):
        x = dict(zip(S, spins))
        en = sum(theta[e][(x[e[0]], x[e[1]])] for e in es) + sum(phi[v] * x[v] for v in S)
        Z[x["t"]] += math.exp(en)
    return math.log(Z[1]) - math.log(Z[-1])


if __name__ == "__main__":
    import time
    theta, phi = draw_tables(248, 1.3, 1.0)
    L = make_L(theta, phi)
    for S in [("t",), ("t", "a", "b", "c"), ("t", "a", "b", "c", "w", "x", "y", "z", "p1", "p8")]:
        print(S, L(S), brute_L(theta, phi, S))
    t0 = time.time()
    rest = [v for v in VERTS if v not in ("t", "a", "b", "c")]
    n = 0
    for r in range(len(rest) + 1):
        for extra in itertools.combinations(rest, r):
            L(("t", "a", "b", "c") + extra); n += 1
            if n == 2000: break
        if n == 2000: break
    print("per S: %.2f ms" % ((time.time() - t0) / n * 1000))
