---
course: "differential equations"
source_file: "MA301 Lecture 8.pdf"
tags: ["math", "coursework", "differential-equations"]
---

# MA301 Lecture 8

<!-- Page 1 -->
**Lecture 8**

**Result:** Let $(x = f_p(t), y = g_p(t))$ be any solution of the nonhomogeneous system
$$\left.\begin{aligned}
\frac{dx}{dt} &= a_{11}(t)x + a_{12}(t)y + F_1(t) \\
\frac{dy}{dt} &= a_{21}(t)x + a_{22}(t)y + F_2(t)
\end{aligned}\right\} -\text{①},$$
and let $(x = f_1(t), y = g_1(t))$ and $(x = f_2(t), y = g_2(t))$ be two linearly independent solutions of the corresponding homogeneous system
$$\left.\begin{aligned}
\frac{dx}{dt} &= a_{11}(t)x + a_{12}(t)y \\
\frac{dy}{dt} &= a_{21}(t)x + a_{22}(t)y
\end{aligned}\right\} -\text{②}$$

Let $C_1$ and $C_2$ be two arbitrary real constants. Then, the solution
$$(x = C_1 f_1(t) + C_2 f_2(t) + f_p(t), \; y = C_1 g_1(t) + C_2 g_2(t) + g_p(t))$$
is called a **general solution** of the nonhomogeneous system in ①.

**Solution:** Let $x^{(1)}(t) = \begin{pmatrix} f_1(t) \\ g_1(t) \end{pmatrix}$, $x^{(2)}(t) = \begin{pmatrix} f_2(t) \\ g_2(t) \end{pmatrix}$, and $x_p(t) = \begin{pmatrix} f_p(t) \\ g_p(t) \end{pmatrix}$.

Consider $y_p(t) = \begin{pmatrix} f_p(t) \\ g_p(t) \end{pmatrix}$ is any solution of nonhomogeneous equation ①.

---

<!-- Page 2 -->
**Show that $y_p(t) - x_p(t)$ is a solution of homogenous equation!**

That is,
$$y_p(t) - x_p(t) = C_1 x^{(1)}(t) + C_2 x^{(2)}(t)$$
$$\Rightarrow y_p(t) = C_1 x^{(1)}(t) + C_2 x^{(2)}(t) + x_p(t).$$

**Result:** Consider the nonhomogeneous system
$$\left.\begin{aligned}
\frac{dx}{dt} &= a_{11}(t)x + a_{12}(t)y + F_1(t) \\
\frac{dy}{dt} &= a_{21}(t)x + a_{22}(t)y + F_2(t)
\end{aligned}\right\} -\text{①}$$

Let $(x = f_p(t), y = g_p(t))$ be any solution of the nonhomogeneous system in ① and let $(x = f(t), y = g(t))$ be any solution of the corresponding homogeneous system
$$\left.\begin{aligned}
\frac{dx}{dt} &= a_{11}(t)x + a_{12}(t)y \\
\frac{dy}{dt} &= a_{21}(t)x + a_{22}(t)y
\end{aligned}\right\} -\text{②}$$

**Conclusion:** Then, $(x = f(t) + f_p(t), \; y = g(t) + g_p(t))$ is also a solution of the nonhomogeneous system in ①.

---

<!-- Page 3 -->
**Solutions to Homogeneous System of Equations**

Consider the linear system of differential equations:
$$\left.\begin{aligned}
\frac{dx}{dt} &= a_{11}x + a_{12}y \\
\frac{dy}{dt} &= a_{21}x + a_{22}y
\end{aligned}\right\} -\text{①}, \quad \begin{aligned} &a_{11}, a_{12}, \\ &a_{21}, a_{22} \\ &\text{are real constants.} \end{aligned}$$

