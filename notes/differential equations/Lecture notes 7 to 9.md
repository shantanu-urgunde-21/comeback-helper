---
course: "differential equations"
source_file: "Lecture notes 7 to 9.pdf"
tags: ["math", "coursework", "differential-equations"]
---

# Lecture notes 7 to 9

<!-- Page 1 -->
25/03/2025 Lecture - 7

Now, we will start with definitions which will be used in the subsequent explanation.

Definition: (from calculus) Let \( f(x) \) be a function of two real variables such that \( f \) has continuous first order partial derivatives in a domain \( D \). The total differential \( dF \) of \( F \) is defined by the formula

$$ dF(x, y) = F_x(x, y) \, dx + F_y(x, y) \, dy $$

for all \( (x, y) \in D \), where \( F_x = \frac{\partial F}{\partial x} \) and \( F_y = \frac{\partial F}{\partial y} \).

Definition: The differential equation

$$ M(x, y) \, dx + N(x, y) \, dy = 0 $$

is called an exact differential equation if there exists a function \( F(x, y) \in D \subset \mathbb{R}^2 \) such that

$$ F_x(x, y) = M(x, y) \quad \text{and} \quad F_y(x, y) = N(x, y) $$

for all \( (x, y) \in D \).

Note that here \( D \) denotes a bounded domain in \( \mathbb{R}^2 \).

<!-- Page 2 -->
So, now if an ODE

$M(x, y) + N(x, y) \frac{dy}{dx} = 0$

is exact then there exists a function $F(x, y)$ such that $F_x(x, y) = M(x, y)$ and $F_y(x, y) = N(x, y)$

$\Rightarrow$

$M(x, y) dx + N(x, y) dy = \frac{\partial F}{\partial x} dx + \frac{\partial F}{\partial y} dy = 0$

$\Rightarrow$

$dF = 0$

or $\boxed{F(x, y) = C}$

is implicit / formal solution to the given ODE.

Example: $2x + y^2 + 2xy \frac{dy}{dx} = 0$ is exact?

Yes, the given ODE is exact. Consider the function $F(x, y) = x^2 + xy^2$. Note that,

$F_x = 2x + y^2$, $F_y = 2xy$

$F_x = M$, $F_y = N$

Therefore, $x^2 + xy^2 = C$ is the solution to the given ODE.

<!-- Page 3 -->
$\text { Theorem } \circ: \text { Let } D \text { denotes a bounded domain in } \mathbb{R}^{2} \text {. Assume that } M(x, y) \text { and } N(x, y) \in C^{1}(D) \text {. Then the following two statements are equivalent: }$

(1) $M(x, y) + N(x, y) y' = 0$ is exact.

(2) $M_{x}(x, y) = N_{x}(x, y)$ for all $(x, y) \in D$.

Proof: (1) $\Rightarrow$ (2) Since $M_{x} + N_{y} = 0$ is exact. Then there exists a function $F$ such that $F_{x} = M$ and $F_{y} = N$.

Proof: (1) $\Rightarrow$ (2) Since $M$ and $N$ are given to be $C^{1}$ functions, $M_{x} = F_{x, y}$ and $N_{x} = F_{y, x}$.

Proof: (2) $\Rightarrow$ (1) Since $M_{x} = F_{x, y}$ and $N_{x} = F_{y, x}$, $F_{x, y} = F_{y, x}$.

Note: That here we have used a result from the missing order partial derivatives.

Proof: (2) $\Rightarrow$ (1) Since $F_{x, y} = F_{y, x}$, $F_{x, y} = \frac{\partial^{2} F}{\partial x \partial y}$ and $F_{y, x} = \frac{\partial^{2} F}{\partial y \partial x}$.

<!-- Page 4 -->
The concave part is more technical. ④

Proposition: (3.14) (Miccra partials theorem):
Let D ⊆ R² be an open set and let (x₀, y₀) be any point of D. Let f: D → R be such that both fₓ and fᵧ exist on D. If fₓ and fᵧ or fₓ and fᵧ exist on D and are continuous at (x₀, y₀), then both fₓ(x₀, y₀) and fᵧ(x₀, y₀) exist and are continuous at (x₀, y₀).

Example: Solve the DE
4x + 3y + 3(x + y²)y' = 0.

Note that M, N ∈ C'(R) and M_y = N_x = 3.

Therefore, the equation is exact.

There exists a function F(x, y) such that
Fₓ = 4x + 3y, Fᵧ = 3(x + y²).

