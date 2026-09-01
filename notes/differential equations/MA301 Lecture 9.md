---
course: "differential equations"
source_file: "MA301 Lecture 9.pdf"
tags: ["math", "coursework", "differential-equations"]
---

# MA301 Lecture 9

<!-- Page 1 -->
$$\text{Lecture } 9$$

$$\text{Case 2: Two roots } \lambda_1 \text{ and } \lambda_2 \text{ of the characteristic equations are complex conjugate}$$
$$\text{of each other, i.e., } \overline{\lambda}_1 = \lambda_2.$$

$$\text{Exercise: Write the general solution of the following system:}$$
$$\frac{dx}{dt} = 3x + 2y, \quad \frac{dy}{dt} = -5x + y.$$

$$\text{Solution: Let us assume the solution of the form } \begin{bmatrix} x \\ y \end{bmatrix} e^{\lambda t},$$
$$x = Ae^{\lambda t}, \quad y = Be^{\lambda t}$$
$$\frac{dx}{dt} = \lambda Ae^{\lambda t}, \quad \frac{dy}{dt} = \lambda Be^{\lambda t}$$

$$A\lambda e^{\lambda t} = 3Ae^{\lambda t} + 2Be^{\lambda t}$$
$$B\lambda e^{\lambda t} = -5Ae^{\lambda t} + Be^{\lambda t}$$

$$\Rightarrow A\lambda = 3A + 2B, \quad e^{\lambda t} \neq 0$$
$$B\lambda = -5A + B$$

$$A(\lambda - 3) - 2B = 0$$
$$5A + B(\lambda - 1) = 0$$

$$\begin{bmatrix} \lambda - 3 & -2 \\ 5 & \lambda - 1 \end{bmatrix} \begin{bmatrix} A \\ B \end{bmatrix} = \begin{bmatrix} 0 \\ 0 \end{bmatrix}.$$

$$\text{For nontrivial solution (i.e. } (A, B) \neq (0,0)\text{), we must have}$$
$$\det \begin{bmatrix} \lambda - 3 & -2 \\ 5 & \lambda - 1 \end{bmatrix} = 0$$

<!-- Page 2 -->
$$\Rightarrow (\lambda - 3)(\lambda - 1) + 10 = 0$$
$$\Rightarrow \lambda^2 - 4\lambda + 13 = 0$$

$$\left\{ \Delta = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a} = \frac{4 \pm \sqrt{16 - 4(1)(13)}}{2} \right\}$$

$$\lambda = \frac{4 \pm 6i}{2} = 2 \pm 3i$$

$$\text{If } \lambda = 2+i3, \text{ then } M \begin{bmatrix} A \\ B \end{bmatrix} = \lambda \begin{bmatrix} A \\ B \end{bmatrix}.$$

$$\Rightarrow (-1+3i)A - 2B = 0$$
$$\Rightarrow 5A + (2+i3-1)B = 0$$

$$\text{Choose } A = 2, \text{ then } B = -1 + 3i$$
$$x = Ae^{\lambda_1 t} = 2e^{(2+i3)t}$$
$$y = Be^{\lambda_2 t} = (-1+3i)e^{(2+i3)t}$$

$$x = 2e^{2t}(\cos 3t + i \sin 3t)$$
$$y = (-1+3i)e^{2t}(\cos 3t + i \sin 3t)$$

$$y = -e^{2t}\cos 3t - 3e^{2t}\sin 3t + i(3e^{2t}\cos 3t - e^{2t}\sin 3t)$$
$$= e^{2t} [-(\cos 3t + 3\sin 3t) + i (3\cos 3t - \sin 3t)]$$

$$\text{These are complex valued functions.}$$
$$\text{Consider the real parts of both functions}$$
$$(x = 2e^{2t}\cos 3t, \quad y = -e^{2t}(\cos 3t + 3\sin 3t))$$
$$\text{which will be a solution pair.}$$

<!-- Page 3 -->
$$\text{Also, consider the imaginary parts of both functions as a solution pair}$$

