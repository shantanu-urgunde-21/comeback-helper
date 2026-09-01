---
course: "differential equations"
source_file: "MA301 Lecture 16.pdf"
tags: ["math", "coursework", "differential-equations"]
---

# MA301 Lecture 16

<!-- Page 1 -->
Lecture 16

First fundamental theorem of Calculus :

Let $f$ be continuous on $[a,b]$. For $x \in [a,b]$, define
$$F(x) := \int_a^x f(t)\,dt.$$
Then, $F$ is differentiable on $[a,b]$ and $F'(x) = f(x)$ for all $x \in [a,b]$.

Outline of the proof: Our aim is to solve the (Existence part) IVP :
$$y' = f(x,y),\; y(x_0) = y_0 \quad -\textcircled{1}$$

Suppose there exists a solution $y(x)$ for $\textcircled{1}$, then integrating on both sides, we obtain
$$y(x) = y_0 + \int_{x_0}^x f(t,y(t))\,dt \quad -\textcircled{2}$$

Now conversely suppose that $y$ is a continuous function and $y$ satisfies the integral identity given in $\textcircled{2}$. Then we can show that $y$ is a solution for the IVP $\textcircled{1}$. Only step involved here is to find $\frac{d}{dx} \int_{x_0}^x f(t,y(t))\,dt$. If we define

<!-- Page 2 -->
$g(t) = f(t,y(t))$. Then, the function $g$ is continuous since $f$ and $y$ are continuous. Now by the first fundamental theorem of Calculus, we have
$$\boxed{\frac{d}{dx} \int_{x_0}^x f(t,y(t))\,dt = f(x,y(x))}$$

Idea of Picard's Theorem Derivation
Construction of Solution by Picard :

Define an iterative sequence :
$$y_1(x) = y_0 + \int_{x_0}^x f(t,y_0)\,dt$$
$$y_2(x) = y_0 + \int_{x_0}^x f(t,y_1(t))\,dt$$
$$y_3(x) = y_0 + \int_{x_0}^x f(t,y_2(t))\,dt$$
$$\vdots \qquad\qquad \vdots$$
$$y_n(x) = y_0 + \int_{x_0}^x f(t,y_{n-1}(t))\,dt$$

<!-- Page 3 -->
and etc $\dots$. Under the assumptions of the Picard's theorem, the sequence $\{y_n\}$ can be shown to converge to some continuous function $y(x)$ in the interval $I_{\alpha}(x_0)$ and the limiting function must solve the IVP. Proof uses certain results on the uniform convergence of sequence of functions.

Proof of Uniqueness :

Suppose $\phi_1$ & $\phi_2$ be two solutions of the IVP. Let $x_0 = 0$. Then,
$$\phi_1(x) = y_0 + \int_0^x f(t,\phi_1(t))\,dt$$
and $\phi_2(x) = y_0 + \int_0^x f(t,\phi_2(t))\,dt$.

So,
$$\phi_1(x) - \phi_2(x) = \int_0^x [f(t,\phi_1(t)) - f(t,\phi_2(t))]\,dt$$

<!-- Page 1 -->
Let us consider the case $x>0$ and the case $x<0$ can be treated similarly with the necessary modifications. Using the $y$-Lipschitz condition, we can write

$$|\phi_1(x) - \phi_2(x)| \le L \int_0^x |\phi_1(t) - \phi_2(t)| \, dt. \tag{$e_1$}$$

Let us define

$$v(x) = \int_0^x |\phi_1(t) - \phi_2(t)| \, dt.$$

Then, $v'(x) = |\phi_1(x) - \phi_2(x)|$ and hence we can obtain (from ($e_1$))

$$v'(x) - L \, v(x) \le 0.$$

Multiplying the above relation by $e^{-Lx}$ on both sides we get

$$(e^{-Lx} v)' \le 0$$

<!-- Page 2 -->
Since $(e^{-Lx} v)' \le 0$, the function $e^{-Lx} v(x)$ must be decreasing in the interval $(0, \infty)$. By the definition of $v(x)$ clearly $v(0)=0$ and hence

$$e^{-Lx} v(x) \le e^{-L \cdot 0} v(0) = 0$$

Therefore, we obtain

$$v(x) \le 0.$$

Again, from the definition we can see that $v$ has to be a non-negative function. From both the cases we find the function

$$v(x) = \int_0^x |\phi_1(t) - \phi_2(t)| \, dt$$

must be identically zero. It is possible only if $\phi_1(t) = \phi_2(t)$ for all $t$. Hence the uniqueness.

<!-- Page 3 -->
Examples of Picard's iteration:

Solve $y' = xy$, $y(0) = 1$ using Picard's iteration method.

Solution: The equivalent integral equation is

$$y(x) = y(x_0) + \int_{x_0}^x f(t, y(t)) \, dt \implies y(x) = 1 + \int_0^x t y \, dt,$$
where $f(x, y) = xy$, $y(0) = 1$.

Picard's successive approximations are:

$$y_n(x) = y_0 + \int_{x_0}^x f(t, y_{n-1}(t)) \, dt, \quad n=1, 2, 3, \dots$$

$$y_1(x) = 1 + \int_0^x t \cdot 1 \, dt = 1 + \frac{x^2}{2}.$$

$$y_2(x) = 1 + \int_0^x t \left(1 + \frac{t^2}{2}\right) dt = 1 + \frac{x^2}{2} + \frac{x^4}{2 \cdot 4}.$$

$$y_n(x) = 1 + \frac{x^2}{2} + \frac{1}{2!} \left(\frac{x^2}{2}\right)^2 + \dots + \frac{1}{n!} \left(\frac{x^2}{2}\right)^n.$$

$$y(x) = \lim_{n \to \infty} y_n(x) = e^{x^2/2} \quad \text{(By induction)}$$

