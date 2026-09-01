---
course: "differential equations"
source_file: "MA301 Lecture 3.pdf"
tags: ["math", "coursework", "differential-equations"]
---

# MA301 Lecture 3

<!-- Page 1 -->

### Lecture-3

**Remark:** A set of two functions $\{\phi_1(x), \phi_2(x)\}$ are linearly dependent if
(a) at least one of them is a zero function.
(b) or $\phi_1(x) = c \phi_2(x) \quad \forall x \in I$.

### Examples of linearly dependent / independent functions:

(1) $\{\sin x, \cos x\}$ in the interval $[0, 2\pi]$.
(2) $\{1, x\}$ in the interval $[0, 1]$.
(3) $\{1, x, x^2\}$ in the interval $[0, 1]$.
(4) $\{\sin x, \cos x, \sin x + 5\cos x\}$ in the interval $[0, 2\pi]$.
(5) $\{1, e^x, e^{2x}\}$ in the interval $(-\infty, \infty)$.
(6) $\{1 + 2x, 1 + x, x\}$ in the interval $(-1, 1)$.
(7) $\{\sin x, \sin^2 x\}$
(8) $\{\sin^2 x, \cos^2 x\}$
(9) $\{\sin^2 x, \cos^2 x, 1\}$
(10) $\{\sin^2 x, \cos^2 x, \cos 2x\}$

**Answer:** Examples (4), (6), (9) and (10) are linearly dependent. We will see if there is any other method to check the linear independence of collection of functions.

<!-- Page 2 -->

### Wronskian : (Definition)

The Wronskian of two differentiable functions $\{y_1(x), y_2(x)\}$ is the determinant defined by

$$W(y_1, y_2) := W(y_1, y_2)(x) = \begin{vmatrix} y_1(x) & y_2(x) \\ y_1'(x) & y_2'(x) \end{vmatrix}$$

The Wronskian of three twice differentiable functions $\{y_1(x), y_2(x), y_3(x)\}$ is the determinant defined by

$$W(y_1, y_2, y_3) := W(y_1, y_2, y_3)(x) = \begin{vmatrix} y_1(x) & y_2(x) & y_3(x) \\ y_1'(x) & y_2'(x) & y_3'(x) \\ y_1''(x) & y_2''(x) & y_3''(x) \end{vmatrix}.$$

### Checking L.I. / L.D. using Wronskian :

Suppose $\{y_1(x), y_2(x), y_3(x)\}$ are three twice differentiable functions defined on an interval $I$ and we need to check if they are L.I. or not. Let

$$c_1 y_1 + c_2 y_2 + c_3 y_3 = 0.$$

Differentiating once we get

$$c_1 y_1' + c_2 y_2' + c_3 y_3' = 0$$

<!-- Page 3 -->

Again differentiating

$$c_1 y_1'' + c_2 y_2'' + c_3 y_3'' = 0$$

### Important Observations:

We can write the last three equations in the matrix form to get

$$\begin{pmatrix} y_1(x) & y_2(x) & y_3(x) \\ y_1'(x) & y_2'(x) & y_3'(x) \\ y_1''(x) & y_2''(x) & y_3''(x) \end{pmatrix} \begin{pmatrix} c_1 \\ c_2 \\ c_3 \end{pmatrix} = \begin{pmatrix} 0 \\ 0 \\ 0 \end{pmatrix}$$

(a) If the Wronskian $W(y_1, y_2, y_3)(x) \neq 0$ then $c_1 = c_2 = c_3 = 0$ or the vectors $\{y_1, y_2, y_3\}$ are L.I.

(b) Note that it is only necessary to find one point $x_0 \in I$ for which $W(y_1, y_2, y_3)(x_0) \neq 0$ to conclude that $\{y_1, y_2, y_3\}$ are L.I.

<!-- Page 1 -->

### Test for linear independence:

From the above observations, we conclude the following result:

**$\underline{\text{Theorem}} :$** Suppose $y_1$ and $y_2$ are differentiable functions on an interval $I$. If for some $x_0 \in I$, the Wronskian $W(y_1, y_2)(x_0) \neq 0$, then the functions $y_1, y_2$ are linearly independent on $I$.

Converse of the statement is **$\underline{\text{False}}$**. Why?

That is, two differentiable functions are linearly independent does not imply that the Wronskian is non-zero at some point.

**$\underline{\text{Counter Example}} :$** Consider two functions $y_1(x) = x^2$ and $y_2(x) = x|x|$ in the interval $I = (-1, 1)$.

Check that $y_1, y_2$ are L.I in $(-1, 1)$, but $W(y_1, y_2)(x) = 0$ for all $x \in (-1, 1)$.

---

<!-- Page 2 -->

