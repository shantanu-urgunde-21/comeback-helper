---
course: "differential equations"
source_file: "Lecture notes 7 to 9 (1).pdf"
tags: ["math", "coursework", "differential-equations"]
---

# Lecture notes 7 to 9 (1)

<!-- Page 1 -->

$$25/03/2025 \qquad \text{Lecture } - 7$$

Now, we will start with definitions which will be used in the subsequent explanation.

**Definition :** (from calculus) : Let '$f$' be a function of two real variables such that '$F$' has 'continuous' first order partial derivatives in a domain $D$. The total differential $dF$ of $F$ is defined by the formula

$$\boxed{d F(x,y) = F_x(x,y) dx + F_y(x,y) dy}$$

for all $(x,y) \in D$, where $F_x = \frac{\partial F}{\partial x}$ & $F_y = \frac{\partial F}{\partial y}$.

**Definition :** The differential equation

$$M(x,y) dx + N(x,y) dy = 0$$

is called an exact differential equation if there exists a function $F(x,y) \in D \subset \mathbb{R}^2$, such that

$$F_x(x,y) = M(x,y) \quad \text{and} \quad F_y(x,y) = N(x,y)$$

for all $(x,y) \in D$.

Note that, here $D$ denotes a bounded domain in $\mathbb{R}^2$.

---

<!-- Page 2 -->

So, now if an ODE

$$M(x,y) + N(x,y) \frac{dy}{dx} = 0$$

is exact then there exists a function $F(x,y)$ such that $F_x(x,y) = M(x,y)$ and $F_y(x,y) = N(x,y) \implies$

$$M(x,y) dx + N(x,y) dy = \frac{\partial F}{\partial x} dx + \frac{\partial F}{\partial y} dy = 0$$

$$\implies dF = 0$$

$$\text{or } \boxed{F(x,y) = C}$$

is implicit / formal solution to the given ODE.

**Example :** Is $\underbrace{(2x+y^2)}_{M} + \underbrace{2xy}_{N} \frac{dy}{dx} = 0$ exact? Why!

Yes, the given ODE is exact. Consider the function $F(x,y) = x^2 + xy^2$. Note that,

$$\begin{aligned}
F_x &= 2x + y^2, & F_y &= 2xy \\
&= M & &= N
\end{aligned}$$

Therefore, $x^2 + xy^2 = C$ is the solution of the given ODE.

---

<!-- Page 3 -->

**Theorem :** Let $D$ denotes a bounded domain in $\mathbb{R}^2$. Assume that $M(x,y)$ and $N(x,y) \in C^1(D)$. Then the following two statements are equivalent:

(1) $M(x,y) + N(x,y) y' = 0$ is exact.

(2) $M_y(x,y) = N_x(x,y)$ for all $(x,y) \in D$,

where $M_y(x,y) = \frac{\partial M(x,y)}{\partial y}$ and $N_x(x,y) = \frac{\partial N(x,y)}{\partial x}$.

**Proof :** $(1) \implies (2)$. Since $M dx + N dy = 0$ is exact. Then there exists a function $F$ such that

$$F_x = M \quad \text{and} \quad F_y = N.$$

Since $M$ and $N$ are given to be $C^1$ functions $\implies M_y = F_{x,y}$ and $N_x = F_{y,x}$.

$$\boxed{F_{x,y} = F_{y,x}} \quad \text{and thus} \quad \boxed{M_y = N_x}$$

Note that, here we have used a result from the mixed order partial derivatives

$$F_{x,y} = F_{y,x}$$

where $F_{x,y} = \frac{\partial^2 F}{\partial x \partial y}$, $F_{y,x} = \frac{\partial^2 F}{\partial y \partial x}$.

Reference for this result: A course in Multivariable calculus & Analysis
- Sudhir R. Ghorpade & B.V. Limaye

<!-- Page 4 -->

The converse part is more technical, ... (4)

**Proposition (3.14) : (Mixed Partials Theorem) :**

Let $D \subseteq \mathbb{R}^2$ be an open set and let $(x_0, y_0)$ be any point of $D$. Let $f : D \to \mathbb{R}$ be such that both $f_x$ and $f_y$ exist on $D$. If $f_{xy}$ or $f_{yx}$ exists on $D$ and is continuous at $(x_0, y_0)$, then both $f_{xy}(x_0, y_0)$ and $f_{yx}(x_0, y_0)$ exist and
$$f_{xy}(x_0, y_0) = f_{yx}(x_0, y_0).$$