Substitute $x = A e^{mt}$ and $y = B e^{mt}$ in ①, we have
$$m A e^{mt} = a_{11} A e^{mt} + a_{12} B e^{mt}$$
$$m B e^{mt} = a_{21} A e^{mt} + a_{22} B e^{mt} \; ;$$
and dividing by $e^{mt}$ yields the linear algebraic equation in unknowns $A$ and $B$:
$$\left.\begin{aligned}
m A &= a_{11} A + a_{12} B \\
m B &= a_{21} A + a_{22} B
\end{aligned}\right\} \Rightarrow \left\{\begin{aligned}
(a_{11} - m) A + a_{12} B &= 0 \\
a_{21} A + (a_{22} - m) B &= 0
\end{aligned}\right\}, -\text{③}$$

Note that, ③ has a trivial solution $A = B = 0$, which gives trivial solution $x = 0, y = 0$. (see ②)

Now, the system in ③ can be written as
$$\begin{bmatrix} a_{11} - m & a_{12} \\ a_{21} & a_{22} - m \end{bmatrix} \begin{bmatrix} A \\ B \end{bmatrix} = \begin{bmatrix} 0 \\ 0 \end{bmatrix}.$$

<!-- Page 1 -->
So, for a non-trivial solution, we must have
$$\begin{vmatrix} a_{11}-m & a_{12} \\ a_{21} & a_{22}-m \end{vmatrix} = 0$$
$$\underbrace{\text{det of coefficient}}_{\text{matrix}}\neq 0$$

When we expand this determinant, we get the following quadratic equation
$$m^2 - (a_{11}+a_{22})m + (a_{11}a_{22} - a_{12}a_{21}) = 0, \quad -\text{4}$$
for unknown '$m$'.

This equation is called the auxiliary or characteristic equation of the system $\text{①}$.

Let $m_1$ and $m_2$ be the roots of $\text{④}$.
If we replace '$m$' in $\text{③}$ by $m_1$, then we will have non-trivial solution $A_1, B_1$.

So $\quad x = A_1 e^{m_1 t}, \quad y = B_1 e^{m_1 t} \quad -\text{⑤}$
That is $\quad x^{(1)} = \begin{bmatrix} A_1 \\ B_1 \end{bmatrix} e^{m_1 t}$ is a non-trivial solution of $\text{①}$.

Similarly, for $m=m_2$, we have another non-trivial solution $\quad x^{(2)} = \begin{bmatrix} A_2 \\ B_2 \end{bmatrix} e^{m_2 t}$.

<!-- Page 2 -->
Summary:

Consider the following homogeneous linear system:
$$\frac{dx}{dt} = a_{11}x + a_{12}y, \quad \frac{dy}{dt} = a_{21}x + a_{22}y,$$
where $a_{11}, a_{12}, a_{21}, a_{22}$ are real constants.

Definition: Characteristic equation associated with homogeneous linear system with constant coefficients

Let $M = \begin{bmatrix} a_{11} & a_{12} \\ a_{21} & a_{22} \end{bmatrix}$, the coefficient matrix.

The equation
$$\det(M - \lambda I_2) = 0, \quad \text{i.e.} \quad \begin{vmatrix} a_{11}-\lambda & a_{12} \\ a_{21} & a_{22}-\lambda \end{vmatrix} = 0$$
$$\Rightarrow \lambda^2 - \text{tr}(M)\lambda + \det(M) = 0$$

i.e. $\quad \lambda^2 - (a_{11}+a_{22})\lambda + (a_{11}a_{22} - a_{12}a_{21}) = 0$
is called the characteristic equation associated with given system.

<!-- Page 3 -->
Now, we will discuss the solution of the homogeneous system of ODEs by the roots of the associated characteristic equation:
$$\lambda^2 - (a_{11}+a_{12})\lambda + (a_{11}a_{22} - a_{12}a_{21}) = 0.$$

<u>Case 1:</u> The roots $\lambda_1$ and $\lambda_2$ of the associated characteristic equation in (1) are real and distinct.

Then, the given system has two nontrivial solutions of the form
$$\overbrace{(x = A_1 e^{\lambda_1 t}, \, y = B_1 e^{\lambda_1 t})}^{x^{(1)}(t)} \text{ and } \overbrace{(x = A_2 e^{\lambda_2 t}, \, y = B_2 e^{\lambda_2 t})}^{x^{(2)}(t)},$$
where $A_1, A_2, B_1$ and $B_2$ are definite constants.

