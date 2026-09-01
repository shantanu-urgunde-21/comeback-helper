---
course: "differential equations"
source_file: "MA301 Lecture 10.pdf"
tags: ["math", "coursework", "differential-equations"]
---

# MA301 Lecture 10

<!-- Page 1 -->
$$\text{Lecture } 10$$

$$\textbf{Result: } \text{Consider the homogeneous linear system:}$$

$$\frac{dx}{dt} = a_{11}x + a_{12}y$$
$$\frac{dy}{dt} = a_{21}x + a_{22}y$$

$(i)$ If the roots of the associated characteristic equation
$$\lambda^2 - (a_{11} + a_{22})\lambda + (a_{11}a_{22} - a_{12}a_{21}) = 0$$

has two complex roots $\lambda_1 = a + ib$, $\lambda_2 = \bar{\lambda}_1 = a - ib$ (where $b \neq 0$), and
$$\omega = \begin{bmatrix} A + iB \\ C + iD \end{bmatrix} = \begin{bmatrix} A \\ C \end{bmatrix} + i \begin{bmatrix} B \\ D \end{bmatrix} \in \mathbb{C}^2$$
$$\underbrace{\hspace{1cm}}_{u \in \mathbb{R}^2} \underbrace{\hspace{1cm}}_{v \in \mathbb{R}^2}, A, B, C, D \in \mathbb{R}$$

is an eigenvector for the matrix $M = \begin{bmatrix} a_{11} & a_{12} \\ a_{21} & a_{22} \end{bmatrix}$ corresponding to the eigenvalue $\lambda_1 = a + ib$,

and $\bar{\omega} = \begin{bmatrix} A - iB \\ C - iD \end{bmatrix} = \begin{bmatrix} A \\ C \end{bmatrix} - i \begin{bmatrix} B \\ D \end{bmatrix} \in \mathbb{C}^2$
$$\underbrace{\hspace{1cm}}_{u \in \mathbb{R}^2} \underbrace{\hspace{1cm}}_{v \in \mathbb{R}^2}$$

is an eigenvector for $M = \begin{bmatrix} a_{11} & a_{12} \\ a_{21} & a_{22} \end{bmatrix}$ corresponding to the eigenvalue $\lambda_2 = \bar{\lambda}_1 = a - ib$.

---

<!-- Page 2 -->
$$\text{Then, the set } \{\omega, \bar{\omega}\} \text{ is linearly independent (L.I.).}$$

$$\text{Further, the set } \left\{ u = \begin{bmatrix} A \\ C \end{bmatrix}, v = \begin{bmatrix} B \\ D \end{bmatrix} \right\} \subset \mathbb{R}^2 \text{ is L.I.}$$

$(ii)$ If we denote $\overbrace{\begin{pmatrix} x \\ y \end{pmatrix} = \left(\begin{bmatrix} A \\ C \end{bmatrix} + i \begin{bmatrix} B \\ D \end{bmatrix}\right) e^{\lambda_1 t}}^{\omega},$ then the pair $(x, y)$ of complex valued functions is a solution of the given system.

$(iii)$ If we denote
$$\begin{aligned}
\text{Re } X &= \text{Real part of function } X \\
\text{Re } y &= \text{Real part of function } y \\
\text{Im } X &= \text{Imaginary part of function } X \\
\text{Im } y &= \text{Imaginary part of function } y,
\end{aligned}$$

then the pairs $(\text{Re } X, \text{Re } y)$ and $(\text{Im } X, \text{Im } y)$ of real valued functions are two linearly independent solutions of the given system.

$(iv)$ By part $(iii)$, the general solution is given by $c_1 (\text{Re } X, \text{Re } y) + c_2 (\text{Im } X, \text{Im } y),$ that is

---

