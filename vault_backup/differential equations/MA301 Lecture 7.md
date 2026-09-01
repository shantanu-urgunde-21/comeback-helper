---
course: "differential equations"
source_file: "MA301 Lecture 7.pdf"
tags: ["math", "coursework", "differential-equations"]
---

# MA301 Lecture 7

<!-- Page 1 -->
## Theorem 1.6 : Lecture 7

**Hypothesis:** Consider the homogeneous system of the form

$$
\left.
\begin{aligned}
\frac{dx}{dt} &= a_{11}(t) x + a_{12}(t) y \\
\frac{dy}{dt} &= a_{21}(t) x + a_{22}(t) y
\end{aligned}
\right\} \quad -(2)
$$

$$
\Rightarrow \begin{cases}
\frac{df_1}{dt} = a_{11}(t) f_1 + a_{12}(t) g_1 \\
\frac{dg_1}{dt} = a_{21}(t) f_1 + a_{22}(t) g_1
\end{cases}
$$

$$
\Rightarrow \begin{cases}
\frac{df_2}{dt} = a_{11}(t) f_2 + a_{12}(t) g_2 \\
\frac{dg_2}{dt} = a_{21}(t) f_2 + a_{22}(t) g_2
\end{cases}
$$

Let $x^{(1)}(t) = (f_1(t), g_1(t))$ and $x^{(2)}(t) = (f_2(t), g_2(t))$ be the two solutions of the homogeneous linear system in (2). Let $c_1$ and $c_2$ be two arbitrary constants.

Note that

$$
\left\{
\begin{aligned}
& c_1 x^{(1)} + c_2 x^{(2)} \\
& c_1(f_1, g_1) + c_2(f_1, g_2) \\
& (\underbrace{c_1 f_1 + c_2 f_2}_{\text{first component}}, \quad \underbrace{c_1 g_1 + c_2 g_2}_{\text{second component}})
\end{aligned}
\right.
$$

**Conclusion:** Then, $c_1 x^{(1)}(t) + c_2 x^{(2)}(t)$

$$
(x = c_1 f_1(t) + c_2 f_2(t), \quad y = c_1 g_1(t) + c_2 g_2(t)) \quad -(e_1)
$$

is also a solution of the system in (2).

In other words, a linear combination of the solutions is again a solution for a homogeneous system in (2).

<!-- Page 2 -->
**Proof:**
$$ \frac{dx}{dt} = C_1 \frac{df_1}{dt} + C_2 \frac{df_2}{dt} $$
$$ = C_1 \left( a_{11}(t)f_1 + a_{12}(t)g_1 \right) + C_2 \left( a_{11}(t)f_2 + a_{12}(t)g_2 \right) $$
$$ = a_{11}(t) (C_1 f_1 + C_2 f_2) + a_{12}(t) (C_1 g_1 + C_2 g_2) $$
$$ = a_{11}(t) x + a_{12}(t) y $$

$$ \text{Ill}^y \quad \frac{dy}{dt} = a_{21}(t) x + a_{22}(t) y . $$

$$ \Rightarrow (x(t), y(t)) \text{ is a solution of } \text{\textcircled{2}}. $$
$$ \text{or} $$
$$ (C_1 f_1(t) + C_2 f_2(t), C_1 g_1(t) + C_2 g_2(t)) \text{ is a solution of } \text{\textcircled{2}}. $$

---

**Example 1.7:** Consider the system
$$ \left. \begin{aligned} \frac{dx}{dt} &= 3x + y, \\ \frac{dy}{dt} &= 6x + 4y \end{aligned} \right\} \quad (*) $$

We have already verified that

1. $(x = e^{6t}, y = 3e^{6t})$ is a solution pair of the given system.
2. $(x = e^t, y = -2e^t)$ is a solution pair of the given system.

<!-- Page 3 -->
Now, verify that
($x = c_1 e^{6t} + c_2 e^t, y = 3c_1 e^{6t} - 2c_2 e^t$)
is a solution for the considered system
any real $c_1, c_2$.

Question : Does ($e_1$) contains all solutions
of system (2)?

Now, we will focus on answering this
question.

<!-- Page 1 -->
Linear dependence and independence:

A set of functions $\{\phi_1(x), \phi_2(x), \dots, \phi_n(x)\}$ are said to be linearly independent on an interval $I$ if for some constants $c_1, c_2, \dots, c_n \in \mathbb{R}$,

$$\sum_{j=1}^n c_j \phi_j(x) = 0 \quad \forall x \in I \implies c_1 = c_2 = \dots = c_n = 0.$$