$$\left\{ x^{(1)} = \begin{pmatrix} x \\ y \end{pmatrix} = \begin{pmatrix} A_1 \\ B_1 \end{pmatrix} e^{\lambda_1 t}, \quad x^{(2)} = \begin{pmatrix} A_2 \\ B_2 \end{pmatrix} e^{\lambda_2 t} \right\}$$

<!-- Page 1 -->
Example: Find the general solution of each of the linear system in the following:

(i) $\frac{dx}{dt} = 5x - 2y$, $\quad \frac{dy}{dt} = 4x - y$

Here $M = \begin{bmatrix} 5 & -2 \\ 4 & -1 \end{bmatrix}$

The associated characteristic equation
$\det(M - \lambda I_2) = \begin{vmatrix} 5 - \lambda & -2 \\ 4 & -1 - \lambda \end{vmatrix} = 0$

$\Rightarrow \lambda^2 - 4\lambda + 3 = 0$

$\Rightarrow (\lambda - 3)(\lambda - 1) = 0$, $\quad \lambda_1 = 3$, $\lambda_2 = 1$

Now, $(x = A_1 e^{\lambda_1 t}, \quad y = B_1 e^{\lambda_1 t})$ and
$(x = A_2 e^{\lambda_2 t}, \quad y = B_2 e^{\lambda_2 t})$ are two nontrivial linearly independent solutions.

First, we find $A_1, B_1, A_2, B_2$. For that we put the solution $(x = A_1 e^{\lambda_1 t}, \quad y = B_1 e^{\lambda_1 t})$

in the given system
$\frac{dx}{dt} = 5x - 2y$, $\quad \frac{dy}{dt} = 4x - y$.

<!-- Page 2 -->
$\begin{cases}
\text{LHS}: \frac{dx}{dt} = \frac{d}{dt}(A_1 e^{3t}) = 3A_1 e^{3t} \\
\text{RHS}: \frac{dx}{dt} = 5x - 2y = 5(A_1 e^{3t}) - 2B_1(e^{3t}) \\
\quad\quad\quad = (5A_1 - 2B_1)e^{3t}
\end{cases}$

$\text{LHS} = \text{RHS} \Rightarrow 3A_1 e^{3t} = (5A_1 - 2B_1) e^{3t}$

$\Rightarrow 2A_1 - 2B_1 = 0 \quad \text{--- } \textcircled{1}$

$\begin{cases}
\text{LHS}: \frac{dy}{dt} = \frac{d}{dt}(B_1 e^{3t}) = 3B_1 e^{3t} \\
\text{RHS}: 4x - y = 4(A_1 e^{3t}) - B_1 e^{3t} \\
\quad\quad\quad = (4A_1 - B_1)e^{3t} \\
\text{So}, \quad 3B_1 e^{3t} = (4A_1 - B_1)e^{3t} \\
\Rightarrow A_1 - B_1 = 0 \quad \text{--- } \textcircled{2}
\end{cases}$

Thus, both eqns $\textcircled{1}$ and $\textcircled{2}$ give $A_1 = B_1$.

Choose $A_1 = B_1 = 1$, So $\left(x = e^{3t}, \, y = e^{3t}\right)$ for $\lambda_1 = 3$ eigenvalue.

Now, we put the second solution $(x = A_2 e^t, \, y = B_2 e^t)$ in the given system
$\frac{dx}{dt} = 5x - 2y$, $\quad \frac{dy}{dt} = 4x - y$.

$A_2 e^t = 5A_2 e^t - 2B_2 e^t$, $\quad B_2 e^t = 4A_2 e^t - B_2 e^t$
$$\Downarrow \quad \Downarrow$$

<!-- Page 3 -->
$4A_2 - 2B_2 = 0$, $\quad 4A_2 - 2B_2 = 0$

Both eqns are same ($2A_2 = B_2$)
Choose $A_2 = 1 \Rightarrow B_2 = 2$.

