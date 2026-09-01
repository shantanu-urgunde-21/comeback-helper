---
course: "differential equations"
source_file: "MA301 Lecture 4.pdf"
tags: ["math", "coursework", "differential-equations"]
---

# MA301 Lecture 4

<!-- Page 1 -->

## Lecture 4

1) A second order initial value problem **LHODE** (linear homogeneous ordinary differential equation)
$$y'' + p(x)y' + q(x)y = 0 \ ; \ y(x_0) = a \ , \ y'(x_0) = b$$
admits a unique solution in the interval around $x_0$ where $p(x)$ and $q(x)$ are continuous.

2) If $\{y_1, y_2\}$ are two solutions of **LHODE**, then $\{y_1, y_2\}$ are **LD** **iff** $W(y_1, y_2)(x) = 0$.

3) If $\{y_1, y_2\}$ are two solutions of **LHODE**, then $\{y_1, y_2\}$ are **LI** **iff** $W(y_1, y_2)(x) \neq 0$.

4) If $S$ denotes the set of all solutions of **LHODE**, then $S$ is a two dimensional vector space.

5) To find a second linearly independent solution if one solution is known:
$$y_2(x) = v(x) y_1(x) \text{, where } v(x) = \int \frac{e^{-\int p(x) dx}}{y_1^2(x)} dx$$
$$[\text{Tutorial Sheet 1}, \text{Problem 7}, c = 0]$$

<!-- Page 2 -->

### Remark: Higher order linear ODE:

1) An $n^{\text{th}}$ order initial value problem **LHODE** (linear homogeneous ordinary differential equation)
$$y^{(n)} + p_1(x) y^{(n-1)} + \dots + p_n(x) y = 0 \ ;$$
$$y(x_0) = a_0 \ ; \ y'(x_0) = a_1, \dots, y^{(n-1)}(x_0) = a_{n-1}$$
admits a unique solution in the interval around $x_0$ where $p_i(x)$ are continuous.

2) If $\{y_1, y_2, \dots, y_n\}$ are $n$ solutions of $n^{\text{th}}$ order **LHODE**, then $\{y_1, y_2, \dots, y_n\}$ are **LD** **iff**
$$W(y_1, y_2, \dots, y_n)(x) = 0.$$

3) If $\{y_1, y_2, \dots, y_n\}$ are $n$ solutions of $n^{\text{th}}$ order **LHODE**, then $\{y_1, y_2, \dots, y_n\}$ are **LI** **iff**
$$W(y_1, y_2, \dots, y_n)(x) \neq 0.$$

4) If $S$ denotes the set of all solutions of **LHODE**, then $S$ is an $n$ dimensional vector space.

<!-- Page 3 -->

### Remark:

1) From the theoretical results we developed, it is clear that a second order **LHODE** must have two linearly independent solutions.

2) It is at least important to know if we can solve a second order **LHODE** with constant coefficients; that is, when $p(x)$ and $q(x)$ are assumed to be constants.

We have developed enough theory to find all solutions

$$\text{(a)} - y'' + py' + qy = 0 \text{, where } p \text{ and } q$$
are constants in $\mathbb{R}$, that is, a second order homogeneous linear ODE with constant coefficients.

Suppose $e^{mx}$ is a solution of equation (a). Then,
$$m^2 e^{mx} + p m e^{mx} + q e^{mx} = 0.$$
$$\Rightarrow m^2 + pm + q = 0 \quad (e^{mx} \neq 0 \ \forall x)$$

<!-- Page 1 -->

This is called the **characteristic equation** or **auxiliary equation** of the linear homogeneous ODE with constant coefficients. Let the roots of this equation be $m_1$ and $m_2$.

We have the following three cases:

### Case 1 (Real & Unequal roots): 
Let $m_1, m_2 \in \mathbb{R}$ such that $m_1 \neq m_2$.

In this case $e^{m_1 x}, e^{m_2 x}$ are two linearly independent solutions of equation (a). (**Why?**)

So, the **general solution** of
$$y'' + p y' + q y = 0$$
is
$$y(x) = C_1 e^{m_1 x} + C_2 e^{m_2 x}, \quad C_1, C_2 \in \mathbb{R}.$$