<!-- Page 3 -->
$$\begin{aligned}
x &= e^{at} (A (c_1 \cos bt + c_2 \sin bt) - B (c_1 \sin bt + c_2 \cos bt)), \\
y &= e^{at} (C (c_1 \cos bt + c_2 \sin bt) - D (c_1 \sin bt + c_2 \cos bt))
\end{aligned}$$

$$\text{on any interval } [a, b].$$

$$\textbf{Proof }(i)\textbf{: } \text{Since } \omega \text{ and } \bar{\omega} \text{ are eigenvectors for the matrix } M = \begin{bmatrix} a_{11} & a_{12} \\ a_{21} & a_{22} \end{bmatrix} \text{ corresponding to the distinct eigenvalues}$$

$$\lambda_1 = a + ib \text{ \& } \lambda_2 = \bar{\lambda}_1 = a - ib \ (b \neq 0, \text{ so } \lambda_1 \neq \lambda_2),$$

$$\text{respectively, by the argument given in the previous case the set } \{\omega, \bar{\omega}\} \text{ is a L.I. set.}$$

$$\text{The proof is as follows:}$$

$$\text{Let } \alpha, \beta \in \mathbb{C} \text{ be such that}$$
$$\alpha \omega + \beta \bar{\omega} = 0 \quad -(1)$$
$$\Rightarrow M (\alpha \omega + \beta \bar{\omega}) = 0$$
$$= \alpha (M\omega) + \beta (M\bar{\omega}) = 0$$
$$= \alpha \lambda_1 \omega + \beta \lambda_2 \bar{\omega} = 0 \quad -(2)$$

$$\lambda_1 \times (1) \Rightarrow \alpha \lambda_1 \omega + \beta \lambda_1 \bar{\omega} = 0 \quad -(3)$$

$$(2) - (3) \Rightarrow \beta (\lambda_2 - \lambda_1) \bar{\omega} = 0$$
$$\Rightarrow \beta = 0 \quad (\lambda_1 \neq \lambda_2, \ \bar{\omega} \neq 0 \text{ as eigenvectors})$$

$$\beta = 0 \text{ and eqn } (1) \Rightarrow \alpha \omega = 0 \Rightarrow \alpha = 0 \ (\omega \neq 0 \text{ as eigenvector})$$

$$\Rightarrow \alpha = \beta = 0 \Rightarrow \text{So, } \{\omega, \bar{\omega}\} \text{ is L.I. }]$$

<!-- Page 1 -->
Now, we prove that $\{u, v\} \subset \mathbb{R}^2$ is L.I. 
(where $w = (u + iv) \in \mathbb{C}^2$)
$\in \mathbb{R}^2 \quad \in \mathbb{R}^2$

Let $c_1, c_2 \in \mathbb{R}$ be such that $c_1 u + c_2 v = 0$
$\Rightarrow \left(\frac{c_1 + ic_2}{2} + \frac{c_1 - ic_2}{2}\right)u + \left(\frac{c_1 + ic_2}{2i} - \frac{c_1 - ic_2}{2i}\right)v = 0$

$\Rightarrow \left(\frac{c_1 + ic_2}{2} + \frac{c_1 - ic_2}{2}\right)u - \frac{i^2}{i} \left(\frac{c_1 + ic_2}{2} - \frac{c_1 - ic_2}{2}\right)v = 0$

$\Rightarrow \left(\frac{c_1 + ic_2}{2} + \frac{c_1 - ic_2}{2}\right)u - i \left(\frac{c_1 + ic_2}{2} - \frac{c_1 - ic_2}{2}\right)v = 0$
$\quad \underbrace{\hspace{1cm}}_{K_1} \quad \underbrace{\hspace{1cm}}_{K_2} \quad \underbrace{\hspace{1.2cm}}_{K_1} \quad \underbrace{\hspace{1.2cm}}_{K_2}$