$$(x = 2e^{2t}\sin 3t, \quad y = e^{2t}(3\cos 3t - \sin 3t)) = x^{(2)}$$
$$\text{which will be a solution pair.}$$

$$\text{Now, linearly independent verification:}$$

$$W = \begin{vmatrix} 2e^{2t}\cos 3t & 2e^{2t}\sin 3t \\ -e^{2t}(\cos 3t + 3\sin 3t) & e^{2t}(3\cos 3t - \sin 3t) \end{vmatrix}$$
$$= 2e^{4t} [3\cos^2 3t - \cos 3t \sin 3t + \cos 3t \sin 3t + 3\sin^2 3t]$$
$$= 2e^{4t} \neq 0 \quad \forall t$$

$$\text{So, linearly independent solutions.}$$

$$\text{The general solution (real valued) is of the form:}$$
$$(x = 2e^{2t}(C_1 \cos 3t + C_2 \sin 3t), \quad y = -e^{2t}(C_1(\cos 3t + 3\sin 3t) + C_2(\sin 3t - 3\cos 3t)))$$

<!-- Page 1 -->
Problem:
Find the general solution of the following systems:

(1) $\frac{dx}{dt} = \begin{pmatrix} 5 & -2 \\ 4 & -1 \end{pmatrix} x$, where $x = \begin{pmatrix} x_1 \\ x_2 \end{pmatrix}$ and

$\frac{dx}{dt} = \begin{pmatrix} \frac{dx_1}{dt} \\ \frac{dx_2}{dt} \end{pmatrix}$  Do it yourself!

(2) $\frac{dx}{dt} = \begin{pmatrix} 1 & -4 \\ 1 & 1 \end{pmatrix} x$, $M = \begin{bmatrix} 1 & -4 \\ 1 & 1 \end{bmatrix}$, $\det(M - \lambda I) = 0$

$$ \begin{vmatrix} 1-\lambda & -4 \\ 1 & 1-\lambda \end{vmatrix} = 0 \Rightarrow (1-\lambda)^2 + 4 = 0 $$
$$ \Rightarrow \lambda^2 - 2\lambda + 5 = 0 $$

$$ \lambda = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a} = \frac{2 \pm \sqrt{4 - 4(5)}}{2} $$

$$ \lambda_1, \bar{\lambda}_1 = \frac{2 \pm 4i}{2} = 1 \pm 2i $$

$\lambda_1 = 1 + 2i$, $M\mathbf{w} = \lambda_1 \mathbf{w}$  $\nearrow \text{eigenvector (complex)}$
$$\mathbf{w} = \begin{bmatrix} a + ib \\ c + id \end{bmatrix} \begin{matrix} z_1 \\ z_2 \end{matrix}$$

$$ \begin{bmatrix} 1 & -4 \\ 1 & 1 \end{bmatrix} \begin{bmatrix} z_1 \\ z_2 \end{bmatrix} = (1 + 2i) \begin{bmatrix} z_1 \\ z_2 \end{bmatrix} $$

$$ \begin{cases} z_1 - 4z_2 = (1 + 2i)z_1 \Rightarrow -4z_2 = 2iz_1 \\ z_1 + z_2 = (1 + 2i)z_2 \Rightarrow z_1 = 2iz_2 \end{cases} $$

$$ \begin{aligned} (a+ib) &= 2i(c+id) \\ -4(c+id) &= 2i(a+ib) \end{aligned} \Rightarrow \begin{aligned} a+ib &= 2ic - 2d \\ -2c - 2id &= ia - b \end{aligned} $$

<!-- Page 2 -->
$$ \boxed{a = -2d, \quad b = 2c} $$