---

### Case 2 (Real and equal roots): 
Let $m_1 = m_2 = m \in \mathbb{R}$.

Clearly $e^{mx}$ is a solution. Then, using the method in tutorial sheet 1, Problem 7, we have $v(x) e^{mx}$ as another solution (linearly independent to $e^{mx}$), where 
$$v(x) = \int \frac{e^{-\int p dx}}{y_1^2} dx \quad \text{--- (*)}$$

<!-- Page 2 -->

$$\left(\text{Recall } y_2(x) = y_1(x) \underbrace{\int \frac{e^{-\int p dx}}{(y_1(x))^2} dx}_{v(x)}, \text{ choose } C=0\right) \quad (\text{Tutorial Sheet 1})$$

In this case $v(x) = x$ (**solve!**)

Therefore, $e^{mx}$ and $x e^{mx}$ are two linearly independent solutions.

The **general solution** is given by
$$y(x) = (C_1 + C_2 x) e^{mx}, \quad C_1, C_2 \in \mathbb{R}.$$

---

#### Calculation of $v(x)$:

$$v(x) = \int \frac{e^{-\int p dx}}{y_1^2} dx$$

$$= \int \frac{e^{-px}}{e^{2mx}} dx = \int \frac{e^{2mx}}{e^{2mx}} dx = x$$

$$y_2(x) = v(x) y_1 = x e^{mx}$$

**Notes:**
* $m = -p/2$, roots are equal $\implies -p = 2m$
* $\begin{aligned}
\because m^2 + pm + q &= 0 \\
m &= \frac{-p \pm \sqrt{p^2 - 4q}}{2} \xrightarrow{\quad \text{roots are equal} \quad} m = -p/2
\end{aligned}$

<!-- Page 3 -->

### Case 3 (Complex roots): 
Here $m_1 = a + ib$, $m_2 = a - ib = \overline{m_1}$ where $a, b \in \mathbb{R}, b > 0$.

Now, 
$$e^{m_1 x}, e^{m_2 x}$$
$$e^{(a \pm ib)x} = e^{ax} (\cos bx \pm i \sin bx)$$
are two linearly independent solutions.

The general complex solution is
$$y(x) = e^{ax} \left(C_1 e^{ibx} + C_2 e^{-ibx}\right), \quad C_1, C_2 \in \mathbb{C}.$$

For **real** general solution, choose
$$C_1 = \frac{(A - iB)}{2}, \quad C_2 = \frac{(A + iB)}{2}, \quad A, B \in \mathbb{R}.$$

Therefore, the **general solution** is given by
$$y(x) = e^{ax} (A \cos bx + B \sin bx), \quad A, B \in \mathbb{R}.$$

---

**Example:** Solve the IVP
$$4y'' - 8y' + 3y = 0, \quad y(0) = 2, \, y'(0) = \frac{1}{2}.$$

**Solution:** The characteristic equation is
$$4m^2 - 8m + 3 = 0 \implies m = 3/2, \, 1/2$$

<!-- Page 1 -->

The general solution is given by
$$y(x) = C_1 e^{(\frac{3}{2})x} + C_2 e^{(\frac{1}{2})x}.$$

The initial conditions lead to
$$\left.\begin{aligned} C_1 + C_2 &= 2 \\ \frac{3}{2} C_1 + \frac{1}{2} C_2 &= \frac{1}{2} \end{aligned}\right\} \implies \begin{aligned} C_1 &= -1/2 \\ C_2 &= 5/2 \end{aligned}$$

$$\therefore y(x) = -\frac{1}{2} e^{\frac{3}{2}x} + \frac{5}{2} e^{\frac{1}{2}x}$$

---

### Example: Solve the IVP
$$y'' - 4y' + 4y = 0, \quad y(0) = 3, \quad y'(0) = 1.$$

### Solution:
The characteristic equation is
$$(m - 2)^2 = 0 \implies m = 2, 2.$$

The general solution is
$$y(x) = (C_1 + C_2 x) e^{2x}$$

$$y'(x) = (2 C_1 + C_2 + 2 C_2 x) e^{2x}.$$