Linear dependence: A set of functions $\{\phi_1, \phi_2, \dots, \phi_n\}$ are said to be linearly dependent on an interval $I$ if there exist some constants $c_1, c_2, \dots, c_n \in \mathbb{R}$, at least one of the $c_j$ is non zero and

$$\sum_{j=1}^n c_j \phi_j(x) = 0 \quad \forall x \in I.$$

<!-- Page 2 -->
Recall:

Remark: A set of two functions $\{\phi_1(x), \phi_2(x)\}$ are linearly dependent if
(a) at least one of them is a zero function.
(b) or $\phi_1(x) = c \phi_2(x) \quad \forall x \in I.$

Examples of linearly dependent / independent functions:
(1) $\{\sin x, \cos x\}$ in the interval $[0, 2\pi]$.
(2) $\{1, x\}$ in the interval $[0, 1]$.
(3) $\{1, x, x^2\}$ in the interval $[0, 1]$.
(4) $\{\sin x, \cos x, \sin x + 5\cos x\}$ in the interval $[0, 2\pi]$.
(5) $\{1, e^x, e^{2x}\}$ in the interval $(-\infty, \infty)$.
(6) $\{1+2x, 1+x, x\}$ in the interval $(-1, 1)$.
(7) $\{\sin x, \sin^2 x\}$
(8) $\{\sin^2 x, \cos^2 x\}$
(9) $\{\sin^2 x, \cos^2 x, 1\}$
(10) $\{\sin^2 x, \cos^2 x, \cos 2x\}$

Answer: Examples $(4)$, $(6)$, $(9)$ and $(10)$ are linearly dependent. We will see if there is any other method to check the linear independence of collection of functions.

<!-- Page 3 -->
Now, we discuss the linear independence of two solutions of the homogeneous system in $(2)$, using the definition and Wronskian of two solutions.

$$\begin{cases} \frac{dx}{dt} = a_{11}x + a_{12}y \\ \frac{dy}{dt} = a_{21}x + a_{22}y \end{cases} - (2)$$

Linear Dependence and Independence (using definition)

The two solutions $x^{(1)}(t) = (f_1(t), g_1(t))$ and $x^{(2)}(t) = (f_2(t), g_2(t))$ are linearly independent if

$$c_1 x^{(1)}(t) + c_2 x^{(2)}(t) = 0 \implies c_1 = c_2 = 0.$$

On simplification, we obtain
$$c_1(f_1(t), g_1(t)) + c_2(f_2(t), g_2(t)) = (0,0) \quad \forall t \in [a, b].$$
$$\implies c_1 = c_2 = 0$$

That is,
and
$$\begin{cases} c_1 f_1(t) + c_2 f_2(t) = 0 \\ c_1 g_1(t) + c_2 g_2(t) = 0 \end{cases} \quad \forall t \in [a, b].$$
$$\implies c_1 = c_2 = 0.$$

Similarly, we can define, when the two solutions are linearly dependent.

<!-- Page 1 -->
$$\text{Definition: (Wronskian)}$$

Let $x^{(1)}(t) = (x = f_1(t), y = g_1(t))$ and $x^{(2)}(t) = (x = f_2(t), y = g_2(t))$ be two solutions of the homogeneous system in (2):
$$\left.\begin{aligned}
\frac{dx}{dt} &= a_{11}(t)x + a_{12}(t)y \\
\frac{dy}{dt} &= a_{21}(t)x + a_{22}(t)y
\end{aligned}\right\} \text{ (2)}$$

The determinant
$$W[\phi_1, \phi_2](t) = \begin{vmatrix}
f_1(t) & f_2(t) \\
g_1(t) & g_2(t)
\end{vmatrix}$$

is called the Wronskian of these solutions.

$$\underline{\text{Theorem (T10)}}$$ Two solutions 
$$\begin{aligned}
x^{(1)}(t) &= (x = f_1(t), y = g_1(t)) \\
\text{and } x^{(2)}(t) &= (x = f_2(t), y = g_2(t))
\end{aligned}$$
of the homogeneous system in (2)
$$\left.\begin{aligned}
\frac{dx}{dt} &= a_{11}(t)x + a_{12}(t)y \\
\frac{dy}{dt} &= a_{21}(t)x + a_{22}(t)y
\end{aligned}\right\} \text{ (2)}$$
are linearly independent on an interval $[a, b]$ if and only if
$$W(t) = \begin{vmatrix}
f_1(t) & f_2(t) \\
g_1(t) & g_2(t)
\end{vmatrix} \neq 0 \quad \forall t \in [a, b].$$