*(It will be discussed in the tutorial session)*

**Example :** Solve the DE
$$4x + 3y + 3(x + y^2) y' = 0.$$

Note that, $M, N \in C^1(\mathbb{R})$ and $M_y = N_x = 3$.

Therefore, the equation is exact.

There exists a function $F(x,y)$ such that
$$F_x = 4x + 3y, \quad F_y = 3(x + y^2). \quad \text{--- (1)}$$

$$\therefore F_x = 4x + 3y \implies F(x,y) = 2x^2 + 3xy + \phi(y) \quad \text{--- (2)}$$

Now from (1) and (2), we have
$$3x + 3y^2 = F_y(x,y) = 3x + \phi'(y)$$

<!-- Page 5 -->

(5)

$$\implies \phi'(y) = 3y^2 \implies \phi(y) = y^3.$$

Thus, from (2), $F(x,y) = 2x^2 + 3xy + y^3$.

The general solution is given by
$$\boxed{2x^2 + 3xy + y^3 = c.}$$

**Example :** Solve the DE
$$(y\cos x + 2x e^y) + (\sin x + x^2 e^y - 1) y' = 0.$$

**Sol$^n$ :** Here $M = y\cos x + 2x e^y$
$$N = \sin x + x^2 e^y - 1$$

Is this equation exact?

Check whether $\boxed{M_y = N_x}$?

The answer is Yes.

By the previous result, there exists a function $F(x,y)$ such that
$$F_x = M \quad \text{and} \quad F_y = N.$$

Now,
$$F_x = y\cos x + 2x e^y \quad \text{--- (*)}$$
$$F_y = \sin x + x^2 e^y - 1 \quad \text{--- (**)}$$

After integrating (*), we obtain
$$F(x,y) = \int (y\cos x + 2x e^y) dx + \phi(y)$$
$$= y\sin x + x^2 e^y + \phi(y)$$

<!-- Page 6 -->

(6)

Therefore,
$$F_y = \sin x + x^2 e^y + \phi'(y) \quad \text{--- (***)}$$

From (**) and (***), we obtain
$$\sin x + x^2 e^y + \phi'(y) = \sin x + x^2 e^y - 1$$
$$\implies \phi'(y) = -1 \implies \phi(y) = -y.$$

Therefore, we have
$$F(x,y) = y\sin x + x^2 e^y - y = c$$
as a general solution to DE.

**Definition :** If the equation
$$M(x,y)dx + N(x,y)dy = 0 \quad \text{--- (*)}$$
is not exact, but the equation
$$\mu(x,y)\{ M(x,y)dx + N(x,y)dy \} = 0$$
is exact, then $\mu(x,y)$ is called an **integrating factor** of equation (*).

**Theorem :** If $\frac{M_y - N_x}{N}$ is continuous and depends only on $x$, then
$$\mu(x) = \exp \left( \int \left(\frac{M_y - N_x}{N}\right) dx \right) \quad \text{--- (**)}$$
is an integrating factor for $Mdx + Ndy = 0$.

<!-- Page 7 -->

### Solution:

If $u(x,y)$ is an integrating factor then we must have

$$ \boxed{\frac{\partial}{\partial y} (u M) = \frac{\partial}{\partial x} (u N)} \quad \text{— Claim} $$

or we have to prove

$$ \boxed{\frac{\partial}{\partial y} (u M) - \frac{\partial}{\partial x} (u N) = 0} \quad \text{— (a)} $$

If $u = u(x) = e^{\int \left( \frac{M_y - N_x}{N} \right) dx}$, then

$$ \frac{du}{dx} = e^{\int \left( \frac{M_y - N_x}{N} \right) dx} \times \left( \frac{M_y - N_x}{N} \right) $$

$$ \boxed{\frac{du}{dx} = \left( \frac{M_y - N_x}{N} \right) u} \quad \text{— (b)} $$

Now L.H.S. of **(a)** is as follows:

$$ \frac{\partial}{\partial y} (u M) - \frac{\partial}{\partial x} (u N) = \underbrace{u_y}_{=0} M + u M_y - u_x N - u N_x $$
$$ \text{(as } u \text{ is a function of } x \text{ alone)} $$

$$ = u M_y - \left( \frac{M_y - N_x}{N} \right) u N - u N_x \quad \text{(using (b))} $$

$$ = u M_y - u M_y + u N_x - u N_x = 0 = \text{R.H.S.} $$