The initial conditions imply $C_1 = 3, \quad 2 C_1 + C_2 = 1$
$$\implies C_2 = -5.$$

Therefore, $$y(x) = (3 - 5x) e^{2x}.$$

<!-- Page 2 -->

### Example: Solve the IVP
$$y'' - 6y' + 25y = 0, \quad y(0) = -3, \quad y'(0) = -1.$$

### Solution:
The characteristic equation is
$$m^2 - 6m + 25 = 0.$$
$$\implies m = 3 \pm 4i.$$

The general solution is
$$y(x) = e^{3x} (C_1 \cos 4x + C_2 \sin 4x).$$

Also,
$$y'(x) = 3e^{3x} (C_1 \cos 4x + C_2 \sin 4x) + e^{3x} (-4 C_1 \sin 4x + 4 C_2 \cos 4x).$$

The initial conditions imply
$$C_1 = -3, \quad 3 C_1 + 4 C_2 = -1$$
$$\implies C_1 = -3, \quad C_2 = 2.$$

$$\therefore y(x) = e^{3x} (-3 \cos 4x + 2 \sin 4x)$$

<!-- Page 3 -->

# Non-homogeneous second Order ODE

Consider the non-homogeneous DE (Differential Equation):
$$y'' + p(x) y' + q(x) y = r(x),$$
where $p(x)$, $q(x)$ and $r(x)$ are continuous functions on an interval $I$.

The associated homogeneous DE is
$$y'' + p(x) y' + q(x) y = 0.$$

Can we relate the solutions of the above two DE's?

### Theorem:
Let $y_p(x)$ be any solution of
$$y'' + p(x) y' + q(x) y = r(x)$$
and $y_1(x), y_2(x)$ be a basis of the solution space of the corresponding homogeneous DE.

Then, the set of solutions of the non-homogeneous DE is
$$\{ C_1 y_1(x) + C_2 y_2(x) + y_p(x) \mid C_1, C_2 \in \mathbb{R} \}.$$

### Proof:
Let $\phi(x)$ be any solution of
$$L(y) = y'' + p(x) y' + q(x) y = r(x).$$

<!-- Page 1 -->

Then, $L(\phi(x) - y_p(x)) = L(\phi(x)) - L(y_p(x))$
$$\phantom{L(\phi(x) - y_p(x))} = r(x) - r(x) = 0.$$

Therefore, $\phi(x) - y_p(x)$ is a solution of the homogeneous DE. Thus,
$$\phi(x) - y_p(x) = C_1 y_1(x) + C_2 y_2(x),$$
for $C_1, C_2 \in \mathbb{R}$.

Therefore,
$$\phi(x) = C_1 y_1(x) + C_2 y_2(x) + y_p(x).$$

---

$\underline{\text{Summary}} :$ In order to find the general solution of a non-homogeneous DE, we need to:

1) get one particular solution of the non-homogeneous DE.
2) get the general solution of the corresponding homogeneous DE.

<!-- Page 2 -->

### Method of variation of parameters (a method to obtain $y_p(x)$)

A method to find a particular solution of a non-homogeneous ODE is **the method of variation of parameters**.

Here, we vary the constants $C_1, C_2$ in the general solution
$$y(x) = C_1 y_1(x) + C_2 y_2(x)$$
of the associated homogeneous equation
$$y'' + p(x)y' + q(x)y = 0.$$

That is, we replace the constants $C_1, C_2$ by functions $v_1(x), v_2(x)$ so that
$$y_p(x) = v_1(x)y_1(x) + v_2(x)y_2(x)$$
is a solution of
$$y'' + p(x)y' + q(x)y = r(x)$$

Now, $y_p'(x) = v_1 y_1' + v_2 y_2' + v_1' y_1 + v_2' y_2$.

Let us also demand
$$v_1' y_1 + v_2' y_2 = 0. \qquad \text{--- (1)}$$

Thus,
$$y_p'' = v_1 y_1'' + v_1' y_1' + v_2 y_2'' + v_2' y_2'.$$

<!-- Page 3 -->