$\Rightarrow K_1 u + K_2 u - i K_1 v + i K_2 v = 0$
$\Rightarrow K_1 (u - iv) + K_2 (u + iv) = 0$
$\Rightarrow K_1 \bar{w} + K_2 w = 0$
$\Rightarrow K_1 = K_2 = 0 \quad (\because \{w, \bar{w}\} \text{ is L.I. in } \mathbb{C}^2)$

$\Rightarrow \frac{c_1 + ic_2}{2} = 0, \quad \frac{c_1 - ic_2}{2} = 0 \Rightarrow c_1 = 0 \text{ \& } c_2 = 0$

So, $\{u, v\}$ is L.I.

**Proof (ii):** Let us denote
$\begin{pmatrix} X \\ Y \end{pmatrix} = \left(\begin{bmatrix} A \\ C \end{bmatrix} + i \begin{bmatrix} B \\ D \end{bmatrix}\right) e^{\lambda_1 t}, \quad (\lambda_1 = a + ib).$

Then, $X = (A + iB) e^{\lambda_1 t}, \quad Y = (C + iD) e^{\lambda_1 t}$
$\frac{dX}{dt} = (A + iB) \lambda_1 e^{\lambda_1 t}, \quad \frac{dY}{dt} = (C + iD) \lambda_1 e^{\lambda_1 t}$
$\underset{\text{Show!}\Downarrow}{L_1} \quad \underset{\text{Show}\downarrow}{L_2}$
$= a_{11}X + a_{12}Y \quad \quad = a_{21}X + a_{22}Y!$

<!-- Page 2 -->
Now as $Mw = \lambda_1 w$
$$\begin{bmatrix} a_{11} & a_{12} \\ a_{21} & a_{22} \end{bmatrix} \begin{bmatrix} A + iB \\ C + iD \end{bmatrix} = \lambda_1 \begin{bmatrix} A + iB \\ C + iD \end{bmatrix}$$

$$a_{11}(A + iB) + a_{12}(C + iD) = \lambda_1 (A + iB) \quad -(3)$$
$$a_{21}(A + iB) + a_{22}(C + iD) = \lambda_1 (C + iD) \quad -(4)$$

Now, $a_{11}X + a_{12}Y = a_{11}(A + iB)e^{\lambda_1 t} + a_{12}(C + iD)e^{\lambda_1 t} \quad -(5)$
\& $a_{21}X + a_{22}Y = a_{21}(A + iB)e^{\lambda_1 t} + a_{22}(C + iD)e^{\lambda_1 t} \quad -(6)$

Using (1), (3), (5) $\implies \frac{dX}{dt} = a_{11}X + a_{12}Y$
Using (2), (4), (6) $\implies \frac{dY}{dt} = a_{21}X + a_{22}Y$

Thus, the pair $(X, Y)$ of complex valued functions is a solution of the given system.

**Proof (iii):** By part (ii), the pair $(X, Y)$ is a solution (complex valued functions)
$$\frac{dX}{dt} = a_{11}X + a_{12}Y, \quad \frac{dY}{dt} = a_{21}X + a_{22}Y$$
First equation $X$
$$\frac{d}{dt} (\operatorname{Re} X + i \operatorname{Im} X) = a_{11}(\operatorname{Re} X + i \operatorname{Im} X) + a_{12}(\operatorname{Re} Y + i \operatorname{Im} Y)$$
Comparing Real \& Imaginary parts, we have
First equation
$$\begin{cases}
\frac{d}{dt} (\operatorname{Re} X) = a_{11} \operatorname{Re} X + a_{12} \operatorname{Re} Y \quad -(1) \\
\frac{d}{dt} (\operatorname{Im} X) = a_{11} \operatorname{Im} X + a_{12} \operatorname{Im} Y \quad -(2)
\end{cases}$$

<!-- Page 3 -->
Second Equation:
$$\begin{cases}
\frac{d}{dt} (\operatorname{Re} Y) = a_{21} \operatorname{Re} X + a_{22} \operatorname{Re} Y \quad -(1)' \\
\frac{d}{dt} (\operatorname{Im} Y) = a_{21} \operatorname{Im} X + a_{22} \operatorname{Im} Y \quad -(2)'
\end{cases}$$