$c = d = 1 \Rightarrow a = -2, \quad b = 2$
$\mathbf{w} = \begin{bmatrix} z_1 \\ z_2 \end{bmatrix} = \begin{bmatrix} a+ib \\ c+id \end{bmatrix} = \begin{bmatrix} -2+i2 \\ 1+i \end{bmatrix}$
$\mathbf{w} = \underbrace{\begin{bmatrix} -2 \\ 1 \end{bmatrix}}_{\mathbf{u}} + i\underbrace{\begin{bmatrix} 2 \\ 1 \end{bmatrix}}_{\mathbf{v}}, \quad \bar{\mathbf{w}} = \begin{bmatrix} -2 \\ 1 \end{bmatrix} - i\begin{bmatrix} 2 \\ 1 \end{bmatrix}$

The solution associated to eigenvalue $\lambda_1$ is:
$$ x^{(1)} = \begin{pmatrix} x \\ y \end{pmatrix} = \mathbf{w} e^{\lambda_1 t} $$
$$ = \begin{bmatrix} -2+i2 \\ 1+i \end{bmatrix} e^{(1+2i)t} $$

$$ \begin{pmatrix} x \\ y \end{pmatrix} = e^t \begin{bmatrix} -2+i2 \\ 1+i \end{bmatrix} (\cos 2t + i \sin 2t) $$

$$ \begin{pmatrix} x(t) \\ y(t) \end{pmatrix} = \begin{bmatrix} e^t (-2+i2)(\cos 2t + i \sin 2t) \\ e^t (1+i)(\cos 2t + i \sin 2t) \end{bmatrix} $$

$$ \begin{pmatrix} x \\ y \end{pmatrix} = e^t \begin{bmatrix} (-2\cos 2t - 2\sin 2t) + i(2\cos 2t - 2\sin 2t) \\ (\cos 2t - \sin 2t) + i(\cos 2t + \sin 2t) \end{bmatrix} $$

Similarly, find solution associated to eigenvalue $\lambda_2 = \bar{\lambda}_1$:
$$ x^{(2)} = \bar{\mathbf{w}} e^{\lambda_2 t} \text{ (complete!)} $$
General Solution: $C_1 x^{(1)}(t) + C_2 x^{(2)}(t)$

<!-- Page 3 -->
Result: Consider the homogeneous linear system:
$$ \begin{aligned} \frac{dx}{dt} &= a_{11}x + a_{12}y \\ \frac{dy}{dt} &= a_{21}x + a_{22}y \end{aligned} $$

(i) If the roots of the associated characteristic equation
$$ \lambda^2 - (a_{11} + a_{22})\lambda + (a_{11}a_{22} - a_{12}a_{21}) = 0 $$
has two complex roots $\lambda_1 = a + ib$, $\lambda_2 = \bar{\lambda}_1 = a - ib$ (where $b \neq 0$), and
$$ \mathbf{w} = \begin{bmatrix} A + iB \\ C + iD \end{bmatrix} = \underbrace{\begin{bmatrix} A \\ C \end{bmatrix}}_{\mathbf{u} \in \mathbb{R}^2} + i\underbrace{\begin{bmatrix} B \\ D \end{bmatrix}}_{\mathbf{v} \in \mathbb{R}^2}, A, B, C, D \in \mathbb{R} $$
is an eigenvector for the matrix $M = \begin{bmatrix} a_{11} & a_{12} \\ a_{21} & a_{22} \end{bmatrix}$ corresponding to the eigenvalues $\lambda_1 = a + ib$, and
$$ \bar{\mathbf{w}} = \begin{bmatrix} A - iB \\ C - iD \end{bmatrix} = \underbrace{\begin{bmatrix} A \\ C \end{bmatrix}}_{\mathbf{u} \in \mathbb{R}^2} - i\underbrace{\begin{bmatrix} B \\ D \end{bmatrix}}_{\mathbf{v} \in \mathbb{R}^2} $$
is an eigenvector for $M = \begin{bmatrix} a_{11} & a_{12} \\ a_{21} & a_{22} \end{bmatrix}$ corresponding to the eigenvalue $\lambda_2 = \bar{\lambda}_1 = a - ib$.

<!-- Page 1 -->

Then, the set $\{w, \bar{w}\}$ is linearly independent (LI).