Substituting $y_p, y_p', y_p''$ in the given non-homogeneous ODE and rearranging the terms, we get

$$v_1 (y_1'' + p y_1' + q y_1) + v_2 (y_2'' + p y_2' + q y_2) + v_1' y_1' + v_2' y_2' = r(x).$$

Therefore,
$$v_1' y_1' + v_2' y_2' = r(x). \qquad \text{--- (2)}$$

Recall that, we also have (from (1))
$$v_1' y_1 + v_2' y_2 = 0.$$

Thus, we have
$$\begin{bmatrix} y_1 & y_2 \\ y_1' & y_2' \end{bmatrix} \begin{bmatrix} v_1' \\ v_2' \end{bmatrix} = \begin{bmatrix} 0 \\ r(x) \end{bmatrix}.$$

Hence,
$$v_1' = \frac{\begin{vmatrix} 0 & y_2 \\ r(x) & y_2' \end{vmatrix}}{W(y_1, y_2)}, \quad v_2' = \frac{\begin{vmatrix} y_1 & 0 \\ y_1' & r(x) \end{vmatrix}}{W(y_1, y_2)}.$$

On solving, we obtain
$$v_1 = -\int \frac{y_2 r(x)}{W(y_1, y_2)(x)} \, dx, \quad v_2 = \int \frac{y_1 r(x)}{W(y_1, y_2)(x)} \, dx.$$

<!-- Page 1 -->

Therefore,
$$y_p = v_1 y_1 + v_2 y_2$$
$$= y_2 \int \frac{y_1 r(x)}{W(y_1, y_2)(x)} \, dx - y_1 \int \frac{y_2 r(x)}{W(y_1, y_2)(x)} \, dx.$$

Hence, the general solution of the non-homogeneous equation is
$$y = c_1 y_1 + c_2 y_2 + y_p .$$

**Example:** Find a particular solution of
$$y'' + y = \operatorname{cosec} x .$$

**Solution:**
**Step 1:** Find a basis of solutions for the associated homogeneous equation
$$y'' + y = 0 \quad \text{--- } \text{①}$$

The general solution of ① is
$$y(x) = c_1 \sin x + c_2 \cos x$$

**Step-II** Calculate the Wronskian $W(y_1, y_2)(x)$.
$$W(y_1, y_2)(x) = \begin{vmatrix} \sin x & \cos x \\ \cos x & -\sin x \end{vmatrix} = -1 \neq 0 .$$

<!-- Page 2 -->

Now,
$$v_1(x) = -\int \frac{y_2 r(x)}{W(y_1, y_2)(x)} = -\int \frac{\cos x \operatorname{cosec} x}{-1} \, dx$$
$$= \ln |\sin x| .$$

$$v_2(x) = \int \frac{y_1 r(x)}{W(y_1, y_2)(x)} \, dx = \int \frac{\sin x \operatorname{cosec} x}{-1} \, dx$$
$$= -x$$

Therefore, a particular solution is
$$y_p(x) = \sin x \ln |\sin x| - x \cos x .$$

What about the general solution?

**Example:** Find the general solution of
$$y'' - y' - 2y = e^{-x} .$$

**Solution:** A basis of solutions of the corresponding homogeneous equation is
$$y_1(x) = e^{2x}, \quad y_2(x) = e^{-x} .$$

Now,
$$W(y_1, y_2)(x) = \begin{vmatrix} e^{2x} & e^{-x} \\ 2e^{2x} & -e^{-x} \end{vmatrix} = -3e^x$$

<!-- Page 3 -->

Thus, a particular solution is
$$y_p(t) = v_1(t) y_1(t) + v_2(t) y_2(t) .$$

Write the general solution!

<!-- Page 1 -->

### Tutorial Sheet 1

9. Find a second order linear homogeneous ODE of the form $(*)$ for which $\{x, x \ln x\}$ are two linearly independent solutions. Subsequently solve $y'' + py' + qy = x$. (Answer: $c_1 x + c_2 x \ln x + x^3/4$.)

---

### Solution:

Given $\{x, x \ln x\}$ are solution of
$$y'' + p(x) y' + q(x) y = 0 \quad \text{--- } (*)$$

