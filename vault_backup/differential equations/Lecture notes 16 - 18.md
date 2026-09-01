---
course: "differential equations"
source_file: "Lecture notes 16 - 18.pdf"
tags: ["math", "coursework", "differential-equations"]
---

# Lecture notes 16 - 18

<!-- Page 1 -->
$$\text{Lecture} - 16 \ \& \ 17 \ \& \ 18$$

$$\text{\textbf{\text{Wronskian}}}: \text{The Wronskian of two differentiable functions } \{y_1(x), y_2(x)\} \text{ is the determinant defined by}$$

$$W(y_1, y_2) := W(y_1, y_2)(x) = \begin{vmatrix} y_1(x) & y_2(x) \\ y_1'(x) & y_2'(x) \end{vmatrix}$$

$$\text{Similarly, the Wronskian of three differentiable functions } \{y_1(x), y_2(x), y_3(x)\} \text{ is the determinant defined by}$$

$$W(y_1, y_2, y_3) := W(y_1, y_2, y_3)(x) = \begin{vmatrix} y_1(x) & y_2(x) & y_3(x) \\ y_1'(x) & y_2'(x) & y_3'(x) \\ y_1''(x) & y_2''(x) & y_3''(x) \end{vmatrix}$$

$$\text{\textbf{\text{Checking L.I. / L.D. using Wronskian}}}:$$

$$\text{Suppose } \{y_1(x), y_2(x), y_3(x)\} \text{ are three twice differentiable functions defined on an interval } I \text{ and we need to check if they are L.I. or not. Let}$$

$$c_1 y_1 + c_2 y_2 + c_3 y_3 = 0 \quad — \quad (1)$$

$$\text{Differentiating } (1) \text{ we get}$$

$$c_1 y_1' + c_2 y_2' + c_3 y_3' = 0 \quad — \quad (2)$$

---

<!-- Page 2 -->
$$\text{Again differentiating}$$

$$c_1 y_1'' + c_2 y_2'' + c_3 y_3'' = 0 \quad — \quad (3)$$

$$\text{\textbf{\text{Important observations}}}: \text{We can write the equations } (1) - (3) \text{ in the matrix form as follows: } \forall x \in I$$

$$\begin{pmatrix} y_1(x) & y_2(x) & y_3(x) \\ y_1'(x) & y_2'(x) & y_3'(x) \\ y_1''(x) & y_2''(x) & y_3''(x) \end{pmatrix} \begin{pmatrix} c_1 \\ c_2 \\ c_3 \end{pmatrix} = \begin{pmatrix} 0 \\ 0 \\ 0 \end{pmatrix} \quad — \quad (4)$$

$$\text{Let } x = x_0 \text{ such that } W(y_1, y_2, y_3)(x_0) \neq 0, \text{ for some } x_0 \in I. \quad — \quad (5)$$

$$\text{Now, put } x = x_0 \text{ in } (4), \text{ we have}$$

$$\begin{bmatrix} y_1(x_0) & y_2(x_0) & y_3(x_0) \\ y_1'(x_0) & y_2'(x_0) & y_3'(x_0) \\ y_1''(x_0) & y_2''(x_0) & y_3''(x_0) \end{bmatrix} \begin{bmatrix} c_1 \\ c_2 \\ c_3 \end{bmatrix} = \begin{bmatrix} 0 \\ 0 \\ 0 \end{bmatrix} \quad — \quad (6)$$

$$\text{Using } W(y_1, y_2, y_3)(x_0) \neq 0 \text{ (from } (5)) \text{ in } (6), \text{ we have}$$

$$c_1 = c_2 = c_3 = 0.$$

$$\text{\textbf{\text{Remark}}}: \text{Note that it is only necessary to find one point } x_0 \in I \text{ for which } W(y_1, y_2, y_3)(x_0) \neq 0 \text{ to conclude that } \{y_1, y_2, y_3\} \text{ are L.I. on } I.$$

---

<!-- Page 3 -->
$$\text{\textbf{\text{Test for linear independence}}}$$

$$\text{From the above observations, we conclude the following result:}$$