We will see in Theorem (T1) later, that the converse of the above statement is true, under an additional assumption that $y_1, y_2$ are LI solutions of some second order homogeneous linear differential equation in the monic form. But, before that we will establish properties of Wronskian.

**$\underline{\text{Abel's lemma}} :$** Let $y_1(x)$ and $y_2(x)$ be two solutions of
$$y'' + p(x)y' + q(x)y = 0 \quad \text{--- } (*)$$
in an open interval $I$. Let $W(x)$ be their Wronskian. Then
$$\boxed{W'(x) = -p(x)W(x)}$$

**$\underline{\text{Proof}} :$** $y_1$ and $y_2$ satisfy $(*)$,
$$\left. \begin{aligned} y_1'' + p(x)y_1' + q(x)y_1 &= 0 \\ y_2'' + p(x)y_2' + q(x)y_2 &= 0 \end{aligned} \right\} \quad \text{--- } (**)$$

$$W(x) = \begin{vmatrix} y_1 & y_2 \\ y_1' & y_2' \end{vmatrix} = y_1 y_2' - y_1' y_2 \quad \text{--- } (\text{A})$$

$$W'(x) = \cancel{y_1' y_2'} + y_1 y_2'' - \cancel{y_1' y_2'} - y_1'' y_2$$

---

<!-- Page 3 -->

$$= y_1 y_2'' - y_1'' y_2$$

Use $(**)$ to write,

$$W'(x) = y_1 (-p(x)y_2' - q(x)y_2) - (-p(x)y_1' - q(x)y_1) y_2$$
$$= -p(x)y_1 y_2' - \cancel{q(x)y_1 y_2} + p(x)y_1' y_2 + \cancel{q(x)y_1 y_2}$$
$$= -p(x) \underbrace{(y_1 y_2' - y_1' y_2)}_{W(x) \text{ (from } \text{A})} \implies \boxed{W'(x) = -p(x)W(x)}$$
$$\underline{\text{proved}}$$

Integrate the above from $x_0$ to $x$, we get

$$W(x) = W(x_0) e^{-\int_{x_0}^x p(t) dt} \quad \text{--- } (P1)$$

<!-- Page 1 -->

# Wronskian and linear independence (LI)

Now onwards, we will denote $W(y_1, y_2)(x)$ as $W(x)$ whenever there is no confusion. We state the Wronskian Criterion for the linear independence of homogeneous linear ODE.

**Theorem (T1):** Suppose that $y_1(x), y_2(x)$ are two solutions of
$$y'' + p(x)y' + q(x)y = 0$$
in an open interval $I$. Let $W(x)$ be their Wronskian. Then, the followings are equivalent:
1) $y_1, y_2$ are linearly independent on $I$.
2) $\exists x_0 \in I$ such that $W(x_0) \neq 0$.
3) $\forall x \in I$, $W(x) \neq 0$.

<!-- Page 2 -->

# Wronskian and linear dependence:

Next, we state the Wronskian criterion for the linear dependence of homogeneous linear ODE.

**Theorem (T2):** Suppose that $y_1(x), y_2(x)$ are two solutions of
$$y'' + p(x)y' + q(x)y = 0$$
in an open interval $I$. Let $W(x)$ be their Wronskian. Then, the followings are equivalent:
(1) $y_1, y_2$ are linearly dependent on $I$.
(2) $\exists x_0 \in I$ such that $W(x_0) = 0$.
(3) $\forall x \in I$, $W(x) = 0$.

## Proof of linearly dependence (LD) and Wronskian:

**Step 1:** First we prove the equivalence of (2) and (3), $(2) \Leftrightarrow (3)$.

Clearly $(3) \Rightarrow (2)$. The converse can be proved using (P1). Let $x_0$ be a point in $I$ where $W(x_0) = 0$. Then $W(x) = 0$ for all $x \in I$ using (P1). This proves $(2) \Rightarrow (3)$.

Recall:
$$\text{(P1)} \quad W(x) = W(x_0) e^{-\int_{x_0}^x p(t) dt}$$

<!-- Page 3 -->

**Step II:** $(1) \Leftrightarrow (2)$. From the result proved $W(x_0) \neq 0 \Rightarrow \text{LI}$.

The contrapositive statement of which is $\text{LD} \Rightarrow W(x_0) = 0$. Or in other words, we have proved $(1) \Rightarrow (2)$.

Now, it only remains to prove $(2) \Rightarrow (1)$.
$$W(x_0) = 0 \Rightarrow \text{LD}.$$

Suppose (2) holds. Then, we need to prove that $y_1, y_2$ are LD. Consider the matrix
$$\begin{pmatrix} y_1(x_0) & y_2(x_0) \\ y_1'(x_0) & y_2'(x_0) \end{pmatrix}$$