Further, the set $\left\{ u = \begin{bmatrix} A \\ C \end{bmatrix}, v = \begin{bmatrix} B \\ D \end{bmatrix} \right\} \subset \mathbb{R}^2$ is LI.

(ii) If we denote
$$\begin{pmatrix} X \\ Y \end{pmatrix} = \left( \overbrace{\begin{bmatrix} A \\ C \end{bmatrix} + i \begin{bmatrix} B \\ D \end{bmatrix}}^{w} \right) e^{\lambda_1 t},$$
then the pair $(X, Y)$ of complex valued functions is a solution of the given system.

(iii) If we denote
$$\begin{aligned}
\operatorname{Re} X &= \text{Real part of function } X \\
\operatorname{Re} Y &= \text{Real part of function } Y \\
\operatorname{Im} X &= \text{Imaginary part of function } X \\
\operatorname{Im} Y &= \text{Imaginary part of function } Y,
\end{aligned}$$
then the pairs $(\operatorname{Re} X, \operatorname{Re} Y)$ and $(\operatorname{Im} X, \operatorname{Im} Y)$ of real valued functions are two linearly independent solutions of the given system.

(iv) By part (iii), the general solution is given by
$$C_1 (\operatorname{Re} X, \operatorname{Re} Y) + C_2 (\operatorname{Im} X, \operatorname{Im} Y), \text{ that is}$$

---
<!-- Page 2 -->

$$\begin{pmatrix} x = e^{at} \left( A(C_1 \cos bt + C_2 \sin bt) - B(C_1 \sin bt + C_2 \cos bt) \right), \\ y = e^{at} \left( C(C_1 \cos bt + C_2 \sin bt) - D(C_1 \sin bt + C_2 \cos bt) \right) \end{pmatrix}$$
on any interval $[a, b]$.

**Proof (i):** Since $w$ and $\bar{w}$ are eigenvectors for the matrix $M = \begin{bmatrix} a_{11} & a_{12} \\ a_{21} & a_{22} \end{bmatrix}$ corresponding to the distinct eigenvalues
$$\lambda_1 = a + ib \quad \& \quad \lambda_2 = \bar{\lambda}_1 = a - ib \quad (b \neq 0, \text{ so } \lambda_1 \neq \lambda_2),$$
respectively, by the argument given in the previous case the set $\{w, \bar{w}\}$ is a LI set.

The proof is as follows:  
Let $\alpha, \beta \in \mathbb{C}$ be such that
$$\alpha w + \beta \bar{w} = 0 \quad \text{--- (1)}$$
$$\implies M(\alpha w + \beta \bar{w}) = 0$$
$$= \alpha(Mw) + \beta(M\bar{w}) = 0$$
$$= \alpha \lambda_1 w + \beta \lambda_2 \bar{w} = 0 \quad \text{--- (2)}$$

$$\lambda_1 \times \text{(1)} \implies \alpha \lambda_1 w + \beta \lambda_1 \bar{w} = 0 \quad \text{--- (3)}$$

$$\text{(2)} - \text{(3)} \implies \beta(\lambda_2 - \lambda_1) \bar{w} = 0$$
$$\implies \beta = 0 \qquad (\lambda_1 \neq \lambda_2, \quad \bar{w} \neq 0 \text{ as eigenvectors})$$

$$\beta = 0 \text{ and eqn (1)} \implies \alpha w = 0 \implies \alpha = 0 \quad (w \neq 0 \text{ as eigenvector})$$

$$\implies \alpha = \beta = 0 \implies \text{So, } \{w, \bar{w}\} \text{ is L.I.}$$

---
<!-- Page 3 -->

Now, we prove that $\{u, v\} \subset \mathbb{R}^2$ is L.I.
$$\left(\text{where } w = (\underbrace{u}_{\in \mathbb{R}^2} + i \underbrace{v}_{\in \mathbb{R}^2}) \in \mathbb{C}^2\right)$$