So, $(x = e^t, \quad y = 2e^t)$.

The two solutions are $\nearrow \text{Check Wronskian!}$
$(x = e^{3t}, \, y = e^{3t})$ and $(x = e^t, \, y = 2e^t)$.

Now, the general solution is given by
$(x = C_1 e^{3t} + C_2 e^t, \quad C_1 e^{3t} + 2C_2 e^t)$,

where $C_1$ and $C_2$ are arbitrary constants.

Observe that,
$\begin{bmatrix} a_{11} - \lambda & a_{12} \\ a_{21} & a_{22} - \lambda \end{bmatrix} \begin{bmatrix} A \\ B \end{bmatrix} = \begin{bmatrix} 0 \\ 0 \end{bmatrix}$

$\underbrace{(M - \lambda I)v}_{\uparrow} = 0 \longrightarrow \text{eigenvector}$
$\text{eigenvalue}$

<!-- Page 1 -->
**Remark:**

Now, observe the following for the above example where

$$M = \begin{bmatrix} 5 & -2 \\ 4 & -1 \end{bmatrix} \text{ and eigenvalues are } \lambda_1 = 3, \lambda_2 = 1.$$

The eigenspaces for these eigenvalues can be obtained as follows:

Associated to $\lambda = 3$:
$$E_{\lambda_1} = E_3 = \{v \in \mathbb{R}^2 : Mv = 3v\}.$$

Say, $v = \begin{bmatrix} v_1 \\ v_2 \end{bmatrix} \in \mathbb{R}^2$, such that $Mv = 3v$.

$$\Rightarrow \begin{bmatrix} 5 & -2 \\ 4 & -1 \end{bmatrix} \begin{bmatrix} v_1 \\ v_2 \end{bmatrix} = 3 \begin{bmatrix} v_1 \\ v_2 \end{bmatrix}$$

$$\left. \begin{array}{l} 5v_1 - 2v_2 = 3v_1 \\ 4v_1 - v_2 = 3v_2 \end{array} \right\} \Rightarrow \left. \begin{array}{l} 2v_1 - 2v_2 = 0 \\ v_1 - v_2 = 0 \end{array} \right\} \Rightarrow v_1 = v_2$$

So, $E_3 = \left\{v \in \begin{bmatrix} v_1 \\ v_1 \end{bmatrix} : v_1 \in \mathbb{R}\right\}$ is the eigenspace

(for the eigenvalue $\lambda_1 = 3$), and any nonzero vector in $E_3$ is an eigenvector for the matrix $M$ corresponding to eigenvalue $\lambda_1 = 3$.

For example, $v = \begin{bmatrix} 1 \\ 1 \end{bmatrix}$ is an eigenvector.

<!-- Page 2 -->
Observe that
$$x^{(1)} = \begin{bmatrix} x \\ y \end{bmatrix} = v e^{\lambda_1 t} = \begin{bmatrix} 1 \\ 1 \end{bmatrix} e^{3t} = \begin{bmatrix} e^{3t} \\ e^{3t} \end{bmatrix}$$ is a solution of the given system.

Similarly, let's find the eigenspace for $M$ corresponding to the eigenvalue $\lambda_2 = 1$.
i.e., $E_{\lambda_2} = E_1 = \{w \in \mathbb{R}^2 : Mw = \lambda_2 w\}$
$= \{w \in \mathbb{R}^2 : Mw = w\}$

Now $Mw = w \Rightarrow \begin{bmatrix} 5 & -2 \\ 4 & -1 \end{bmatrix} \begin{bmatrix} w_1 \\ w_2 \end{bmatrix} = \begin{bmatrix} w_1 \\ w_2 \end{bmatrix} \Rightarrow \begin{array}{l} 5w_1 - 2w_2 = w_1 \\ 4w_1 - w_2 = w_2 \end{array}$

$$\Rightarrow 4w_1 - 2w_2 = 0$$
$$\Rightarrow 2w_1 = w_2$$