Now, from ① and ②, we have
3x + 3y² = f₃(x, y) = 3x + φ(y)

Thus, the solution is
φ(y) = y² - 3y + C

<!-- Page 5 -->
$\Rightarrow \quad \phi^{\prime}(y)=3 y^{2} \quad \Rightarrow \quad \phi(y)=y^{3} .$

Thus, from (2), $F(x, y)=2 x^{2}+3 x y+y^{3}$.

The general solution is given by

$2 x^{2}+3 x y+y^{3}=c .$

Example: Solve the D.E

$(y \cos x+2 x e^{y})+(y \sin x+x^{2} e^{y}-1) y^{\prime}=0 .$

Solution: Here $M=y \cos x+2 x e^{y}$

$N=\sin x+x^{2} e^{y}-1$

Is this equation exact?

Check whether $M_{x}=N_{y}$

The answer is Yes.

By the previous result, there exists a function $F(x, y)$ such that

$f_{x}=M \quad \text { and } \quad f_{y}=N .$

Now,

$F_{x}=y \cos x+2 x e^{y} \quad \text { (1) }$

$F_{y}=\sin x+x^{2} e^{y}-1 \quad \text { (2) }$

After integrating (1), we obtain

$F(x, y)=\int(y \cos x+2 x e^{y}) \, dx + \phi(y)$

$=y \sin x+x^{2} e^{y} + \phi(y)$

<!-- Page 6 -->
Here is the transcribed content from the handwritten note page:

```markdown
Therefore,

$F_{y} = \sin(x) + x^2 e^y + \phi(y) - (*)$

From (*) and (***), we obtain

$\sin(x) + x^2 e^y + \phi'(y) = \sin(x) + x^2 e^y - 1$

$\Rightarrow \phi'(y) = -1$

$\Rightarrow \phi(y) = -y$

Therefore, we have

$F(x, y) = y \sin(x) + x^2 e^y - y = c$

$F(x, y) = y \sin(x) + x^2 e^y - y = c$

Definition: If the equation

$M(x, y) dx + N(x, y) dy = 0$

is not exact but the equation

$u(x, y) \left\{ M(x, y) dx + N(x, y) dy \right\} = 0$

is exact, then $u(x, y)$ is called an integrating factor.

Theorem: If $\frac{M_y - N_x}{N}$ is continuous, then $u(x, y)$ is an integrating factor for $M dx + N dy = 0$.
```

<!-- Page 7 -->
```markdown
Solution: If $u(x, y)$ is an integrating factor, then we must have

$$
\left\{\begin{array}{l}
\frac{\partial}{\partial y}(uM) = \frac{\partial}{\partial x}(uN) \\
\frac{\partial u}{\partial y} - \frac{\partial u}{\partial x} = 0
\end{array}\right.
$$

or

If $u = u(x)$, then

$$
\frac{du}{dx} = e^{\int \left(\frac{M_y - N_x}{N}\right) dx}
$$

Now, L.H.S. of (a) is as follows:

$$
\frac{\partial}{\partial y}(uM) - \frac{\partial}{\partial x}(uN) = u_yM + u_M_y - u_xN - u_N_x
$$

$$
= u_M_y - \left(\frac{M_y - N_x}{N}\right)u_N - u_N_x
$$

Using (a)

$$
u_M_y - u_M_y + u_N_x - u_N_x = 0
$$

Hence, proved!
```

<!-- Page 8 -->
```markdown
# Example
Solve $(2x^2 + y)dx + (x^2y - x)dy = 0$

The equation is not exact as $M_2 = 1 \neq 2xy - 1 = N_2x$

Note that $\frac{M_2 - N_2x}{N} = \frac{1 - 2xy + 1}{-x(1 - xy)} = \frac{2(1 - xy)}{-x(1 - xy)} = -2$

which is a function of only $x$.

Therefore, from equation $(**)$, we have $u(x) = \int \frac{2}{x}dx = x^{-2}$

as an integrating factor.

Now, multiply $(\textbf{1})$ by $u(x)$. Then the resulting equation is an exact equation.

One can solve it using the method for exact ODE and obtain the following general solution:

$2x + \frac{y^2}{2} - 2xy^{-1} = C$

Theorem: If $\frac{N_2 - M_2}{M_2}$ is continuous and depends only on $y$, then

$u(y) = \exp\left(\int \frac{N_2 - M_2}{M_2}dy\right) - C$

is an integrating factor for $M_2x + N_2y = 0$.
```