$$ \text{Hence proved!} $$

---

<!-- Page 8 -->

### Example:

Solve $\underbrace{(2x^2 + y)}_{M} dx + \underbrace{(x^2 y - x)}_{N} dy = 0 \quad \text{— (1)}$

The equation is not exact as $M_y = 1 \neq 2xy - 1 = N_x$.

Note that
$$ \frac{M_y - N_x}{N} = \frac{1 - 2xy + 1}{-x(1 - xy)} = \frac{2(1 - xy)}{-x(1 - xy)} = \frac{-2}{x} $$

which is a function of only $x$.

Therefore, from equation (**), we have

$$ u(x) = e^{-\int \frac{2}{x} dx} = x^{-2} $$

as an integrating factor.

Now, multiply **(1)** by $u(x)$. Then the resulting equation is an exact equation.

One can solve using the method for exact ODE and obtain the following general solution:

$$ \boxed{2x + \frac{y^2}{2} - 2yx^{-1} = c} $$

---

### Theorem:

If $\frac{N_x - M_y}{M}$ is continuous and depends only on $y$, then

$$ u(y) = \exp \left( \int \left\{ \frac{N_x - M_y}{M} \right\} dy \right) \quad \text{— (c)} $$

is an integrating factor for $M dx + N dy = 0$.

---

<!-- Page 9 -->

### Example:

$$ xy \, dx + (2x^2 + 3y^2 - 20) \, dy = 0 $$

Verify that this is not an exact DE.

Here $M(x,y) = xy$ and $N(x,y) = 2x^2 + 3y^2 - 20$.

Then
$$ \frac{M_y - N_x}{N} = \frac{-3x}{2x^2 + 3y^2 - 20} $$
depends on $x$ and $y$ and gets nowhere.

Note that
$$ \frac{N_x - M_y}{M} = \frac{3}{y} $$
a function of $y$ alone. By the result of equation **(c)**, an integrating factor is

$$ \boxed{u(y) = y^3} $$

Then, multiplying by the integrating factor we obtain

$$ xy^4 \, dx + (2x^2 y^3 + 3y^5 - 20y^3) \, dy = 0 $$

This is an exact ODE.

Show that the solution is

$$ \boxed{\frac{1}{2} x^2 y^4 + \frac{1}{2} y^6 - 5 y^4 = c} $$

---

### Example:

Solve the ODE

$$ (8xy - 9y^2) + (2x^2 - 6xy) \frac{dy}{dx} = 0 $$

Here $M = 8xy - 9y^2, \quad N = 2x^2 - 6xy$.

<!-- Page 10 -->

Thus, $M_y = 8x - 18y$ and $N_x = 4x - 6y$.

As $M_y \neq N_x$, the given ODE is not exact. Note that
$$\frac{M_y - N_x}{N} = \frac{4x - 12y}{2x(x - 3y)} = \frac{2}{x}, \text{ is a}$$

function of $x$ alone.

So from equation (*), an integrating factor is $\boxed{u(x) = x^2}$.

Multiplying the given ODE by $u(x) = x^2$, we get
$$(8x^3 y - 9x^2 y^2) + (2x^4 - 6x^3 y)y' = 0.$$

Verify that this is an exact ODE.

Now, there exists a function $F(x,y)$ such that $F_x = 8x^3 y - 9x^2 y^2$ and $F_y = 2x^4 - 6x^3 y$.

$$F(x,y) = 2x^4 y - 3x^3 y^2 + \phi(y)$$
$$F_y(x,y) = 2x^4 - 6x^3 y + \phi'(y) = 2x^4 - 6x^3 y$$

Thus $\phi'(y) = 0$. Therefore,

$$F(x,y) = 2x^4 y - 3x^3 y^2 = c \text{ is a general}$$
solution of the given ODE.

---

<!-- Page 11 -->

Problem: Consider the equation $y' = y; y(0) = 1$
show that $y = e^x$ is the only solution of the above differential equation.

Existence of solution: Substitute $y = e^x$ in the equation $y' = y$ and show that it satisfies the differential equation and the initial condition.

Uniqueness: Let $y_1 = e^x$ and $y_2$ be any other solution of the ODE $y' = y; y(0) = 1$.

In general, to prove uniqueness, we either prove $y_2 - y_1 = 0$ or $\frac{y_2}{y_1} = 1$. Here, since $y_1(x) \neq 0$, we will show that $\frac{y_2}{y_1} = 1$.

