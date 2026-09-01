---
course: "differential equations"
source_file: "MA301 Lecture 6 notes.pdf"
tags: ["math", "coursework", "differential-equations"]
---

# MA301 Lecture 6 notes

<!-- Page 1 -->

## Lecture 6

Refer to Lecture 5 notes for other three cases!

### Case 4: Finite sums and products of these functions:

**Example:** Find a particular solution of
$$y'' - 3y' - 4y = -8 e^t \cos 2t.$$

**Solution:** We will search for a solution of the form
$$y(t) = a e^t \cos 2t + b e^t \sin 2t.$$

Then,
$$y'(t) = (a + 2b) e^t \cos 2t + (-2a + b) e^t \sin 2t.$$
and
$$y''(t) = (-3a + 4b) e^t \cos 2t + (-4a - 3b) e^t \sin 2t.$$
Substituting, we get
$$-10a - 2b = -8, \quad 2a - 10b = 0 \implies a = \frac{10}{13}, b = \frac{2}{13}.$$

Therefore, a particular solution is
$$y(t) = \frac{10}{13} e^t \cos 2t + \frac{2}{13} e^t \sin 2t.$$

**Result:** Let $\Psi_1$ and $\Psi_2$ are particular solutions of $y'' + py' + qy = r_1(x)$ and $y'' + py' + qy = r_2(x)$, respectively. Then $y_p = \Psi_1 + \Psi_2$ is a particular solution of $y'' + py' + qy = r_1(x) + r_2(x)$.

<!-- Page 2 -->

**Example:** $y'' - y' = e^{2x} + x$

**Solution:** Using the above result, we first find two functions $\Psi_1$ and $\Psi_2$.

For $y'' - y' = e^{2x}$, it can be verified that $\Psi_1(x) = e^{2x}$ is a particular solution.

Now, for $y'' - y' = x$, we may look for a solution of the form $Ax + B$. But, since any constant $B$ itself is a solution of $y'' - y' = 0$, we don't obtain anything.

Hence, we look for $\Psi_2 = Ax^2 + Bx$ and obtain
$$A = -\frac{1}{2} \quad \text{and} \quad B = -1.$$

So, a particular solution of $y'' - y' = e^{2x} + x$ is
$$y_p(x) = \Psi_1 + \Psi_2,$$
$$y_p(x) = e^{2x} - x - \frac{x^2}{2}$$

<!-- Page 3 -->

**Remark:** If $r(t) = r_1(t) + \dots + r_n(t)$, where $r_i(t)$ are $e^{at}$ or $\sin at$ or $\cos at$ or polynomials in $t$, consider the $n$ subproblems
$$y'' + py' + qy = r_i(t) \quad - (eq1)$$

If $y_i(t)$ is a particular solution of $(eq1)$, then
$$y(t) = y_1(t) + y_2(t) + \dots + y_n(t)$$
is a particular solution of
$$y'' + py' + qy = r(t).$$

### Form of particular solution

1) $r(x) = p_n(x) = a_n x^n + \dots + a_1 x + a_0$,
$$y_p(x) = x^s P_n(x) = x^s \{ A_n x^n + \dots + A_1 x + A_0 \}$$

2) $r(x) = a e^{\alpha x}, \quad y_p(x) = x^s A e^{\alpha x}$

3) $r(x) = a \cos \beta x + b \sin \beta x$,
$$y_p(x) = x^s \{ A \cos \beta x + B \sin \beta x \}$$

4) $r(x) = p_n(x) e^{\alpha x}, \quad y_p(x) = x^s P_n(x) e^{\alpha x}$

5) $r(x) = p_n(x) \cos \beta x \quad (\text{or } p_n(x) \sin \beta x)$
$$y_p(x) = x^s \{ P_n(x) \cos \beta x + P_n(x) \sin \beta x \}$$

<!-- Page 1 -->

6) $r(x) = a e^{\alpha x} \cos\beta x \quad (\text{or } b e^{\alpha x} \sin\beta x)$
   $$y_p(x) = x^s \{ A e^{\alpha x} \cos\beta x + B e^{\alpha x} \sin\beta x \}$$

7) $r(x) = P_n(x) e^{\alpha x} \cos\beta x \quad (\text{or } P_n(x) e^{\alpha x} \sin\beta x)$
   $$y_p(x) = x^s e^{\alpha x} \{ P_n(x) \cos\beta x + P_n(x) \sin\beta x \}$$

