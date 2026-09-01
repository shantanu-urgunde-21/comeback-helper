---
course: "differential equations"
source_file: "MA301 Lecture 5.pdf"
tags: ["math", "coursework", "differential-equations"]
---

# MA301 Lecture 5

<!-- Page 1 -->

# Lecture-5
## Particular Solution of Constant Coefficients ODE

### Method of undetermined coefficients:

A simple procedure for finding a particular solution ($y_p$) to a non-homogeneous equation $\mathcal{L}(y) = r(x)$, where '$\mathcal{L}$' is a differential operator with constant coefficients and when '$r(x)$' is of special type:

That is, when $r(x)$ is either

1) a polynomial in $x$
2) an exponential function $e^{\alpha x}$
3) trigonometric functions $\sin(\beta x)$, $\cos(\beta x)$
4) or finite sums and products of these functions

We will mostly consider only the second order linear ODE, in which case

$$\mathcal{L}(y) = y'' + py' + qy = r(x) .$$

---

<!-- Page 2 -->

### Case 1: When $r(x)$ is a polynomial

For finding $y_p(x)$ to the equation $\mathcal{L}(y) = p_n(x)$, where $p_n(x)$ is a polynomial of degree '$n$'.

Try a solution of the form

$$y_p(x) = A_n x^n + A_{n-1} x^{n-1} + \dots + A_1 x + A_0$$

and match the coefficients of $\mathcal{L}(y_p)$ with those of $p_n(x)$:

$$\mathcal{L}(y_p) = p_n(x)$$

**Remark:** This procedure yields $n+1$ linear equations in $n+1$ unknowns $A_0, A_1, \dots, A_n$.

**Example:** Find $y_p$ to
$$\mathcal{L}(y)(x) := y'' + 3y' + 2y = 3x + 1$$

**Solution:** Try the form $y_p(x) = Ax + B$ and attempt to match up $\mathcal{L}(y_p)$ with $3x + 1$.

---

<!-- Page 3 -->

Since $\mathcal{L}(y_p) = 2Ax + 3A + 2B$,

equating

$$2Ax + 3A + 2B = 3x + 1 \implies A = 3/2 \text{ and } B = -7/4$$

Thus, $y_p(x) = \frac{3}{2}x - \frac{7}{4}$.

**Example:** Find a particular solution of
$$y'' - 3y' - 4y = 4x^2 - 1.$$

**Solution:** Set $y(x) = ax^2 + bx + c$.

Substituting, we get

$$-4ax^2 + (-6a - 4b)x + (2a - 3b - 4c) = 4x^2 - 1.$$

Thus, $-4a = 4$, $-6a - 4b = 0$, $2a - 3b - 4c = -1$.

Hence, $a = -1$, $b = 3/2$, $c = -11/8$.

Thus, a particular solution is

$$y(x) = -x^2 + \frac{3x}{2} - \frac{11}{8}$$

<!-- Page 1 -->

**Case 2: When $r(x)$ is an exponential function:**

The method of undetermined coefficients will also work for equations of the form
$$L(y) = a e^{\alpha x},$$
where $a$ and $\alpha$ are given constants.
Try $y_p$ of the form
$$y_p(x) = A e^{\alpha x}$$
and solve $L(y_p)(x) = y'' + 3y' + 2y = e^{3x}$.

**Example:** Find $y_p$ to
$$L(y)(x) := y'' + 3y' + 2y = e^{3x}$$

Seek $y_p(x) = A e^{3x}$. Then
$$L(y_p) = 9A e^{3x} + 3(3A e^{3x}) + 2(A e^{3x}) = 20A e^{3x}$$

Now, $L(y_p) = e^{3x} \implies 20A e^{3x} = e^{3x} \implies A = 1/20$.

Thus, $y_p(x) = \left(\frac{1}{20}\right) e^{3x}$

<!-- Page 2 -->

**Example:** Find the general and particular solution of the DE:
$$y'' - 3y' - 4y = 3e^{2x}.$$

**Solution:** We'll search for a solution of the form $A e^{2x}$, where '$A$' is a constant.

So, put $y = e^{2x}$. We get
$$(A e^{2x})'' - 3(A e^{2x})' - 4A e^{2x} = 3e^{2x}$$

