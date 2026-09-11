"""Outward certificates for the widened response-path lower theorem.

Run in the repository virtual environment (python-flint, scipy):
    python figures/source/numerics/endpoint_certificates.py            # both endpoints
    python figures/source/numerics/endpoint_certificates.py --q 4       # one degree

For d = q+1 in {5,6} the script builds, at the listed noise endpoint
sigma_0, a positive Gaussian mixture  Phi~(x) = sum_k c_k exp(-x^2/(2 w_k))
with w_k >= tau, checks  Phi~ <= Phi_tau  on the whole line, and evaluates
the certified per-level factor  Lambda = sum_k c_k SF_{q-1}(b_q, w_k).
The theorem needs q*Lambda > 1.  Here

  Q_tau(u)  = E_Z[ psi(Z,u) exp(-r(Z,u)^2/(2 tau)) ],  Z standard normal,
  psi(z,u)  = (cosh(sigma z)+1)/(cosh(sigma u)+cosh(sigma z)),
  r(z,u)    = 2 artanh(tanh(sigma z/2) tanh(sigma u/2))/sigma,
  Phi_tau(x)= E Q_tau(G+x),  G ~ N(0, s),  s = q+1,
  SF_n(b,w) = E_G m_b(G/sqrt w)^n,  m_b(t) = cos(t sqrt b) if t sqrt b <= pi, else -1
              (for even n the negative part of m_b is replaced by 0).

Rigour.  Every quantity that must be bounded below is bounded below by a
monotone Riemann sum evaluated in Arb ball arithmetic: Q is decreasing in
|u| and psi is increasing / |r| increasing in |z|; Phi is decreasing in |x|;
the integrand of SF is decreasing on the integration range.  Positive tails
are discarded.  The linear program that proposes the mixture runs in floating
point; the verification of the mixture does not.  Beyond x = X the inequality
Phi~ <= Phi follows from the explicit exponential lower tail
Phi(x) >= (kappa/2) exp(-sigma x + sigma^2 s/2) for x >= 1 + sigma s, checked
once at X (the ratio is monotone past sigma*w_max).
"""
import argparse, json, math
from pathlib import Path
import numpy as np
from flint import arb, ctx
from scipy import optimize

# retained endpoint certificate parameters: (sigma_0, b_q, tau)
CASES = {4: ('4.0', '.738', '5'), 5: ('8.0', '.764', '6')}

def arb_gauss_mass(a, b, mean, sd):
    """P(a <= N(mean,sd^2) <= b) as an arb, a<=b; erfc-based to avoid cancellation in the tails."""
    r2 = arb(2).sqrt()
    ta, tb = (a-mean)/(sd*r2), (b-mean)/(sd*r2)
    if ta >= 0:
        return (ta.erfc() - tb.erfc())/2
    if tb <= 0:
        return ((-tb).erfc() - (-ta).erfc())/2
    return (tb.erf() - ta.erf())/2

def psi_arb(sigma, z, u):
    cz = (sigma*z).cosh(); cu = (sigma*u).cosh()
    return (cz+1)/(cu+cz)

def resp_arb(sigma, z, u):
    return 2*((sigma*z/2).tanh()*(sigma*u/2).tanh()).atanh()/sigma

def Q_lower(q, sigma, tau, us, zcells, eps=None):
    """Rigorous lower bounds for Q_tau(u) at each u in us (u>=0). zcells: increasing arb nodes from 0."""
    masses = [arb_gauss_mass(zcells[i], zcells[i+1], arb(0), arb(1)) for i in range(len(zcells)-1)]
    out = []
    for u in us:
        tot = arb(0)
        for i in range(len(zcells)-1):
            zlo, zhi = zcells[i], zcells[i+1]
            p = psi_arb(sigma, zlo, u)                  # psi increasing in z
            car = (-(resp_arb(sigma, zhi, u))**2/(2*tau)).exp()   # |r| increasing in z
            if eps is not None:
                c = (sigma*zlo/2).tanh()
                p = p*arb.min(arb(1), c/eps)
            tot += masses[i]*p*car
        out.append(2*tot)
    return out

def Phi_lower(Q_lb, us, xs, s):
    """Rigorous lower bounds for Phi(x)=E Q(G+x), G~N(0,s), x in xs, using Q decreasing in |u|."""
    sd = arb(s).sqrt()
    out = []
    for x in xs:
        tot = arb(0)
        for j in range(len(us)-1):
            ulo, uhi = us[j], us[j+1]
            m = arb_gauss_mass(ulo, uhi, x, sd) + arb_gauss_mass(-uhi, -ulo, x, sd)
            tot += Q_lb[j+1]*m
        out.append(tot)
    return out

def SF_lower(n, b, w, ncells=4000):
    """Rigorous lower bound for E_G m_b(G/sqrt w)^n."""
    a = (b/w).sqrt()
    lim = arb.pi()/a if n % 2 == 1 else arb.pi()/(2*a)
    L = arb.min(lim, arb(12))
    tot = arb(0)
    for i in range(ncells):
        g0 = L*i/ncells; g1 = L*(i+1)/ncells
        val = (a*g1).cos()**n                           # decreasing on [0,L]
        tot += arb_gauss_mass(g0, g1, arb(0), arb(1))*val
    tot = 2*tot
    if n % 2 == 1:
        tot -= 1 - 2*arb_gauss_mass(arb(0), L, arb(0), arb(1))   # m_b^n >= -1 on |G| > L
    return tot