Now,
$$\left( \frac{y_2}{y_1} \right)' = \frac{y_1 y_2' - y_1' y_2}{y_1^2} = \frac{e^x y_2' - e^x y_2}{e^{2x}}$$
$$= e^{-x}(y_2' - y_2) = 0, \quad \text{since } y_2(x) \text{ satisfies}$$
the differential equation and $e^{-x} \neq 0$.

This implies $\frac{y_2}{y_1} = k$. Now $y_1(0) = 1 = y_2(0)$

$$\implies k = 1 \implies y_2(x) = y_1(x) \quad \forall x.$$

---

<!-- Page 12 -->

Exercise 1: Solve $(4x + 2y + 5)y' + (2x + y - 1) = 0$.

Hint: Substitution $v = 2x + y$ reduces to the variable separable form.

Exercise 2: Solve $y' = \frac{x + y - 3}{x - y - 1}$

Hint: Substitute $x = \xi + h, y = \eta + k$ for some $h, k$ which will be determined

$$\frac{d\eta}{d\xi} = \frac{dy}{dx} = \frac{\xi + \eta + h + k - 3}{\xi - \eta + h - k - 1}$$

choose $h, k$ such that
$$h + k - 3 = 0$$
$$h - k - 1 = 0$$

This choice makes the equation homogeneous.

Problem: Suppose $M$ and $N$ are continuous and have continuous partial derivatives $M_y$ and $N_x$ that satisfy the condition $M_y = N_x$ on an open rectangle $\mathcal{R} = \{ |x - x_0| < a, |y - y_0| < b \}$ around $(x_0, y_0)$. Show that if $(x,y) \in \mathcal{R}$ and

$$F(x,y) = \int_{x_0}^x M(s, y_0) \, ds + \int_{y_0}^y N(x, t) \, dt \quad \text{--- } (*)$$

then $F_x = M$ and $F_y = N$. (This is the converse of the theorem which was left unproved in the class).

<!-- Page 1 -->

13

$\text{Sol}^n:$ Note that, from $(*)$ we have from the first fundamental theorem of integral calculus

$$\boxed{F_y (x,y) = N(x,y) \quad \forall x,y \in \mathbb{R}}$$

Define \qquad $F(x,y) = \int_{x_0}^x M(s,y) + \int_{y_0}^y N(x_0,t) + t \qquad (**)$

$$\boxed{F_x (x,y) = M(x,y) \quad \forall \quad (x,y) \in \mathbb{R}}$$

We need to show that $F$ defined in $(*)$ and $(**)$ are same.

$$\underbrace{F (x,y)}_{\text{From } (**)} - \overbrace{\left[ \int_{y_0}^y N(x,t) dt + \int_{x_0}^x M(s,y_0) ds \right]}^{(\text{from } *)}$$

$$= \int_{x_0}^x [M(s,y) - M(s,0)] ds - \int_{y_0}^y [N(x,t) - N(x_0,t)] dt$$

$$= \int_{x_0}^x \left[ \int_{y_0}^y \frac{\partial M}{\partial t}(s,t) dt \right] ds - \int_{y_0}^y \left[ \int_{x_0}^x \frac{\partial N}{\partial s}(s,t) ds \right] dt$$

$$= \int_{x_0}^x \int_{y_0}^y \left[ \frac{\partial M}{\partial t}(s,t) - \frac{\partial N}{\partial s}(s,t) \right] ds dt = 0$$

$$\left(\because M_y = N_x \text{ given condition}\right)$$

Therefore, the two definitions in $(*)$ and $(**)$ for $F(x,y)$ are same.

---

<!-- Page 2 -->

Consider the following initial value problem:
$$\begin{cases} y'(x) = f(x,y) & \text{(Differential Equation)} \\ y(x_0) = y_0 & \text{(Initial condition)} \end{cases}$$

Example:

(1) The differential equation $y' = y$, $y(0) = 1$ is known to admit a unique solution.

(2) The differential equation $y' = \sqrt{y}$, $y(0) = 0$, admits at least two solutions.
A solution $y_1(x) = \frac{x^2}{4}$ can be obtained by variable separable method and by inspection $y_2(x) = 0$ is also a solution.

(3) The DE $|y'| + |y| = 0$, $y(0) = 3$ admits no solution. The DE $|y'| + |y| + 1 = 0$ also admits no solution for whatever initial condition we impose.

(4) The DE $y'(x) = \sqrt{x}$, $y(0) = 0$ admits the unique solution $y(x) = \frac{2}{3} x^{3/2}$.

$\implies$ Question: What can we observe about the existence / uniqueness of the IVP $y' = f(x,y)$, $y(x_0) = y_0$?

---

<!-- Page 3 -->

(1)

Hadamard's criterion for well-posed IVP:

An IVP is said to be \underline{well posed} if
(i) it has a solution
(ii) the solution is unique and
(iii) the solution depends continuously on the initial condition / data $y_0$ and $f$.

Why "Existence of solution":

(1) Not every differential equation can be solved explicitly, even implicit relations are difficult to obtain.

(2) Mathematicians are not interested in finding a solution for an appropriate problem and live happily thereafter.

(3) So we look of some results, which tell us there exists a solution to the DE.

(4) There are basically three types of differential equations:
(i) Equations for which solution is known to exist.
ii) Equations which do not admit any solution.