---

<!-- Page 2 -->
$$\underline{\text{Solution: }(\Leftarrow)}$$ If $W(t) \neq 0$, then the solutions are linearly independent.

Assume $W(t) \neq 0$. Suppose there exist constants $C_1, C_2$ such that
$$C_1 x^{(1)}(t) + C_2 x^{(2)}(t) = 0 \quad \forall t$$

Evaluating this at some '$t_0$', we have
$$\begin{aligned}
C_1 x^{(1)}(t_0) + C_2 x^{(2)}(t_0) &= 0 \\
C_1 \begin{bmatrix} f_1(t_0) \\ g_1(t_0) \end{bmatrix} + C_2 \begin{bmatrix} f_2(t_0) \\ g_2(t_0) \end{bmatrix} &= 0
\end{aligned}$$
$$\Rightarrow \underbrace{\begin{bmatrix}
f_1(t_0) & f_2(t_0) \\
g_1(t_0) & g_2(t_0)
\end{bmatrix}}_{W \neq 0} \begin{bmatrix} C_1 \\ C_2 \end{bmatrix} = 0$$

$\Rightarrow C_1 = C_2 = 0$. Therefore, functions are linearly independent.

$\Rightarrow$ If the solutions are linearly independent, then $W(t) \neq 0$.

We will prove the contrapositive.

---

<!-- Page 3 -->
If $W(t) = 0$, the solutions are linearly dependent.

Consider $W(t_0) = 0$ for some '$t$'
$$\Rightarrow \begin{vmatrix}
f_1(t_0) & f_2(t_0) \\
g_1(t_0) & g_2(t_0)
\end{vmatrix} = 0$$

Then, $C_1 x^{(1)}(t_0) + C_2 x^{(2)}(t_0) = 0$ has a non trivial solution, $C_1$ and $C_2$ not both zero.

Define $z(t) = C_1 x^{(1)}(t) + C_2 x^{(2)}(t)$
$z(t)$ is a solution of (2) (homogeneous ODE)
(Linear combination of solutions)

Also $z(t_0) = 0$. The trivial solution $0(t) = 0$ is also a solution of (2) and satisfies the same initial condition.
By the uniqueness theorem $z(t) \equiv 0 \quad \forall t$

Thus, $C_1 x^{(1)}(t) + C_2 x^{(2)}(t) = 0$ for all $t$, with $C_1, C_2$ not both zero.

$\Rightarrow$ Solutions are linearly dependent.

<!-- Page 1 -->
$$\underline{\text{Example:}}\text{ We have verified that the system}$$
$$\left. \begin{array}{l} \frac{dx}{dt} = 3x + y, \\ \frac{dy}{dt} = 6x + 4y \end{array} \right\} - (*)$$
$$\text{two solutions : } (x = e^{6t}, y = 3e^{6t}) \text{ and } (x = e^t, y = -2e^t).$$
$$\underline{\text{Now,}}$$
$$W(t) = \begin{vmatrix} e^{6t} & e^t \\ 3e^{6t} & -2e^t \end{vmatrix} = -2e^{7t} - 3e^{7t} = -5e^{7t} \neq 0$$
$$\text{on any closed interval } [a,b].$$