Let $C_1, C_2 \in \mathbb{R}$ be such that $C_1 u + C_2 v = 0$
$$\implies \left( \frac{C_1 + iC_2}{2} + \frac{C_1 - iC_2}{2} \right) u + \left( \frac{C_1 + iC_2}{2i} - \frac{C_1 - iC_2}{2i} \right) v = 0$$
$$\implies \left( \frac{C_1 + iC_2}{2} + \frac{C_1 - iC_2}{2} \right) u - \frac{i^2}{i} \left( \frac{C_1 + iC_2}{2} - \frac{C_1 - iC_2}{2} \right) v = 0$$
$$\implies (\underbrace{\frac{C_1 + iC_2}{2}}_{K_1} + \underbrace{\frac{C_1 - iC_2}{2}}_{K_2}) u - i (\underbrace{\frac{C_1 + iC_2}{2}}_{K_1} - \underbrace{\frac{C_1 - iC_2}{2}}_{K_2}) v = 0$$
$$\implies K_1 u + K_2 u - i K_1 v + i K_2 v = 0$$
$$\implies K_1 (u - iv) + K_2 (u + iv) = 0$$
$$\implies K_1 \bar{w} + K_2 w = 0$$
$$\implies K_1 = K_2 = 0 \qquad (\because \{w, \bar{w}\} \text{ is L.I. in } \mathbb{C}^2)$$

$$\implies \frac{C_1 + iC_2}{2} = 0, \quad \frac{C_1 - iC_2}{2} = 0 \implies C_1 = 0 \ \& \ C_2 = 0$$

$$\text{So, } \{u, v\} \text{ is L.I.}$$

**Proof (ii):** Let us denote
$$\begin{pmatrix} X \\ Y \end{pmatrix} = \left( \overbrace{\underbrace{\begin{bmatrix} A \\ C \end{bmatrix}}_{u} + i \underbrace{\begin{bmatrix} B \\ D \end{bmatrix}}_{v}}^{w} \right) e^{\lambda_1 t}, \quad (\lambda_1 = a + ib).$$

Then,
$$X = (A + iB)e^{\lambda_1 t}, \qquad Y = (C + iD)e^{\lambda_1 t}$$
$$\frac{dX}{dt} = (A + iB)\lambda_1 e^{\lambda_1 t}, \quad \text{--- (1)} \qquad \frac{dY}{dt} = (C + iD)\lambda_1 e^{\lambda_1 t} \quad \text{--- (2)}$$
$$\begin{aligned}
\text{Show!} \downarrow & & \text{Show} \downarrow & \\
& = a_{11} X + a_{12} Y & & = a_{21} X + a_{22} Y !
\end{aligned}$$

<!-- Page 1 -->
Now as $M\omega = \lambda_1\omega$
$$\begin{bmatrix} a_{11} & a_{12} \\ a_{21} & a_{22} \end{bmatrix} \begin{bmatrix} A + iB \\ C + iD \end{bmatrix} = \lambda_1 \begin{bmatrix} A + iB \\ C + iD \end{bmatrix}$$

$$a_{11}(A + iB) + a_{12}(C + iD) = \lambda_1(A + iB) \quad -\text{③}$$
$$a_{21}(A + iB) + a_{22}(C + iD) = \lambda_1(C + iD) \quad -\text{④}$$

Now, $a_{11}x + a_{12}y = a_{11}(A + iB)e^{\lambda_1 t} + a_{12}(C + iD)e^{\lambda_1 t} \quad -\text{⑤}$
$$\& \quad a_{21}x + a_{22}y = a_{21}(A + iB)e^{\lambda_1 t} + a_{22}(C + iD)e^{\lambda_1 t} \quad -\text{⑥}$$

$$\begin{array}{l|l}
\text{Using } \text{①}, \text{③}, \text{⑤} & \text{②}, \text{④}, \text{⑥} \\
\hline
\dfrac{dx}{dt} = a_{11}x + a_{12}y & \dfrac{dy}{dt} = a_{21}x + a_{22}y
\end{array}$$

Thus, the pair $(x,y)$ of complex valued functions is a solution of the given system.