def find_and_verify(q, sigma_text, b_text, tau_text, zc=3000, verbose=True):
    ctx.prec = 256
    sigma, b, tau, s = arb(sigma_text), arb(b_text), arb(float(tau_text)), arb(q+1)
    assert tau >= s
    D = 2/arb.pi()*(s.sqrt() + (1-s)*(1/s.sqrt()).atan())
    H = 1 - D*(-q*b/(2*s)).exp()
    assert H < b and b > arb('0.5'), ('variance supersolution failed', q)

    sig_f = float(sigma_text); s_f = q+1; tau_f = float(tau_text)
    # grids
    w_cap = max(4*s_f, 2*s_f/sig_f**2); w_cap = min(w_cap, 200.0)
    X = max(14.0, 1 + sig_f*s_f, sig_f*w_cap) + 1.0
    us_f = np.concatenate([np.arange(0, 10, 0.004), np.arange(10, X+0.5, 0.05)])
    xs_f = np.concatenate([np.arange(0, 8, 0.01), np.geomspace(8, X, 200)])
    zcells = [arb(8)*i/zc for i in range(zc+1)]
    us = [arb(float(u)) for u in us_f]; xs = [arb(float(x)) for x in xs_f]
    if verbose: print(f'd={q+1}: computing Q on {len(us)} points x {zc} cells ...', flush=True)
    Q_lb = Q_lower(q, sigma, tau, us, zcells)
    if verbose: print(f'd={q+1}: computing Phi on {len(xs)} points ...', flush=True)
    Phi_lb = Phi_lower(Q_lb, us, xs, s)
    Phi_f = np.array([float(p.lower()) for p in Phi_lb])
    # exponential tail constants: Q(u) >= kappa exp(-sigma u) for u >= 1
    kappa = (1/(1+1/tau)).sqrt() - (-1/(2*tau)).exp()*(1 - 2*arb_gauss_mass(arb(0), arb(1), arb(0), arb(1)))
    assert kappa > 0
    tail_at_X = kappa/2*(-sigma*arb(X) + sigma**2*s/2).exp()
    # LP in floats with conservative cell constraints Phi~(x_i) <= Phi_lb(x_{i+1}), plus tail row at X
    ws_f = np.exp(np.linspace(math.log(tau_f), math.log(w_cap), 80)); ws_f[0] = tau_f
    coef = np.array([float(SF_lower(q-1, b, arb(float(w)), 1500).lower()) for w in ws_f])
    A = np.exp(-xs_f[:-1, None]**2/(2*ws_f[None, :])); rhs = Phi_f[1:]
    A = np.vstack([A, np.exp(-X**2/(2*ws_f))[None, :]]); rhs = np.append(rhs, float(tail_at_X.lower()))
    res = optimize.linprog(-coef, A_ub=A, b_ub=rhs, bounds=[(0, None)]*len(ws_f), method='highs')
    keep = res.x > 1e-6
    # round the mixture down to the printed precision (4 decimals in c, 3 in w); both directions are conservative
    mixture = []
    for c, w in zip(res.x[keep], ws_f[keep]):
        c_txt = f'{math.floor(c*1e4)/1e4:.4f}'
        w_txt = tau_text if abs(w-tau_f) < 1e-9 else f'{math.floor(w*1e3)/1e3:.3f}'
        mixture.append((c_txt, w_txt))
    # rigorous verification of the printed mixture
    cs = [arb(c) for c, _ in mixture]; wsa = [arb(float(w)) for _, w in mixture]
    def Phit(x): return sum(c*(-x*x/(2*w)).exp() for c, w in zip(cs, wsa))
    for i in range(len(xs)-1):
        assert Phit(xs[i]) <= Phi_lb[i+1], ('minorant failed at', float(xs[i]))
    assert Phit(arb(X)) <= tail_at_X, 'tail check failed'
    assert all(w >= tau for w in wsa) and arb(X) >= sigma*max(wsa) and arb(X) >= 1+sigma*s
    Lam = sum(c*SF_lower(q-1, b, w) for c, w in zip(cs, wsa))
    growth = q*Lam
    assert growth > 1, ('path growth failed', q, growth)
    if verbose:
        print(f'd={q+1}, 0<sigma<={sigma_text}, b={b_text}, tau={tau_text}:')
        print('  H_q(b) =', H.str(10))
        print('  mixture components =', len(mixture), ' (c,w):', mixture)
        print('  q*Lambda lower =', growth.lower().str(12))
    return mixture, growth

def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--q', type=int, choices=sorted(CASES))
    p.add_argument('--zcells', type=int, default=3000)
    a = p.parse_args()
    out = {}
    for q in ([a.q] if a.q else CASES):
        mix, g = find_and_verify(q, *CASES[q], zc=a.zcells)
        out[q] = {'sigma': CASES[q][0], 'b': CASES[q][1], 'tau': CASES[q][2], 'mixture': mix, 'q_lambda_lower': g.lower().str(12)}
    output = Path(__file__).resolve().parents[2] / '.build' / 'endpoint-certificates.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(out, indent=1) + '\n')
    print('All requested outward certificates passed.')

if __name__ == '__main__':
    main()