i.e., $E_1 = \left\{\begin{bmatrix} w_1 \\ 2w_1 \end{bmatrix} : w_1 \in \mathbb{R}\right\}$.

Any nonzero vector is an eigenvector for $M$ (for $\lambda_2 = 1$), for example, $w = \begin{bmatrix} 1 \\ 2 \end{bmatrix}$ is an eigenvector.

Then,
$$x^{(2)} = \begin{bmatrix} x \\ y \end{bmatrix} = w e^{\lambda_2 t} = \begin{bmatrix} 1 \\ 2 \end{bmatrix} e^t = \begin{bmatrix} e^t \\ 2e^t \end{bmatrix}$$ is a solution.

<!-- Page 3 -->
Also, $v e^{\lambda_1 t}$ and $w e^{\lambda_2 t}$ are two linearly independent solutions
$$\begin{vmatrix} e^{3t} & e^t \\ e^{3t} & 2e^t \end{vmatrix} = 2e^{4t} - e^{4t} = e^{4t} \neq 0 \quad \forall t$$
Wronskian

The general solution is of the form
$(x, y) = c_1 v e^{3t} + c_2 w e^t$
$$\begin{bmatrix} x \\ y \end{bmatrix} = c_1 \begin{bmatrix} 1 \\ 1 \end{bmatrix} e^{3t} + c_2 \begin{bmatrix} 1 \\ 2 \end{bmatrix} e^t$$
$$= \begin{bmatrix} c_1 e^{3t} + c_2 e^t \\ c_1 e^{3t} + 2c_2 e^t \end{bmatrix}$$

$\Rightarrow (x = c_1 e^{3t} + c_2 e^t, \ y = c_1 e^{3t} + 2c_2 e^t)$ is the general solution.

<!-- Page 1 -->
Example: Consider the homogeneous system
$$\frac{dx}{dt} = 6x-3y, \quad \frac{dy}{dt} = 2x+y.$$

Find the general solution for it.

Solution: Here $M = \begin{bmatrix} 6 & -3 \\ 2 & 1 \end{bmatrix}$.

The associated characteristic equation:
$$\det(M-\lambda I_2) = 0$$
$$\lambda^2 - 7\lambda + 12 = 0$$
$$(\lambda-4)(\lambda-3) = 0 \implies \lambda_1 = 4, \; \lambda_2 = 3.$$
(Roots are real and distinct).

Let us find eigenvectors corresponding to the eigen-values $\lambda_1=4, \; \lambda_2=3$.
So, we need to find nonzero vectors $v_1 \ \& \ v_2$ such that,

$$M v_1 = \lambda_1 v_1, \quad M v_2 = \lambda_2 v_2$$

$$\begin{bmatrix} 6 & -3 \\ 2 & 1 \end{bmatrix} \begin{bmatrix} v_{11} \\ v_{21} \end{bmatrix} = 4 \begin{bmatrix} v_{11} \\ v_{21} \end{bmatrix}, \quad \begin{bmatrix} 6 & -3 \\ 2 & 1 \end{bmatrix} \begin{bmatrix} v_{12} \\ v_{22} \end{bmatrix} = 3 \begin{bmatrix} v_{12} \\ v_{22} \end{bmatrix}$$

$$
\begin{aligned}
6v_{11} - 3v_{21} &= 4v_{11} \\
2v_{11} + v_{21} &= 4v_{21}
\end{aligned}
\quad , \quad
\begin{aligned}
6v_{12} - 3v_{22} &= 3v_{12} \\
2v_{12} + v_{22} &= 3v_{22}
\end{aligned}
$$

<!-- Page 2 -->
$$
\begin{aligned}
2v_{11} - 3v_{21} &= 0 \\
2v_{11} - 3v_{21} &= 0
\end{aligned}
\quad , \quad
\begin{aligned}
v_{12} - v_{22} &= 0 \\
v_{12} - v_{22} &= 0
\end{aligned}
$$

$$\begin{bmatrix} v_{11} \\ v_{21} \end{bmatrix} = \begin{bmatrix} v_{11} \\ \frac{2}{3}v_{11} \end{bmatrix}, \quad \begin{bmatrix} v_{12} \\ v_{22} \end{bmatrix} = \begin{bmatrix} v_{12} \\ v_{12} \end{bmatrix}.$$