**Remarks:**

(a) The nonnegative integer '$s$' is chosen to be the smallest integer so that no term in $y_p$ is a solution to $L(y) = 0$.

(b) $P_n(x)$ must include all the terms even if $P_n(x)$ has some terms that are zero.

### Examples for higher order linear homogeneous ordinary equations :

Find the general solution for
$$y^{(4)} - 8y'' - 16y = 0$$

**Solution:** As before substitute $y = e^{mx}$ and we obtain the characteristic equation
$$m^4 - 8m^2 + 16 = 0.$$

<!-- Page 2 -->

On solving, we obtain $m_1 = m_2 = 2$ and $m_3 = m_4 = -2$

The general solution is
$$y(x) = (c_1 + c_2 x) e^{2x} + (c_3 + c_4 x) e^{-2x}$$

<!-- Page 3 -->

**Remark:** Consider the ODE:
$$\frac{d^2y}{dt^2} + p(t) \frac{dy}{dt} + q(t) y = 0$$

We can write
$$\frac{d^2y}{dt^2} = -p(t) \frac{dy}{dt} - q(t) y$$

$$\text{Set } y = x_1, \quad \frac{dy}{dt} = x_2 = \frac{dx_1}{dt}$$

So,
$$\begin{cases} \frac{dx_2}{dt} = \frac{d^2y}{dt^2} = -q(t) x_1 - p(t) x_2 \\ \frac{dx_1}{dt} = x_2 = 0 \cdot x_1 + 1 \cdot x_2 \end{cases}$$

$$\begin{cases} \frac{dx_1}{dt} = x_2 \\ \frac{dx_2}{dt} = -p(t) x_2 - q(t) x_1 \end{cases} \quad \text{system of first order ODEs}$$

$$\begin{bmatrix} \dot{x}_1 \\ \dot{x}_2 \end{bmatrix} = \begin{bmatrix} \frac{dx_1}{dt} \\ \frac{dx_2}{dt} \end{bmatrix} = \begin{bmatrix} 0 & 1 \\ -q(t) & -p(t) \end{bmatrix} \begin{bmatrix} x_1 \\ x_2 \end{bmatrix}, \quad \begin{cases} x_1 = y \\ x_2 = \frac{dy}{dt} \end{cases}$$

<!-- Page 1 -->

### Exercise:

1) $$y'' - t^2 y' - ty = 0$$

$$x_1 = y, \qquad x_2 = \frac{dy}{dt} = \frac{dx_1}{dt}$$

$$\frac{dx_2}{dt} = \frac{d^2 y}{dt^2} = y'' = t^2 y' + ty = t^2 x_2 + t x_1$$

$$\begin{cases} \frac{dx_1}{dt} = x_2 \\ \frac{dx_2}{dt} = t x_1 + t^2 x_2 \end{cases} \Rightarrow \begin{bmatrix} \frac{dx_1}{dt} \\ \frac{dx_2}{dt} \end{bmatrix} = \begin{bmatrix} 0 & 1 \\ t & t^2 \end{bmatrix} \begin{bmatrix} x_1 \\ x_2 \end{bmatrix}.$$