$$\text{Thus by Theorem (T10) two solutions are linearly}$$
$$\text{independent on any closed interval } [a,b].$$
$$\underline{\text{(Abble's identity)}}$$
$$\underline{\text{Theorem (T11)}:} \text{ Let } W(t) \text{ be the Wronskian of two}$$
$$\text{solutions of homogeneous linear system}$$
$$\text{in (2) on an interval } [a,b].$$
$$\text{Then, there are only two possibilities:}$$
$$(i) \quad \text{Either } W(t) = 0 \quad \forall t \in [a,b] \quad \text{ie. } W \equiv 0.$$
$$(ii) \quad W(t) \neq 0 \quad \forall t \in [a,b].$$

$$\underline{\text{Solution:}} \text{ let the two solutions of the}$$
$$\text{homogeneous system be}$$
$$x^{(1)} = \begin{pmatrix} f_1 \\ g_1 \end{pmatrix}, \quad x^{(2)} = \begin{pmatrix} f_2 \\ g_2 \end{pmatrix}.$$
$$\text{The Wronskian is defined as}$$

<!-- Page 2 -->
$$W(t) = \begin{vmatrix} f_1 & f_2 \\ g_1 & g_2 \end{vmatrix} = f_1 g_2 - f_2 g_1$$
$$\Rightarrow \frac{dW}{dt} = (f_1' g_2 + f_1 g_2') - (f_2' g_1 + f_2 g_1')$$
$$\text{Substitute the derivative from differ-}$$
$$\text{-ential equations}$$
$$\left. \begin{array}{l} f_1' = \frac{df_1}{dt} = a_{11} f_1 + a_{12} g_1 \\ g_1' = \frac{dg_1}{dt} = a_{21} f_1 + a_{22} g_1 \end{array} \right\} x^{(1)} = \begin{pmatrix} f_1 \\ g_1 \end{pmatrix} \text{ satisfies DE.}$$

$$\left. \begin{array}{l} f_2' = \frac{df_2}{dt} = a_{11} f_2 + a_{12} g_2 \\ g_2' = \frac{dg_2}{dt} = a_{21} f_2 + a_{22} g_2 \end{array} \right\} x^{(2)} = \begin{pmatrix} f_2 \\ g_2 \end{pmatrix} \text{ satisfies DE}$$
$$\text{we have}$$
$$\frac{dW}{dt} = [\overbrace{(a_{11} f_1 + a_{12} g_1)}^{f_1'} g_2 + f_1 \overbrace{(a_{21} f_2 + a_{22} g_2)}^{g_2'}]$$
$$- [\overbrace{(a_{11} f_2 + a_{12} g_2)}^{f_2'} g_1 + f_2 \overbrace{(a_{21} f_1 + a_{22} g_1)}^{g_1'}]$$
$$\text{Expanding and cancelling the cross terms}$$
$$(a_{12} g_1 g_2, \, a_{21} f_1 f_2), \text{ we have}$$

<!-- Page 3 -->
$$\frac{dW}{dt} = a_{11} f_1 g_2 + a_{22} f_1 g_2 - a_{11} f_2 g_1 - a_{22} f_2 g_1$$
$$= a_{11} (f_1 g_2 - f_2 g_1) + a_{22} (f_1 g_2 - f_2 g_1)$$
$$= (a_{11} + a_{22}) (f_1 g_2 - f_2 g_1)$$
$$= (a_{11} + a_{22}) W$$

$$\text{This is a first order differential equati-}$$
$$\text{-on. The solution is}$$
$$W(t) = C \, e^{\int (a_{11} + a_{22}) dt}, \text{ for some}$$
$$\text{constant } C. \text{ Because the exponential}$$
$$\text{term is always strictly positive, it}$$
$$\text{will never vanish.}$$

$$\text{Thus, if } C = 0, \, W(t) \equiv 0 \text{ (identically zero)}$$
$$\text{If } C \neq 0, \, W(t) \text{ is never zero on}$$
$$[a,b].$$

<!-- Page 1 -->
**Result:** If $x^{(1)}(t)$ and $x^{(2)}(t)$ are two solutions of the homogeneous system and their Wronskian is non-zero on $[a,b]$, then every solution $\bar{x}(t)$ can be written as a linear combination of $x^{(1)}(t)$ and $x^{(2)}(t)$, that is

$$\bar{x}(t) = c_1 x^{(1)}(t) + c_2 x^{(2)}(t).$$

**Solution:** Let $\bar{x}(t)$ be any solution and let $t_0 \in [a, b]$.

We want to find constants $c_1$ and $c_2$, such that the linear combination matches $\bar{x}(t)$ at '$t_0$':

$$c_1 x^{(1)}(t_0) + c_2 x^{(2)}(t_0) = \bar{x}(t_0) \quad (* *)$$

This is a system of two algebraic equations for the unknowns $c_1$ and $c_2$.

The determinant of coefficient matrix is $W(t_0)$.

Since $W(t) \neq 0, \forall t \in [a,b]$, then $W(t_0) \neq 0$ $\Rightarrow$ There exists a unique solution $(c_1, c_2)$ to the algebraic system $(* *)$.

---
<!-- Page 2 -->
Now, define a new function

$$\bar{y}(t) = c_1 x^{(1)}(t) + c_2 x^{(2)}(t).$$

$\Rightarrow \bar{y}(t)$ is a solution of (2). Further, by our choice of $c_1, c_2$,

$$\bar{y}(t_0) = \bar{x}(t_0).$$

By the existence and uniqueness theorem for linear system of ODEs, the two solutions share the same initial at $t_0$ must be identical for all $t$.

Thus, $\bar{x}(t) = \bar{y}(t) = c_1 x^{(1)}(t) + c_2 x^{(2)}(t).$