<!-- Page 9 -->
```markdown
# Example
$x y \, dx + (2 x^{2} + 3 y^{2} - 20) \, dy = 0$

Verify that this is not an exact differential equation (ODE).

Here $M(x, y) = x^{2}$ and $N(x, y) = 2 x^{2} + 3 y^{2} - 20$

Then, $\frac{M_{y} - N_{x}}{N} = \frac{-3 x}{2 x^{2} + 3 y^{2} - 20}$ depends on $x$ and $y$ and gets nowhere.

Note that $\frac{N_{x} - M_{y}}{M} = \frac{3}{2 y}$, a function of $y$ alone.

By the result of the equation (C), an integrating factor is $u(y) = y^{3}$

Then, multiplying by the integrating factor, we obtain

$x y^{4} \, dx + (2 x^{2} y^{3} + 3 y^{4} - 20 y^{3}) \, dy = 0$

This is an exact ODE.

Show that the solution is

$\frac{1}{2} x^{2} y^{4} + \frac{1}{2} y^{6} - 5 y^{4} = c$

Example: Solve the ODE

$(8 x y - 9 y^{2}) + (2 x^{2} - 6 x y) \frac{dy}{dx} = 0$

Here $M = 8 x y - 9 y^{2}$ and $N = 2 x^{2} - 6 x y$.
```

<!-- Page 10 -->
$\begin{aligned}& \text { Thus, } \\& M_{3}=8 x-18 y \quad \text { and } \quad N_{x}=4 x-6 y . \\& \text { As } M_{3} \neq N_{x}, \text { the given ODE is not exact. } \\& \text { Note that } \\& \frac{M_{3}-N_{x}}{N}=\frac{4 x-12 y}{2 x(x-3 y)}=\frac{2}{x}, \text { is a } \\& \text { function of } x \text { alone. } \\& \text { So from equation (*) , an integrating } \\& \text { factor is } \\& \left|y(x)=x^{2}\right| . \\& \text { Multiplying the given ODE by } y(x)=x^{2}, \\& \text { we get } \\& \left(8 x^{3} y-g x^{2} y^{2}\right)+\left(2 x^{4}-6 x^{3} y\right) y^{\prime}=0 . \\& \text { Verify that this is an exact ODE. } \\& \text { Now, there exists a function } F(x, y) \\& \text { such that } \\& F_{x}=8 x^{3} y-g x^{2} y^{2} \text { and } F_{y}=2 x^{4}-6 x^{3} y \\& F(x, y)=2 x^{4} y-3 x^{3} y^{2}+\phi^{\prime}(y) \\& F_{x}(x, y)=2 x^{4}-6 x^{3} y+\phi^{\prime}(y)=2 x^{4}-6 x^{3} y \\& \text { Thus } \phi^{\prime}(y)=0 . \text { Therefore, } \\& F(x, y)=2 x^{4} y-3 x^{3} y^{2}+c \text { is a general } \\& \text { solution of the given ODE. }\end{aligned}$

<!-- Page 11 -->
$\text { Problem : Consider the equation } y^{\prime}=y, y(0)=1. \text { Show that } y=e^{x} \text { is the only solution of the above differential equation. }$

$\text { Existence of solution : Substitute } y=e^{x} \text { in the equation } y^{\prime}=y \text { and show that it satisfies the differential equation and the initial condition. }$

$\text { Uniqueness : Let } y_{1}=e^{x} \text { and } y_{2} \text { be any other solution of the ODE } y^{\prime}=y, y(0)=1. \text { In general, to prove uniqueness, we either prove } y_{2}-y_{1}=0 \text { or } \frac{y_{2}}{y_{1}}=1. \text { Here, since } y_{1}(x) \neq 0, \text { we will show that } \frac{y_{2}}{y_{1}}=1. \text { Now, } \left(\frac{y_{2}}{y_{1}}\right)^{\prime}=\frac{y_{1} y_{2}^{\prime}-y_{1} y_{2}}{y_{1}^{2}}=\frac{e^{x} y_{2}^{\prime}-e^{x} y_{2}}{e^{2 x}}$