<!-- Page 1 -->

(iii) A third class of equations for which none of the existing theory provides a solution.

(5) In fact the third type is really a huge class and the mathematicians are generally excited when a new differential equation is solved which is relevant to the other branches of science. For example Navier-Stokes equations, Clay Mathematics Institute etc.

(6) Theoretical existence result gives a green signal for the engineers to solve them numerically.

Most of the time a differential equation along with its initial conditions corresponds to a real life problem or a physical process.

**Uniqueness of solution:** These physical problems should have a unique solution. Still if we could find more than one solution to the differential equation, we may need to go back to our basics.

<!-- Page 2 -->

Sometimes we would have ignored certain other factors which describes the physical system or our understanding of the process was wrong.

Firstly, we will concentrate on some concepts which will be needed to discuss the existence and uniqueness of a DE.

**Lipschitz condition:** Let $f$ be defined on an interval $I$. The function $f$ is said to satisfy Lipschitz condition in $I$ if $\exists$ a constant $L > 0$ such that
$$|f(t_1) - f(t_2)| \le L |t_1 - t_2| \quad \forall t_1, t_2 \in I.$$

**Examples:**
1. Using mean value theorem, we can see that if $f$ is differentiable and the derivative is bounded in some interval $I$, then $f$ is Lipschitz continuous on $I$.

2. $\sin t$, $\cos t$, $e^t$ etc are Lipschitz in any closed and bounded interval $[a, b]$.

3. $f(t) = |t|$ is Lipschitz continuous on $[-1, 1]$ by triangle inequality, but not differentiable.

<!-- Page 3 -->

(4) Lipschitz continuous function must be continuous. (Verify!)

(5) $f(t) = \sqrt{t}$ is continuous but not Lipschitz continuous in $[0, 1]$.

**Solution to (5):** Note that we have to show
$$\frac{|f(t_1) - f(t_2)|}{|t_1 - t_2|} \le L \quad \forall t_1, t_2 \in [0, 1].$$

$$f(t) = \sqrt{t}.$$

$$\frac{|f(t_1) - f(t_2)|}{|t_1 - t_2|} = \frac{\sqrt{t_1} - \sqrt{t_2}}{|t_1 - t_2|}$$

Choose $t_2 = 0$,
$$\frac{|f(t_1) - f(0)|}{|t_1 - 0|} = \frac{\sqrt{t_1}}{t_1} = \frac{1}{\sqrt{t_1}} \to \infty \quad \text{as } t_1 \to 0.$$

Here $f$ is continuous but not Lipschitz continuous.

(6) The function $f(t) = t^2$ is Lipschitz in $[1, 2]$ (locally Lipschitz)
$$|f(t_1) - f(t_2)| = |t_1^2 - t_2^2| = |t_1 + t_2| |t_1 - t_2|$$
$$\le \left( \max_{t \in [1, 2]} |t_1 + t_2| \right) |t_1 - t_2|$$
$$\le 4 |t_1 - t_2|$$
Therefore, $f$ is Lipschitz continuous on $[1, 2]$.

(7) The function $f(x) = x^2$ is Lipschitz in $[1, 2]$ (locally Lipschitz)
$$|f(x_1) - f(x_2)| = |x_1^2 - x_2^2| = |(x_1 + x_2)(x_1 - x_2)|$$
$$\le \max_{x_1, x_2 \in [1, 2]} |(x_1 + x_2)(x_1 - x_2)| \le 4 |x_1 - x_2|.$$

