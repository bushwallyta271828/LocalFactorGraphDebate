# An analytic bracket for the zero-move mean error

**Status: proved real-arithmetic bound; the displayed scalar evaluations use
guarded floating point.** This is the pairwise-table tree model, with zero
unaries and independent N(0, sigma^2) entries. It applies to every finite
tree of maximum degree d whose target has degree d, including every
50,000-vertex tree in this campaign. It is used only at h=0.

For an oriented edge table a (parent rows, child columns), put

```
U = (a10+a11-a00-a01)/2,
C = (a01+a11-a00-a10)/2,
J = (a00+a11-a01-a10)/4.
```

These are independent centered Gaussians with variances sigma^2, sigma^2,
and sigma^2/4. With child cavity logit z, its message is

```
M = U + R,
R = log cosh((C+z)/2+J) - log cosh((C+z)/2-J).
```

The derivative of R with respect to C+z is bounded in absolute value by
tanh(|J|) <= |J|, and R vanishes at C+z=0. Thus
`|R| <= |J| |C+z|`. Symmetry in J centers R. Different child subtrees are
independent. Writing q=d-1 and r=q sigma^2/4, when r<1 an induction bounds
the variance of each non-root outgoing message by

```
V = sigma^2 (1+sigma^2/4)/(1-r).
```

Indeed the leaf variance is at most sigma^2+sigma^4/4, and the induction
step gives `sigma^2+(sigma^2/4)(sigma^2+q V)=V`.
At the target, write L=G+S, where G is the sum of the d root-edge U fields.
Then `G ~ N(0,d sigma^2)` independently of S, and

```
E S^2 <= d (sigma^2/4)(sigma^2+q V)
        = d^2 sigma^4 / (4(1-r)).
```

For G~N(0,s^2), f(x)=E|G+x| is even and convex, with
`f(0)=s sqrt(2/pi)` and `0<=f''(x)<=sqrt(2/pi)/s`. Consequently

```
s sqrt(2/pi) <= E|G+S|
             <= s sqrt(2/pi) + E S^2/(s sqrt(2 pi)).
```

Substituting s=sigma sqrt(d) yields

```
sigma sqrt(2d/pi) <= E|L|
 <= sigma sqrt(2d/pi) [1 + d sigma^2/(8(1-(d-1)sigma^2/4))].
```

The lower bound holds at every sigma; the displayed upper bound requires
(d-1)sigma^2/4<1. With no reveals the judge logit is zero, so E|L| is
exactly the h=0 error being tested. These deterministic inequalities can
therefore supplement the population tests without spending statistical
error probability or changing the target statistic. For example, at d=4,
sigma=1/16 the upper bound is below 0.099932, establishing h=0 as successful.
The code adds a 1e-12 relative/absolute guard to scalar bound evaluations.