Choose $v_{11} = 3$, then the eigenvector $v_1 = \begin{bmatrix} 3 \\ 2 \end{bmatrix}$

Choose $v_{12} = 1$, then the eigenvector $v_2 = \begin{bmatrix} 1 \\ 1 \end{bmatrix}$.

$\{v_1 e^{\lambda_1 t}, \; v_2 e^{\lambda_2 t}\}$ is a linearly independent solution set for the given homogeneous system.
And
$$\begin{pmatrix} x \\ y \end{pmatrix} = c_1 v_1 e^{\lambda_1 t} + c_2 v_2 e^{\lambda_2 t}$$
$$\begin{pmatrix} x \\ y \end{pmatrix} = c_1 \begin{bmatrix} 3 \\ 2 \end{bmatrix} e^{4t} + c_2 \begin{bmatrix} 1 \\ 1 \end{bmatrix} e^{3t}, \text{ where } c_1 \text{ and } c_2 \text{ are arbitrary constants, is a general solution for a given homogeneous system on any interval } [a, b].$$

In other words,
$(x = 3c_1 e^{4t} + c_2 e^{3t}, \; y = 2c_1 e^{4t} + c_2 e^{3t})$ is a general solution on any interval $[a, b]$.

<!-- Page 3 -->
Result: Consider the homogeneous linear systems with constant coefficients:
Two equations in Two unknown functions
$$\frac{dx}{dt} = a_{11}x + a_{12}y$$
$$\frac{dy}{dt} = a_{21}x + a_{22}y$$

If the roots of the associated characteristic equation

$$\lambda^2 - (a_{11}+a_{22})\lambda + (a_{11}a_{22}-a_{12}a_{21}) = 0$$
has two distinct real roots $\lambda_1 \ \& \ \lambda_2$, and $v_1 \ \& \ v_2$ are eigenvectors of $M = \begin{bmatrix} a_{11} & a_{12} \\ a_{21} & a_{22} \end{bmatrix}$ corresponding to $\lambda_1 \ \& \ \lambda_2$, respectively, then
$$\left\{\begin{matrix} M v_1 = \lambda_1 v_1 \\ M v_2 = \lambda_2 v_2 \end{matrix}\right\}$$

$(i)$ two vector valued functions (domain is any interval $[a, b]$) $v_1 e^{\lambda_1 t}$ and $v_2 e^{\lambda_2 t}$ forms a linearly independent (over the field $\mathbb{R}$) set on on any interval $[a, b]$.

$(ii)$ $v_1 e^{\lambda_1 t} \ \& \ v_2 e^{\lambda_2 t}$ both are solutions for the given system.

<!-- Page 1 -->
(iii) Thus, by Part (i) & Part (ii), the general solution is given by
$$c_1 v_1 e^{\lambda_1 t} + c_2 v_2 e^{\lambda_2 t} \quad \text{on any interval } [a, b]$$

Proof (i): First, we prove that the set $\{v_1, v_2\}$ is a L.I. set.
Let $\alpha, \beta \in \mathbb{R}$ such that
$$\alpha v_1 + \beta v_2 = 0 \quad - (1)$$
$$M(\alpha v_1 + \beta v_2) = 0$$
$$\alpha \lambda_1 v_1 + \beta \lambda_2 v_2 = 0 \quad - (2)$$
*(if $\lambda_1 = 0$, then $(1) \times \lambda_2 \dots$)*

$$(1) \times \lambda_1 \Rightarrow \alpha \lambda_1 v_1 + \beta \lambda_1 v_2 = 0 \quad - (3)$$
From $(2) - (3)$, we have
$$\beta(\lambda_2 - \lambda_1) v_2 = 0, \quad v_2 \neq 0 \text{ (as eigenvector)}, \lambda_1 \neq \lambda_2$$
$$\Rightarrow \beta = 0$$
From $(1) \Rightarrow \alpha v_1 = 0 \Rightarrow \alpha = 0 \quad (v_1 \neq 0 \text{ as eigenvector})$
So, $\{v_1, v_2\}$ is L.I.