$$\text{\textbf{\text{Theorem}}}: \text{Suppose } y_1 \text{ and } y_2 \text{ are differentiable functions on an interval } I. \text{ If for some } x_0 \in I, \text{ the Wronskian } W(y_1, y_2)(x_0) \neq 0, \text{ then the functions } y_1, y_2 \text{ are linearly independent on } I.$$

$$\text{The converse of the above statement is false.}$$

$$\text{That is, two differentiable functions are linearly independent does not imply that the Wronskian is non-zero at some point.}$$

$$\text{\textbf{\text{Counter example}}}: \text{Consider two functions } y_1(x) = x^2 \text{ and } y_2(x) = x|x| \text{ in the interval } I = (-1, 1). \text{ Check that } y_1, y_2 \text{ are L.I. in } (-1, 1) \text{ but } W(y_1, y_2)(x) = 0 \ \forall x \in (-1, 1).$$

$$\text{\textbf{\text{Remark}}}: \text{We will see in Theorem (T1) below that the converse of the above statement is true under an additional assumption.}$$

<!-- Page 4 -->
that $y_1, y_2$ are LI solutions of some second order homogeneous linear differential equation in the monic form. But before that we will establish properties of Wronskian.

$\circledast$ **Abel's Lemma:** Let $y_1(x)$ and $y_2(x)$ be two solutions of
$$y'' + p(x) y' + q(x) y = 0 \quad - (1)$$
in an interval $I$. Let $W(x)$ be their Wronskian. Then
$$\boxed{W'(x) = - p(x) W(x)}$$

<u>Proof</u>: $y_1$ and $y_2$ satisfy $(*)$, then we have
$$\left. \begin{array}{l} y_1'' + p(x) y_1' + q(x) y_1 = 0 \\ y_2'' + p(x) y_2' + q(x) y_2 = 0 \end{array} \right\} \quad (* *)$$

$$W(x) = \begin{vmatrix} y_1 & y_2 \\ y_1' & y_2' \end{vmatrix} = y_1 y_2' - y_1' y_2 \quad - (A)$$

$$W'(x) = y_1' y_2' + y_1 y_2'' - y_1'' y_2' - y_1'' y_2$$
$$= y_1 y_2'' - y_1'' y_2$$

Use $(* *)$ to write,