Thus,
$$4A e^{2x} - 6A e^{2x} - 4A e^{2x} = 3e^{2x} \implies A = -\frac{1}{2}.$$

Hence, $y_p(x) = -\frac{1}{2} e^{2x}$ is a particular solution of the DE.

**How do you get the general solution?**
Analyse roots of $m^2 - 3m - 4 = 0$. So general solution is
$$y(x) = c_1 e^{4x} + c_2 e^{-x} - \frac{1}{2} e^{2x}$$

<!-- Page 3 -->

**Example:** Find the general and particular solution of the DE:
$$y'' + 5y' + 6y = e^{-3x}$$

**Solution:** We'll search for a solution of the form $A e^{-3x}$, where '$A$' is a constant. So, put $y = A e^{-3x}$. We get
$$(A e^{-3x})'' + 5(A e^{-3x})' + 6A e^{-3x} = e^{-3x}.$$

**This leads to $0 = e^{-3x}$!**

This is because $y_p(x) = A e^{-3x}$ satisfies the homogeneous equation
$$y'' + 5y' + 6y = 0$$
and not the equation itself!

Hence, we choose $y_p(x) = A x e^{-3x}$ as a particular solution of the DE.

In case $-3$ is a double root of the auxiliary equation, we know that $x e^{-3x}$ is also a solution of the homogeneous equation. Then, we choose $y_p(x) = k x^2 e^{-3x}$ as a particular solution.

In this example, $-3$ is not the double root of

<!-- Page 1 -->
the auxiliary equation and therefore $y_p(x) = k x e^{-3x}$ would work.

Check: $A = -1$. Write the general solution!

**Example:** Find $y_p$ to $L(y) = y'' - y' - 12y = e^{4x}$.

**Solution:** Note that $y_h(x) = c_1 e^{4x} + c_2 e^{-3x}$.

Try finding $y_p$ with the guess $y_p(x) = Ae^{4x}$ as before. Since $e^{4x}$ is a solution to the corresponding homogeneous equation $L(y) = 0$, we replace this choice of $y_p$ by $y_p(x) = Axe^{4x}$. Since $L(xe^{4x}) \neq 0$, there exists a particular solution of the form
$$y_p(x) = Axe^{4x}, \quad A = \frac{1}{7}.$$

**Remark:** If $L(y_p) = 0$, then replace $y_p(x)$ by $xy_p(x)$. If $L(xy_p) = 0$ then replace $xy_p$ by $x^2y_p$ and so on. Then, employing $x^s y_p$, where '$s$' is the smallest nonnegative integer such that
$$L(x^s y_p) \neq 0.$$

<!-- Page 2 -->
**Case 3:** When $r(x)$ is a trigonometric function

For an equation of the form
$$L(y) = a\cos\beta x + b\sin\beta x,$$
try $y_p$ of the form
$$y_p(x) = A\cos\beta x + B\sin\beta x$$
and solve $L(y_p) = a\cos\beta x + b\sin\beta x$ for the unknowns $A$ and $B$.

**Example:** Find $y_p$ to $L(y) := y'' - y' - y = \sin x$.

**Solution:** Seek $y_p(x)$ of the form $y_p(x) = A\cos x + B\sin x$. Then,
$$L(y_p) = \sin x \implies A = \frac{1}{5}, \quad B = -\frac{2}{5}$$

Thus, $y_p(x) = \frac{1}{5}\cos x -\frac{2}{5}\sin x$

<!-- Page 3 -->
**Example:** Find a particular solution of
$$y'' - 3y' - 4y = 2\sin x$$

**Solution:** Make a guess, as to functions of which form, we'll search for as a solution. $a\sin x$? No. $a\sin x + b\cos x$? Yes. So, set
$$y(x) = a\sin x + b\cos x.$$
Thus,
$$\begin{aligned}
y'(x) &= a\cos x - b\sin x \\
y''(x) &= -a\sin x - b\cos x
\end{aligned}$$
Substituting, we get
$$(-5a + 3b - 2)\sin x + (-3a - 5b)\cos x = 0$$

Therefore, $a = -\frac{5}{17}$, $b = \frac{3}{17}$, and a particular solution is
$$y(x) = -\frac{5}{17}\sin x + \frac{3}{17}\cos x.$$