(1) \& $(1)' \implies$ The pair $(\operatorname{Re} X, \operatorname{Re} Y)$ is a solution.

(2) \& $(2)' \implies$ The pair $(\operatorname{Im} X, \operatorname{Im} Y)$ is a solution.

Next, claim is to prove that
$\{(\operatorname{Re} X, \operatorname{Re} Y), (\operatorname{Im} X, \operatorname{Im} Y)\}$ is a linearly independent set, where

$$X = (A + iB) e^{\lambda_1 t}$$
$$X = (A + iB) e^{(a + ib)t}$$
$$= (A + iB) e^{at} (\cos bt + i \sin bt)$$

$$\operatorname{Re} X = e^{at}[A \cos bt - B \sin bt]$$
$$\operatorname{Im} X = e^{at}[A \sin bt + B \cos bt]$$

$$Y = (C + iD) e^{\lambda_1 t}$$
$$= (C + iD) e^{at} [\cos bt + i \sin bt]$$

$$\operatorname{Re} Y = e^{at}[C \cos bt - D \sin bt]$$
$$\operatorname{Im} Y = e^{at}[D \sin bt + D \cos bt]$$ *(Note: typo in original text for $\operatorname{Im} Y$)*

<!-- Page 1 -->

Let $C_1, C_2 \in \mathbb{R}$ be st
$$C_1 (\operatorname{Re} X, \operatorname{Re} Y) + C_2 (\operatorname{Im} X, \operatorname{Im} Y) = (0, 0)$$
$$C_1 \operatorname{Re} X + C_2 \operatorname{Im} X = 0 \quad , \quad C_1 \operatorname{Re} Y + C_2 \operatorname{Im} Y = 0$$
$$C_1 e^{at} [A \cos bt - B \sin bt] + C_2 e^{at} [A \sin bt + B \cos bt] = 0$$

$$\begin{cases}
C_1 [A \cos bt - B \sin bt] + C_2 [A \sin bt + B \cos bt] = 0 \\
\text{III}^{\text{ly}} \\
C_1 [C \cos bt - D \sin bt] + C_2 [C \sin bt + D \cos bt] = 0
\end{cases}$$

$$\rightarrow \underbrace{\begin{bmatrix} A & B \\ C & D \end{bmatrix}}_{\substack{\text{invertible} \\ \text{as}}} \underbrace{\begin{bmatrix} \cos bt & \sin bt \\ -\sin bt & \cos bt \end{bmatrix}}_{\substack{\downarrow \\ \text{invertible}}} \begin{bmatrix} C_1 \\ C_2 \end{bmatrix} = \begin{bmatrix} 0 \\ 0 \end{bmatrix}$$

$$\cos^2 bt + \sin^2 bt = 1, \quad \forall b \in \mathbb{R}, \forall t$$

$$(\because \left\{ u = \begin{bmatrix} A \\ C \end{bmatrix}, v = \begin{bmatrix} B \\ D \end{bmatrix} \right\} \text{ is } \text{L.I. set.}$$

$$\text{So, } \operatorname{rank} \begin{bmatrix} A & B \\ C & D \end{bmatrix} = 2, \text{ so invertible.})$$

$$(\text{Rank of } M = \text{no. of linearly independent columns/rows in the matrix } M)$$

$$\Rightarrow \begin{bmatrix} C_1 \\ C_2 \end{bmatrix} = \begin{bmatrix} 0 \\ 0 \end{bmatrix} \Rightarrow C_1 = C_2 = 0$$

$$\text{So } \{(\operatorname{Re} X, \operatorname{Re} Y), (\operatorname{Im} X, \operatorname{Im} Y)\} \text{ is a } \text{LI set.}$$

---

**Proof (iv):** Using (iii), (iv) directly follows.

