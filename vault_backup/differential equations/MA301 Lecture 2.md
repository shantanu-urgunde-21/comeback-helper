---
course: "differential equations"
source_file: "MA301 Lecture 2.pdf"
tags: ["math", "coursework", "differential-equations"]
---

# MA301 Lecture 2

<!-- Page 1 -->
Lecture 2
Homogeneous Linear Equation

Consider the initial value problem $y' + p(x)y = 0; y(x_0) = 1$.
By Picard's theorem the above IVP must admit a unique solution $u(x)$, when $p(x)$ is a bounded continuous function in an interval $I$ containing $x_0$.

**Theorem:** Let $u$ be the unique solution of the homogeneous linear differential equation $y' + p(x)y = 0$ with initial condition $y(x_0) = 1$. If $y_h$ is a solution of $y' + p(x)y = 0$, then $y_h(x) = C u(x)$ for some real constant $C$.

**Proof:** Consider the function $z(x) = \frac{y_h(x)}{u(x)}$.
(Why $u(x) \neq 0$ ?)

**Claim:** $z'(x) = 0$.
Now, $z'(x) = \frac{u'(x) y_h(x) - u(x) y_h'(x)}{(u(x))^2}$.

Note that, $u(x)$ satisfies $y' + p(x)y = 0, y(x_0) = 1$ and
$y_h(x)$ satisfies $y' + p(x)y = 0 \implies$
$\begin{aligned}
y_h'(x) &= -p(x)y \\
u'(x) &= -p(x)u
\end{aligned}$ - $(* *)$

---

<!-- Page 2 -->
Using $(* *)$ in $(*)$, we obtain

$z'(x) = 0 \implies z(x) = C$ (an arbitrary constant)
$$\frac{y_h(x)}{u(x)} = C$$

or $\boxed{y_h(x) = C u(x)}$, for some constant $C$.

---

<!-- Page 3 -->
Second Order Ordinary Differential Equation
We proved the theorem:

**Theorem:** Let $u$ be the unique solution of the homogeneous linear differential equation $y' + p(x)y = 0$ with initial condition $y(x_0) = 1$. If $y_h$ is any solution of the homogeneous DE $y' + p(x)y = 0$, then necessarily $y_h(x) = C u(x)$, for some real constant $C$.

**Question:** What could be the equivalent result for a second order linear differential equation?

**Main results to be proved:** Any solution $y_h$ must be equal to $C_1 y_1 + C_2 y_2$ for some real constants $C_1, C_2$ and $y_1, y_2$ are two linearly independent solutions of an associated initial value problem.

**Second Order linear ODE:**
The second order linear ODE's are among the most important from the point of view of physics and engineering applications. They model the physical world's phenomena in ideal situations.

<!-- Page 1 -->
Recall that a general second order linear ODE
$$\frac{d^2y}{dx^2} + p(x)\frac{dy}{dx} + q(x)y = r(x)$$
is in its standard/normal/monic form.

We study the existence, uniqueness and/or number of solutions of such ODE's and their mathematical behaviour like estimating number of zeros etc. (Qualitative Analysis).

Examples: Some of the important second order linear ODE's are
$$y'' + u^2y = 0 \quad \text{(Fourier Equation)}$$
$$(1-x^2)y'' - 2x y' + n(n+1)y = 0 \quad \text{(Legendre Equation)}$$
$$x^2 y'' + xy' + (x^2 - v^2)y = 0 \quad \text{(Bessel Equation)}$$

(*) In the above equations, $u$, $n$, $v$, respectively are parameters.

(**) The domain intervals are $\mathbb{R}$, $(-1,1)$, $(0,\infty)$ respectively.

Applications: Quantum Mechanics, Signal Processing, Neural Networks, fluid dynamics, etc.

<!-- Page 2 -->
Main theorem for IVP for $2^{\text{nd}}$ order homogeneous ODE:

Definition: (IVP for $2^{\text{nd}}$ order linear homogeneous ODE)

Let $p(x), q(x)$ be continuous on an open or closed interval $I$ with $x_0 \in I$. An initial value problem of a second order homogeneous linear ODE is of the form
$$(\ast) \longrightarrow y'' + p(x)y' + q(x)y = 0 \; ; \; y(x_0)=a, y'(x_0)=b.$$

The following result represents the existence and uniqueness result for second order linear ODE's with prescribed initial values:

Theorem (Existence and uniqueness):
$$(\ast) \begin{cases} \text{An IVP of a second order linear homogeneous} \\ \text{ODE } (\ast) \text{ in an interval } I \text{ has a unique solution in} \\ \text{the said interval.} \end{cases}$$

The existence/uniqueness theorem can be proved by a version of Picard's iteration for vector valued functions (Already discussed in case of first order ODEs)