By assumption (2), the matrix is not invertible.
Hence, the column vectors are linearly dependent.
In other words, there exists $a, b$ at least one of which non zero such that
$$a \begin{pmatrix} y_1(x_0) \\ y_1'(x_0) \end{pmatrix} + b \begin{pmatrix} y_2(x_0) \\ y_2'(x_0) \end{pmatrix} = \begin{pmatrix} 0 \\ 0 \end{pmatrix} \quad \text{--- } \circledast$$

Let $z(x) = a y_1(x) + b y_2(x)$.
Then, $z$ satisfies
$$\text{Verify!} \quad \begin{cases} z'' + p(x) z' + q(x) z = 0 \\ z(x_0) = 0, \quad z'(x_0) = 0 \end{cases} \quad (\text{from } \circledast)$$

<!-- Page 1 -->
Recall: Consider the initial value problem $y' + p(x) y = 0\ ;\ y(x_0) = 1$. By Picard's theorem the above IVP must admit a unique solution $u(x)$ when $p(x)$ is continuous function in an interval $I$ containing $x_0$.

Theorem: Let $u$ be the solution of the homogeneous linear differential equation $y' + p(x) y = 0$ with initial condition $y(x_0)=1$. If $y_h$ is a solution of $y' + p(x) y = 0$, then $y_h(x) = C u(x)$ for some real constant $C$.

We are looking for an analogous result in case of second order linear homogeneous equation. That is, can we characterize all the solutions of a second order linear homo-geneous differential equation?

<!-- Page 2 -->
Basic observation on the solution set of $2^{\text{nd}}$ order linear homogeneous ordinary differential equation:

Let $S$ denote the set of all solutions to a second homogeneous ordinary differential equation, That is, $S = \{y : y'' + p(x)y' + q(x)y = 0\}$ and let $u, v \in S$. For some constants $a, b \in \mathbb{R}$, consider the function $w = au + bv$. Then we will show that $w$ is also a solution of the ODE. By linearity,
$$w'' + p(x)w' + q(x)w = a(u'' + p(x)u' + q(x)u) + b(v'' + p(x)v' + q(x)v) = 0 .$$

$\underline{\text{Remark:}}$ If $u, v \in S$ then $au+bv \in S$. In the language of linear algebra it means that $S$ forms a vector space.

We proved that the solutions of a second order linear homogeneous differential equation forms a vector space. Let us denote this set by $S$. It remains to show that it forms a two dimensional vector space.

<!-- Page 3 -->
Now, by the uniqueness theorem for second order linear ODE, $z(x)=0 \ \forall\ x \in I$. or
$$a y_1(x) + b y_2(x) = 0 \quad \text{for all } x$$
and for some non-zero vector $(a, b)$.
Hence, $\{y_1, y_2\}$ are $\text{LD}$. (Proved)

The proof of Theorem (T1) can be achieved following the similar ideas as in the proof of Theorem (T2).

<!-- Page 1 -->
Consider two IVP's

$$y'' + p(x)y' + q(x)y = 0 \ ;\ y(x_0) = 1\ ,\ y'(x_0) = 0 \quad - (1)$$

$$y'' + p(x)y' + q(x)y = 0 \ ;\ y(x_0) = 0\ ,\ y'(x_0) = 1 \quad - (2)$$

let $y_1$ and $y_2$ be the solutions of $(1)$ and $(2)$, respectively.

**Observation:** 

1) The vectors $y_1, y_2$ are LI. Why?
2) Because $W(x_0) = W(y_1, y_2)(x_0) = 1$. and by the previous theorem (T1), $\{y_1, y_2\}$ are LI.

**Claim:** $\{y_1, y_2\}$ forms a basis for $S$. Now, proof of the theorem is complete if the claim is verified.

**Proof:** Let $u$ be an arbitrary solution of $y'' + p(x)y' + q(x)y = 0$.

Fix a point $x_0 \in I$ and let $a = u(x_0)$ and $b = u'(x_0)$.

(i) Observe that the function $v(x) = a y_1 + b y_2$ satisfies the IVP: 
$$v'' + p(x)v' + q(x)v = 0\ ,\ v(x_0) = a$$
$$v'(x_0) = b$$

(ii) Also $u'' + p(x)u' + q(x)u = 0 \ ; \ u(x_0) = a,\ u'(x_0) = b$.

(iii) From the existence and uniqueness theorem for

<!-- Page 2 -->
the second order linear differential equation, we obtain $u(x) = v(x)$ for all $x \in I$ or 
$$u(x) = a y_1(x) + b y_2(x) \quad \text{in } I.$$

That is, the claim is verified. It means for every element $u \in S$, there exist $a, b \in \mathbb{R}$ such that
$$\boxed{u = a y_1 + b y_2}.$$