$=e^{x}\left(y_{2}^{\prime}-y_{2}\right)=0, \text { since } y_{2}^{\prime}(x) \text { satisfies the differential equation and } e^{-x} \neq 0. \text { This implies } \frac{y_{2}}{y_{1}}=k. \text { Now } y_{1}(0)=1=y_{2}(0) \text { implies } \frac{y_{2}}{y_{1}}=k. \text { Now } y_{1}(x)=y_{2}(x) \neq x. \text { Therefore, } y_{2}(x)=y_{1}(x) \neq x. \text { Therefore, } y_{2}(x)=y_{1}(x) \neq x. \text { Therefore, } y_{2}(x)=y_{1}(x) \neq x. \text { Therefore, } y_{2}(x)=y_{1}(x) \neq x. \text { Therefore, } y_{2}(x)=y_{1}(x) \neq x. \text { Therefore, } y_{2}(x)=y_{1}(x) \neq x. \text { Therefore, } y_{2}(x)=y_{1}(x) \neq x. \text { Therefore, } y_{2}(x)=y_{1}(x) \neq x. \text { Therefore, } y_{2}(x)=y_{1}(x) \neq x. \text { Therefore, } y_{2}(x)=y_{1}(x) \neq x. \text { Therefore, } y_{2}(x)=y_{1}(x) \neq x. \text { Therefore, } y_{2}(x)=y_{1}(x) \neq x. \text { Therefore, } y_{2}(x)=y_{1}(x) \neq x. \text { Therefore, } y_{2}(x)=y_{1}(x) \neq x. \text { Therefore, } y_{2}(x)=y_{1}(x) \neq x. \text { Therefore, } y_{2}(x)=y_{1}(x) \neq x. \text { Therefore, } y_{2}(x)=y_{1}(x) \neq x. \text { Therefore, } y_{2}(x)=y_{1}(x) \neq x. \text { Therefore, } y_{2}(x)=y_{1}(x) \neq x. \text { Therefore, } y_{2}(x)=y_{1}(x) \neq x. \text { Therefore, } y_{2}(x)=y_{1}(x) \neq x. \text { Therefore, } y_{2}(x)=y_{1}(x) \neq x. \text { Therefore, } y_{2}(x)=y_{1}(x) \neq x. \text { Therefore, } y_{2}(x)=y_{1}(x) \neq x. \text { Therefore, } y_{2}(x)=y_{1}(

<!-- Page 12 -->
```markdown
# Exercise 1
Solve $(4x + 2y + 5)y' + (2x + y - 1) = 0$

# Hint
Substitute $v = 2x + y$ to get the separable form.

# Exercise 2
Solve $y' = \frac{x + y - 3}{x - y - 1}$

# Hint
Substitute $x = z + h$, $y = z + k$ for some $h, k$ which will be determined.

# Exercise 3
Solve $y' = \frac{z + h + h + k - 3}{z - h + h - k - 1}$

# Hint
Choose $h, k$ such that $h + k - 3 = 0$ and $h - k - 1 = 0$.

# Problem
Suppose $M$ and $N$ are continuous and have continuous partial derivatives on an open rectangle $R = \{(x, y) \mid |x - x_0| < \epsilon, |y - y_0| < \delta\}$ around $(x_0, y_0)$. Show that if $(x, y) \in R$ and
\[ F(x, y) = \int_{x_0}^{x} M(s, y_0) \, ds + \int_{y_0}^{y} N(x_0, t) \, dt \]
then $F(x, y) = M$ and $F(y, y) = N$.

# Conclusion
This choice makes the equation homogeneous.
```

<!-- Page 13 -->
```markdown
Solution: Note that, from (*) we have

from the first fundamental theorem of integral calculus

Define $F(x, y) = \int_{x_0}^{x} M(s, y) ds + \int_{y_0}^{y} N(x, t) dt + t$

We need to show that $F$ defined in (*) and (*) are the same.

From (*) we have

$F(x, y) - \left[ \int_{y_0}^{y} N(x, t) dt + \int_{x_0}^{x} M(s, y) ds \right]$

$= \int_{x_0}^{x} \left[ M(s, y) - M(s, 0) \right] ds - \int_{y_0}^{y} \left[ N(x, t) - N(x, 0) \right] dt$

$= \int_{x_0}^{x} \int_{y_0}^{y} \left[ \frac{\partial M}{\partial t}(s, t) - \frac{\partial N}{\partial s}(s, t) \right] ds dt$

Therefore, the two definitions in (*) and (*) for $F(x, y)$ are the same.
```

<!-- Page 14 -->
Consider the following initial value problem:

$\left\{\begin{array}{l} y'(x) = f(x, y) \\ y(x_0) = y_0 \end{array}\right.$

Example 1: The differential equation $y' = y$, $y(0) = 1$ is known to admit a unique solution.

Example 2: The differential equation $y' = \sqrt{x}$, $y(0) = 0$ admits at least two solutions. A solution $y_1(x) = \frac{x^2}{4}$ can be obtained by variable separation method. Another solution $y_2(x) = 0$ is also a solution.

Example 3: The differential equation $|y'| + |y| = 0$, $y(0) = 3$ admits no solution. The differential equation $y'(x) = \sqrt{x}$, $y(0) = 0$ admits the unique solution $y(x) = \frac{2}{3}x^{3/2}$.

Question: What can we observe about the existence/uniqueness of the IVP $y'(x) = f(x, y)$, $y(x_0) = y_0$?

<!-- Page 15 -->
Hadamard's criterion for well-posed IVP
An IVP is said to be well posed if
(i) it has a solution
(ii) the solution is unique and
(iii) the solution depends continuously on the initial condition/data $y_0$ and $f$.

Why "Existence of solution":
(1) Not every differential equation can be solved explicitly, even implicit relations are difficult to obtain.
(2) Mathematicians are not interested in finding a solution for an appropriate problem and live happily thereafter.
(3) So we look for some results which tell us there exists a solution to the D.E.
(4) There are basically three types of differential equations:
(i) Equations for which the solution is known to exist.
(ii) Equations which do not admit any solution.

<!-- Page 16 -->
$\text{(III)}$ A third class of equations for which none of the existing theory provides a solution.

(5) In fact the third type is really a huge class and the mathematicians are generally excited when a new differential equation is solved which is relevant to the other branches of science. For example Navier-Stokes equations, clay mathematics, etc.

(6) Theoretical existence result gives a green signal for the engineers to solve them numerically.

Most of the time a differential equation along with its initial conditions corresponds to a real life problem or a physical process.

$\text{Uniqueness of solution}$: These physical problems should have a unique solution. Still if we could find more than one solution to the differential equation, we may need to go back to our basics.

<!-- Page 17 -->
$\text { Sometimes we would have ignored certain other other factors which describes the physical system or our understanding of the process was wrong. }$

$\text { Firstly, we will concentrate on some concepts which will be needed to discuss the existence and uniqueness of a DE. }$

$\text { Lipschitz condition: Let } f \text { be defined on an interval } I. \text { The function } f \text { is said to satisfy Lipschitz condition in } I \text { if } \exists \text { a constant } L > 0 \text { such that if } |f(t_1) - f(t_2)| \leq L |t_1 - t_2| \text { for } t_1, t_2 \in I. \text { Examples: }$

$\text { ① Using the mean value theorem, we can see that if } f \text { is differentiable on an interval } I, \text { then } f \text { is Lipschitz continuous on } I. \text { }$

$\text { ② Sint, cost, etc. etc. are Lipschitz continuous in any closed and bounded interval } [a, b].$

$\text { ③ } f(t) = |t| \text { is Lipschitz continuous on } [-1, 1] \text { by the triangle inequality, but not differentiable. }$

<!-- Page 18 -->
(4) Lipschitz continuous function must be continuous. (Verify!)

(5) $f(t) = \sqrt{t}$ is continuous but not Lipschitz continuous in $[0,1]$. Solution to (5): Note that we have to show

$$\frac{|f(t_1) - f(t_2)|}{|t_1 - t_2|} \leq L \quad \forall t_1, t_2 \in [0,1]$$

Choose $t_2 = 0$,

$$\frac{|f(t_1) - f(0)|}{|t_1 - 0|} = \frac{\sqrt{t_1}}{|t_1|} = \frac{1}{\sqrt{t_1}} \rightarrow \infty \quad \text{as} \quad |t_1| 0| \rightarrow 0$$

Here $f$ is continuous but not Lipschitz continuous.

(6) The function $f(t) = t^2$ is Lipschitz continuous in $[1,2]$.

(6) The function $f(x) = x^2$ is Lipschitz continuous in $[1,2]$.

(7) The function $f(x) = x^2$ is Lipschitz continuous on $[1,2]$.

$f(x_1) - f(x_2) = |x_1^2 - x_2^2| = |(x_1 + x_2)(x_1 - x_2)|$

$$\leq \max_{x_1, x_2 \in [1,2]} |(x_1 + x_2)(x_1 - x_2)| \leq 4|x_1 - x_2|$$