<!-- Page 5 -->
$$W'(x) = y_1 (- p(x) y_2' - q(x) y_2)$$
$$- (- p(x) y_1' - q(x) y_1) y_2$$
$$= - p(x) y_1 y_2' - q(x) y_1 y_2 + p(x) y_1' y_2 + q(x) y_1 y_2$$
$$= - p(x) \underbrace{(y_1 y_2' - y_1' y_2)}_{W(x) \text{ from } (A)}$$

Therefore, we have
$$\boxed{W'(x) = - p(x) W(x) \quad - (e1)}$$
Hence proved!

<u>Remark</u>: Consider the differential equation $(e_1)$, we have
$$W'(t) = - p(t) W(t)$$

Write the equation in variable separable form. Then, integrate the resulting equation with respect to $t$ from $x_0$ to $x$, we have:
$$\boxed{W(x) = W(x_0) e^{-\int_{x_0}^x p(t) dt} \quad - (p1)}$$

<u>Remark</u>: In equation $(1)$, it is to note that $p(x), q(x)$ are continuous functions on $I$.

<!-- Page 6 -->
**Wronskian and Linear Independence (LI)** (6)

Now onwards, we will denote $W(y_1, y_2)(x)$ as $W(x)$ whenever there is no confusion.
We state the Wronskian criterion for the linear independence of the linear homogeneous linear ODE.

$\circledast$ **Theorem (T 1):** Suppose that $y_1(x)$, $y_2(x)$ are two solutions of
$$y'' + p(x) y' + q(x) y = 0$$
in an open interval $I$. Let $W(x)$ be their Wronskian. Then the followings are equivalent:
(1) $y_1, y_2$ are linearly independent on $I$.
(2) $\exists \ x_0 \in I$ such that $W(x_0) \neq 0$.
(3) $\forall \ x \in I$, $W(x) \neq 0$.

$\circledast$ **Wronskian and linear dependence:**
Next, we state the Wronskian criterion for the linear dependence of homogeneous linear ODE.

<!-- Page 7 -->

Theorem (T2): Suppose that $y_1(x)$ and $y_2(x)$ are two solutions of
$$y'' + p(x) y' + q(x) y = 0$$
in an open interval $I$. Let $W(x)$ be their Wronskian. Then, the following are equivalent:

(1) $y_1, y_2$ are linearly dependent on $I$.
(2) $\exists \ x_0 \in I$ such that $W(x_0) = 0$.
(3) $\forall \ x \in I, \quad W(x) = 0$.

Proof: Step 1: First we prove the equivalence of (2) and (3), $(2) \iff (3)$.

Clearly $(3) \implies (2)$. The converse can be proved using (11)
$$W(x) = W(x_0) e^{-\int_{x_0}^x p(t) dt}$$
Let $x_0$ be a point in $I$ where $W(x_0) = 0$. Then $W(x) = 0$ for all $x \in I$ using (11). This proves $(2) \implies (3)$.

Step II: $(1) \iff (2)$. From the earlier result $W(x_0) \neq 0 \implies \text{LI}$. The contrapositive statement

<!-- Page 8 -->

of which is
$$\text{LD} \implies W(x_0) = 0.$$
Or in other words, we have proved $(1) \implies (2)$.

Now, it only remains to prove $(2) \implies (1)$.

Suppose (2) holds. Then we need to prove that $y_1, y_2$ are LD. Consider the matrix
$$\begin{bmatrix} y_1(x_0) & y_2(x_0) \\ y_1'(x_0) & y_2'(x_0) \end{bmatrix}.$$

By assumption (2), the matrix is not invertible. Hence the column vectors are linearly dependent. In other words, there exists $a, b$ at least one of which non zero such that
$$a \begin{pmatrix} y_1(x_0) \\ y_1'(x_0) \end{pmatrix} + b \begin{pmatrix} y_2(x_0) \\ y_2'(x_0) \end{pmatrix} = \begin{pmatrix} 0 \\ 0 \end{pmatrix}.$$

Let $z(x) = a y_1(x) + b y_2(x)$ then $z$ satisfies
$$\left. \begin{aligned} z'' + p(x) z' + q(x) z = 0, \\ z(x_0) = 0, \quad z'(x_0) = 0 \end{aligned} \right\} \quad \text{Verify}$$

Now, by the uniqueness theorem for second order linear ODE, $z(x) = 0 \quad \forall \ x \in I$.

or $a y_1(x) + b y_2(x) = 0 \quad \forall \ x$ and for some non zero vector $(a,b)$. Hence $\{y_1, y_2\}$ are LD.

Remark: The proof of theorem (T1) can be achieved following the similar ideas as in the proof of Theorem (T2).

<!-- Page 9 -->

Problem: A differential equation of the form $y' + p(x) y = r(x) y^\alpha$ is called a Bernoulli equation. Note that if $\alpha = 0$ or $1$, it is linear and for all other values of $\alpha$, it is non-linear.

(a) Show that the transformation $u = y^{1-\alpha}$ converts it into a linear equation given by
$$u' + (1-\alpha) p(x) u = (1-\alpha) r(x).$$

(b) Show that the above linear differential equation has an integrating factor given by the function $e^{\int ((1-\alpha) p(x)) dx}$ and thus
$$\left( u e^{\int ((1-\alpha) p(x)) dx} \right)' = (1-\alpha) e^{\int ((1-\alpha) p(x)) dx} r(x).$$

Sol$^n$:
$$u = y^{1-\alpha}, \quad \frac{du}{dx} = (1-\alpha) y^{-\alpha} \frac{dy}{dx} \quad - (1)$$

Now multiply the Bernoulli equation by $(1-\alpha) y^{-\alpha}$ to obtain:
$$\boxed{y' + p(x) y = r(x) y^\alpha}$$

$$(1-\alpha) y^{-\alpha} \frac{dy}{dx} + (1-\alpha) y^{-\alpha} p(x) y = (1-\alpha) y^{-\alpha} y^\alpha r(x)$$
$$\implies (1-\alpha) y^{-\alpha} \frac{dy}{dx} + (1-\alpha) y^{1-\alpha} p(x) = (1-\alpha) r(x)$$
$$\boxed{\frac{du}{dx} + (1-\alpha) u p(x) = (1-\alpha) r(x)}$$

<!-- Page 10 -->
This is a linear equation with integrating factor $e^{\int(1-\alpha)p(x)\,dx}$

$$\left(e^{\int(1-\alpha)p(x)\,dx}\right)\frac{du}{dx} + \left((1-\alpha)\,p(x)\,e^{\int(1-\alpha)p(x)\,dx}\right)u = (1-\alpha)e^{\int(1-\alpha)p(x)\,dx}r(x)$$

$$\boxed{\left(e^{\int(1-\alpha)p(x)\,dx} \, p(x)\, u\right)' = (1-\alpha)\,r(x)\,e^{\int(1-\alpha)p(x)\,dx}}$$

**Problem:** Find a second order linear homogeneous ODE of the form $(*)$ for which $\{x,\, x\ln x\}$ are two linearly independent solutions.

$$y'' + p(x) y' + q(x) y = 0 \quad - - - (*)$$

**Soln:** Put $y(x) = x$ in $(*)$, we have
$$p(x) + q(x) x = 0 \implies p(x) = -x\,q(x)$$

Put $y(x) = x\ln x$, $y'(x) = x \times \frac{1}{x} + \ln x = 1 + \ln x$, $y''(x) = \frac{1}{x}$ in $(*)$,

$$\frac{1}{x} + p(x) (1 + \ln x) + q(x) (x \ln x) = 0$$

$$\implies \frac{1}{x} + (-x\,q(x))(1 + \ln x) + x\ln x\, q(x) = 0$$

$$\implies \frac{1}{x} - x\,q(x) = 0 \implies \boxed{q(x) = \frac{1}{x^2}}$$

$$p(x) = -x\,q(x) \implies p(x) = -x\left(\frac{1}{x^2}\right) = -\frac{1}{x}$$

Therefore, the desired differential equation is

<!-- Page 11 -->
$$y'' + p(x)y' + q(x)y = 0$$

$$\implies y'' - \frac{1}{x}y' + \frac{1}{x^2}y = 0$$

$$\implies \boxed{x^2 y'' - x y' + y = 0}$$

**Problem:** Show that if $p(x)$ is differentiable and $p(x) > 0$ then the Wronskian of two linearly independent solutions of $(p(x)y')' + q(x)y = 0$ is $W(x) = \frac{c}{p(x)}$.

**Solution:** Consider $p(x)y'' + p'(x)y' + q(x)y = 0$.

In the standard form

$$y'' + \left(\underbrace{\frac{p'(x)}{p(x)}}_{P(x)}\right)y' + \left(\underbrace{\frac{q(x)}{p(x)}}_{Q(x)}\right)y = 0$$

We already know that $W'(x) = -P(x)W(x)$ (Abel's formula)

Using (A), we have
$$W'(x) = -\left(\frac{p'(x)}{p(x)}\right) W(x)$$

$$\implies W'(x) + \left(\frac{p'(x)}{p(x)}\right)W = 0 - - - (B)$$

This is a first order differential equation in $W$.

<!-- Page 12 -->
I.F. $p(x)$. Multiplying (B) by $p(x)$, we get $p\,W' + p'W = 0$

$$\implies (p\,W)' = 0 \implies p\,W = c \quad \text{or} \quad \boxed{W(x) = \frac{c}{p(x)}}$$

**Problem:** If $y_1, y_2$ are two linearly independent solutions of $x y'' + 2 y' + x e^x y = 0$ and if $W(y_1, y_2)(1) = 3$, find the value of $W(y_1, y_2)(5)$.

**Soln:** By a result proved in class, we have

$$W(y_1, y_2)(x) = W(y_1, y_2)(x_0) \, e^{-\int_{x_0}^{x} p(t)\,dt}$$

choosing $x_0 = 1$, $W(y_1, y_2)(1) = 3$.

Here $p(x) = \frac{2}{x}$.

$$W(y_1, y_2)(x) = 3x^{-2}$$

$$W(y_1, y_2)(5) = \frac{3}{25}$$

$$\boxed{W(y_1, y_2)(5) = \frac{3}{25}}$$