**Find $p(x)$ and $q(x)$!**

Put $y(x) = x$ in $(*)$, we have
$$p(x) + q(x) x = 0 \implies p(x) = -x q(x)$$

Put $y(x) = x \ln x$, $y'(x) = x \times \frac{1}{x} + \ln x = 1 + \ln x$,  
$y''(x) = \frac{1}{x}$ in $(*)$,

$$\frac{1}{x} + p(x)(1 + \ln x) + q(x)(x \ln x) = 0$$
$$\implies \frac{1}{x} + (-x q(x))(1 + \ln x) + x \ln x \, q(x) = 0$$
$$\implies \frac{1}{x} - x q(x) = 0 \implies \boxed{q(x) = \frac{1}{x^2}}$$

$$p(x) = -x q(x) \implies p(x) = -x \left(\frac{1}{x^2}\right) = -\frac{1}{x}$$

Therefore, the desired homogeneous differential equation is
$$y'' + p(x) y' + q(x) y = 0$$
$$\implies y'' - \frac{1}{x} y' + \frac{1}{x^2} y = 0$$

---
<!-- Page 2 -->

The solution to homogeneous problem is
$$y_h(x) = c_1 x + c_2 x \ln x .$$

Now, the general solution to non-homogeneous ODE
$$y'' - \frac{1}{x} y' + \frac{1}{x^2} y = x$$

is
$$y(x) = \underbrace{c_1 x + c_2 x \ln x}_{y_h(x)} + \underbrace{y_p(x)}_{\text{Particular solution}} ,$$

where $y_p(x)$ can be found using the method of variation of parameters

**Complete !**

---
<!-- Page 3 -->

### Method of Variation of Parameters

$$W = \begin{vmatrix} x & x \ln x \\ 1 & \ln x + 1 \end{vmatrix} = x$$

The right hand side function is $r(x) = x$.

Therefore
$$v_1' = \frac{-y_2 r(x)}{W} = \frac{-x \ln x \cdot x}{x} = -x \ln x$$
$$v_2' = \frac{y_1 r(x)}{W} = \frac{x \cdot x}{x} = x$$

$$\implies v_1 = -\int x \ln x \, dx = -\left( \frac{x^2}{2} \ln x - \frac{x^2}{4} \right)$$
$$v_2 = \int x \, dx = \frac{x^2}{2}$$

Hence, $y_p(x) = v_1 y_1 + v_2 y_2$
$$= x \left( -\frac{x^2}{2} \ln x + \frac{x^2}{4} \right) + \frac{x^2}{2} (x \ln x)$$
$$= \frac{x^3}{4}$$

<!-- Page 1 -->

**Prob:** Show that if $y_1$ and $y_2$ are two linearly independent solutions of $(*)$, then in between two consecutive zeros of $y_1$, there must be a unique zero of $y_2$.

## **Solution.**

Let $a, b$ be two consecutive zeros of $y_1$ with $a < b$.  
$\because y_1 \text{ \& } y_2$ are a fundamental set of solutions, their Wronskian
$$W(y_1, y_2) = y_1 y_2' - y_1' y_2$$
is not zero for all $t$. This implies neither $a$ or $b$ are the zeros of $y_2$.

Now, we use the method of contradiction to prove $y_2$ has at least one zero in $(a, b)$.

Let $y_2$ does not vanish in $(a, b)$. Then,
$$u := \frac{y_1}{y_2} \quad \text{is differentiable there.}$$
$$u' = \frac{-W}{y_2^2}$$

By observation neither $a$ or $b$ are zeros of $y_2$, we have $u(a) = u(b) = 0$. By Rolle's theorem, there is some point $c \in (a, b)$ where $u'(c) = 0$.

$\implies W$ vanishes. This contradicts the fact that $W$ never vanishes.

<!-- Page 2 -->

For uniqueness, assume $y_2$ has two roots in $(a, b)$, say $c$ and $d$. Apply the same arguments as above to the function $v = \frac{y_2}{y_1}$ and arrive at the contradiction.

$\implies y_2$ has a unique zero between any two consecutive zeros of $y_1$.