<!-- Page 2 -->
Now, assume for $r, s \in \mathbb{R}$ st
$$r v_1 e^{\lambda_1 t} + s v_2 e^{\lambda_2 t} = 0, \quad \forall t \in [a, b]. - (4)$$

Let $t_0 \in [a, b]$. Then, put $t = t_0$ in equation to obtain
$$r e^{\lambda_1 t_0} v_1 + s e^{\lambda_2 t_0} v_2 = 0. \quad - (5)$$
Since $\{v_1, v_2\}$ is L.I.,
$$r e^{\lambda_1 t_0} = s e^{\lambda_2 t_0} = 0 \Rightarrow r = s = 0$$
(as $e^{\lambda_1 t_0} \neq 0$ and $e^{\lambda_2 t_0} \neq 0$)

So, $\{v_1 e^{\lambda_1 t}, v_2 e^{\lambda_2 t}\}$ is L.I. set over any interval $[a, b]$.

Proof (ii): Say, $v_1 = \begin{bmatrix} v_{11} \\ v_{21} \end{bmatrix}, v_2 = \begin{bmatrix} v_{12} \\ v_{22} \end{bmatrix}$.

We need to prove that
$$\begin{pmatrix} x \\ y \end{pmatrix} = v_1 e^{\lambda_1 t} = \begin{bmatrix} v_{11} e^{\lambda_1 t} \\ v_{21} e^{\lambda_1 t} \end{bmatrix}$$
i.e., $(x = v_{11} e^{\lambda_1 t}, y = v_{21} e^{\lambda_1 t})$ is a solution of the given system.
$$\frac{dx}{dt} = \lambda_1 v_{11} e^{\lambda_1 t}, \quad \frac{dy}{dt} = \lambda_1 v_{21} e^{\lambda_1 t} \quad - (1)$$
$$a_{11} x + a_{12} y = a_{11} v_{11} e^{\lambda_1 t} + a_{12} v_{21} e^{\lambda_1 t}$$
$$a_{21} x + a_{22} y = a_{21} v_{11} e^{\lambda_1 t} + a_{22} v_{21} e^{\lambda_1 t} \quad - (2)$$

Since $Mv_1 = \lambda_1 v_1$, i.e.,
$$\begin{bmatrix} a_{11} & a_{12} \\ a_{21} & a_{22} \end{bmatrix} \begin{bmatrix} v_{11} \\ v_{21} \end{bmatrix} = \lambda_1 \begin{bmatrix} v_{11} \\ v_{21} \end{bmatrix}, \text{ we have}$$

<!-- Page 3 -->
$$a_{11} v_{11} + a_{12} v_{21} = \lambda_1 v_{11} \quad - (3)$$
$$a_{21} v_{11} + a_{22} v_{21} = \lambda_1 v_{21} \quad - (4)$$

Thus, by $(1), (2), (3)$ and $(4)$, we have
$$\frac{dx}{dt} = \lambda_1 v_{11} e^{\lambda_1 t} = a_{11} \underbrace{v_{11} e^{\lambda_1 t}}_{x} + a_{12} \underbrace{v_{21} e^{\lambda_1 t}}_{y}$$
$$\frac{dy}{dt} = \lambda_1 v_{21} e^{\lambda_1 t} = a_{21} \underbrace{v_{11} e^{\lambda_1 t}}_{x} + a_{22} \underbrace{v_{21} e^{\lambda_1 t}}_{y}$$
Similarly, prove $v_2 e^{\lambda_2 t}$ is a solution.

Hence, $x = v_{11} e^{\lambda_1 t}, y = v_{21} e^{\lambda_1 t}$ is a solution for the given system.

Proof (iii) Thus, the general solution is given by
$$c_1 v_1 e^{\lambda_1 t} + c_2 v_2 e^{\lambda_2 t}$$
on any interval $[a, b]$.