2) $$y''' = y'' - t^2 (y')^2$$

$$x_1 = y, \qquad x_2 = \frac{dy}{dt}, \qquad x_3 = \frac{d^2 y}{dt^2}$$

$$\frac{dx_3}{dt} = x_3 - t^2 (x_2)^2$$

$$\begin{cases} \dot{x}_1 = \frac{dx_1}{dt} = x_2 \\ \dot{x}_2 = \frac{dx_2}{dt} = x_3 \\ \dot{x}_3 = \frac{dx_3}{dt} = -t^2 (x_2)^2 + x_3 \end{cases}$$

---

<!-- Page 2 -->

### 1.1. System of two linear differential equations in two unknown functions:

Consider the following system of differential equations:

$$\begin{cases} \frac{dx}{dt} = a_{11}(t) x + a_{12}(t) y + F_1(t) \\ \frac{dy}{dt} = a_{21}(t) x + a_{22}(t) y + F_2(t) \end{cases} \qquad \text{--- } ①$$

Here, we assume that the functions $a_{11}, a_{12}, a_{21}, a_{22}, F_1, F_2$ are all continuous on an interval $[a, b] \ (a < b)$.

If $F_1(t) = F_2(t) = 0, \quad \forall t \in [a, b]$, then the system in $(1)$ is called **homogeneous**; otherwise **nonhomogeneous**.

**Remark:** The above form is called **normal form** in the case of two linear differential equations in two unknowns.

#### Example 1.2:
The system
$$\frac{dx}{dt} = 3x - y, \qquad \frac{dy}{dt} = 5x + 3y$$
is homogeneous; and

$$\frac{dx}{dt} = 3x - y + 6t, \qquad \frac{dy}{dt} = 5x + 3y + 3$$
is nonhomogeneous.

---

<!-- Page 3 -->

### Definition 1.3. (Solution of the system in (1)):

By a **solution** of the system in $(1)$, we mean there exist a pair $(f, g)$ of continuously differentiable functions
$$f : [a, b] \to \mathbb{R} \quad \text{and} \quad g : [a, b] \to \mathbb{R}$$
(i.e., $f$ and $g$ are differentiable and their derivatives $f' : [a, b] \to \mathbb{R}$, $g' : [a, b] \to \mathbb{R}$ are also continuous) such that
$$f'(t) = \frac{df(t)}{dt} = a_{11}(t) f(t) + a_{12}(t) g(t) + F_1(t)$$
$$g'(t) = \frac{dg(t)}{dt} = a_{21}(t) f(t) + a_{22}(t) g(t) + F_2(t)$$
$$\forall t \in [a, b].$$

#### Example 1.4:
Consider the system
$$\frac{dx}{dt} = 3x + y, \qquad \frac{dy}{dt} = 6x + 4y.$$

Verify that
1. $(x = e^{6t}, \ y = 3e^{6t})$ is a solution pair of the given system.
2. $(x = e^t, \ y = -2e^t)$ is a solution pair of the given system.

<!-- Page 1 -->
$$\text{Solution:}$$
$$(1) \quad x = e^{6t} , \quad \frac{dx}{dt} = 6e^{6t}$$
$$y = 3e^{6t} , \quad \frac{dy}{dt} = 3 \times 6e^{6t} = 18e^{6t}$$

$$3x + y = 3e^{6t} + 3e^{6t} = 6e^{6t} = \frac{dx}{dt} \quad - (*)$$
$$6x + 4y = 6e^{6t} + 4 \times 3e^{6t} = 18e^{6t} = \frac{dy}{dt} \quad - (**)$$

$$\text{From } (*) \text{ and } (**)$$

$$\begin{cases}
\frac{dx}{dt} = 6e^{6t} = 3x + y \\
\frac{dy}{dt} = 18e^{6t} = 6x + 4y
\end{cases}$$

$$\text{Therefore, the solution pair } (1) \text{ satisfies}$$
$$\text{the given system.}$$

$$\text{Similarly, check for } (2).$$

<!-- Page 2 -->
$$\text{Now, we state the basic existence theorem}$$
$$\text{for the system (1).}$$
$$\underline{\text{Theorem 1.5}} : \mathbf{(\text{Hypothesis})}$$
$$\text{Consider the system of the form}$$
$$\left. \begin{aligned}
\frac{dx}{dt} &= a_{11}(t) x + a_{12}(t) y + F_1(t) \\
\frac{dy}{dt} &= a_{21}(t) x + a_{22}(t) y + F_2(t)
\end{aligned} \right\} - ①$$
$$\text{where the functions } a_{11}, a_{12}, a_{21}, a_{22}, F_1, F_2$$
$$\text{are all continuous on the interval } [a,b] \, (a<b).$$
$$\text{Let } t_0 \in [a,b], \text{ and let } c_1 \text{ and } c_2 \text{ be two}$$
$$\text{arbitrary constants.}$$

$$\underline{\text{Conclusion}} : \text{There exists a unique solution}$$
$$\text{( } x = f(t), \, y=g(t) \text{) of the system in}$$
$$\text{(1) on the interval } [a,b] \text{ such that}$$
$$f(t_0) = c_1 , \quad g(t_0) = c_2 .$$

$$\underline{\text{Result}} : \text{Consider the following homogeneous system of}$$
$$\text{differential equations}$$
$$\left. \begin{aligned}
\frac{dx}{dt} &= a_{11}(t) x + a_{12}(t) y \\
\frac{dy}{dt} &= a_{21}(t) x + a_{22}(t) y
\end{aligned} \right\} - ②$$

<!-- Page 3 -->
$$\text{Let } t_0 \text{ be any point of } a \le t \le b \text{ and}$$
$$\text{let } (x(t), y(t)) \text{ be a solution of } ② \text{ such}$$
$$\text{that } x(t_0) = 0, y(t_0) = 0 . \text{ Then, } x(t) = 0, y(t) = 0$$
$$\text{for all } a \le t \le b .$$

$$\text{Solution:} \text{ Using Theorem 1.5, there exists}$$
$$\text{a unique solution satisfying the initial}$$
$$\text{condition } x(t_0) = 0 \text{ and } y(t_0) = 0 .$$

$$\text{Let } (x(t), y(t)) \text{ be a solution to } ② \text{ with}$$
$$\text{with } x(t_0) = 0, \, y(t_0) = 0 .$$

$$(x(t), y(t)) \equiv 0 , \, \forall \, t \in [a,b] \text{ also satisfies}$$
$$② \text{ along with initial conditions.}$$

$$\text{By using Theorem 1.5, the solution is}$$
$$\text{unique} \implies x(t) \equiv 0 \text{ and } y(t) \equiv 0 .$$

<!-- Page 1 -->
$$\underline{\text{Theorem } 1.6}:$$

$$\underline{\text{Hypothesis}}: \text{ Consider the homogeneous system of the form}$$

$$\left.\begin{array}{l}
\dfrac{dx}{dt} = a_{11}(t)x + a_{12}(t)y \\
\dfrac{dy}{dt} = a_{21}(t)x + a_{22}(t)y
\end{array}\right\} -(2)$$

$$\text{let } (x=f_1(t), \; y=g_1(t)) \text{ and } (x=f_2(t), \; y=g_2(t))$$

$$\Rightarrow \left\{\begin{array}{l}
\dfrac{df_1}{dt} = a_{11}(t)f_1 + a_{12}(t)g_1 \\
\dfrac{dg_1}{dt} = a_{21}(t)f_1 + a_{22}(t)g_1 \\
\dfrac{df_2}{dt} = a_{11}(t)f_2 + a_{12}(t)g_2 \\
\dfrac{dg_2}{dt} = a_{21}(t)f_2 + a_{22}(t)g_2
\end{array}\right.$$

$$\text{be the two solutions of the homogeneous linear system in (2). Let } c_1 \text{ and } c_2 \text{ be two arbitrary constants.}$$

$$\underline{\text{Conclusion}}: \text{ Then, } (x=c_1 f_1(t)+c_2 f_2(t), \; y=c_1 g_1(t)+c_2 g_2(t))$$
$$\text{is also a solution of the system in (2).}$$

$$\text{In other words, a linear combination of the solutions is again a solution for a homogeneous system in (2).}$$

$$\underline{\text{Proof}}: \quad \dfrac{dx}{dt} = c_1 \dfrac{df_1}{dt} + c_2 \dfrac{df_2}{dt}$$

$$= c_1 (a_{11}(t)f_1 + a_{12}(t)g_1) + c_2 (a_{11}(t)f_2 + a_{12}(t)g_2)$$

$$= a_{11}(t) (c_1 f_1 + c_2 f_2) + a_{12}(t) (c_1 g_1 + c_2 g_2)$$

<!-- Page 2 -->
$$= a_{11}(t) x + a_{12}(t) y$$

$$\text{Ily } \dfrac{dy}{dt} = a_{21}(t)x + a_{22}(t)y .$$

$$\Rightarrow (x(t), y(t)) \text{ is a solution of } (2).$$
$$(c_1 f_1(t)+c_2 f_2(t), \; c_1 g_1(t)+c_2 g_2(t)) \text{ is a solution of } (2).$$

$$\underline{\text{Example } 1.7}: \text{ Consider the system } \left.\begin{array}{l}
\dfrac{dx}{dt} = 3x+y, \\
\dfrac{dy}{dt} = 6x+4y
\end{array}\right\} - (*)$$

$$\text{We have already verified that}$$

$$(1) \; (x=e^{6t}, \; y=3e^{6t}) \text{ is a solution pair of the given system.}$$

$$(2) \; (x=e^t, \; y=-2e^t) \text{ is a solution pair of the given system.}$$

$$\text{Now, verify that } (x=c_1 e^{6t} + c_2 e^t, \; y=3c_1 e^{6t} - 2c_2 e^t)$$
$$\text{is a solution for the considered system }$$
$$\text{any real } c_1, c_2 .$$

