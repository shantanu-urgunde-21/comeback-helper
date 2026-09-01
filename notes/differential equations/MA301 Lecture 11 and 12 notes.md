---
course: "differential equations"
source_file: "MA301 Lecture 11 and 12 notes.pdf"
tags: ["math", "coursework", "differential-equations"]
---

# MA301 Lecture 11 and 12 notes

<!-- Page 1 -->
# Basic Strategy

## lectures 11 & 12

Replace the system of linear equations with an equivalent system (?) (one with the same solution set) which is easier to solve.

<!-- Page 2 -->
Basics involved in the Gaussian elimination method:

We observe that in the Gaussian elimination method, we apply some set of row operations on the matrix to reduce it to an equivalent matrix which can be solved easily. These operations are called the elementary row operations for matrices. Next, we state the elementary row operations for matrices and equations.

| | Elementary row operations (Matrices) | Elementary row operations (Equations) |
|---|---|---|
| 1. | Interchange two rows <br> $R_i \leftrightarrow R_j$ (interchange $i^{\text{th}}$ and $j^{\text{th}}$ row) | Interchange two equations |
| 2. | Addition of a constant multiple of one row to another row <br> $R_i \to R_i + C R_j \quad (j \neq i)$ | Addition of a constant multiple of one equation to another equation |
| 3. | Multiplication of a row by a non-zero constant $C (\neq 0)$ <br> $R_i \to C R_i$ | Multiplication of an equation by a non zero constant $C (\neq 0)$ |

<!-- Page 3 -->
Definition: (Row-equivalent Systems)

A linear system $S_1$ is row-equivalent to a linear system $S_2$ ($S_1 \sim S_2$), if $S_2$ can be obtained from $S_1$ by finitely many elementary row operations.

Result: Two row-equivalent systems have the same set of solutions.

Recall: Now, we state the steps involved in Gaussian elimination method for a general $m \times n$ system.

a) Search the first column of $[A|b]$ from the top to the bottom for the first non-zero entry, and then if necessary, the second column (the case where all the coefficients corresponding to the first variable are zero), and then the third column, and so on. The entry thus found is called the current pivot.

b) Interchange, if necessary, the row containing the current pivot with the first row.

<!-- Page 1 -->
**Definition:** Row Echelon Form (REF)
A matrix is said to be in a row echelon form (or to be a row echelon matrix) if it has a staircase-like pattern characterized by the following properties:

(a) All zero rows (if any) are at the bottom.
(b) If we call the leftmost non-zero entry of a non-zero row its **leading entry**, then the leading entry of each non-zero row is to the right of the leading entry of the preceding row.

$$[U \mid C] = \begin{bmatrix}
0 & \cdots & p_1 & * & * & * & * & * & * & \cdots & * & \Big| & c_1 \\
0 & & 0 & \cdots & p_2 & * & * & * & * & \cdots & * & \Big| & c_2 \\
0 & & 0 & 0 & 0 & 0 & p_3 & * & * & \cdots & * & \Big| & c_3 \\
\vdots & & \vdots & & \vdots & & 0 & \vdots & \vdots & & \vdots & \Big| & \vdots \\
0 & & 0 & & 0 & & 0 & p_r & * & \cdots & * & \Big| & c_r \\
0 & & 0 & & 0 & & 0 & 0 & 0 & \cdots & 0 & \Big| & c_{r+1} \\
0 & & 0 & 0 & 0 & 0 & 0 & 0 & 0 & \cdots & 0 & \Big| & c_m
\end{bmatrix}$$

$$\text{Examples } 1) \begin{bmatrix} 2 & 3 & -2 & 4 \\ 0 & -9 & 7 & -8 \\ 0 & 0 & 0 & 20 \\ 0 & 0 & 0 & 0 \end{bmatrix} \text{ is in REF.}$$

---

<!-- Page 2 -->
c) Keeping the row containing the pivot (that is, the first row) untouched, subtract appropriate multipliers of the first row from all the other rows to obtain all zeros below the **current pivot** in its column.

d) Repeat the preceding steps on the submatrix consisting of all those elements which are **below and to the right** of the current pivot.

e) Stop when no further pivot can be found.

---

<!-- Page 3 -->
The effect of Gauss Elimination method:

The $m \times n$ coefficient matrix $A$ of the linear system $Ax=b$ is thus reduced to an $m \times n$ row echelon matrix (?) $U$ and the augmented matrix $[A \mid b]$ is reduced to

$$[U \mid C] = \begin{bmatrix}
0 & \cdots & p_1 & * & * & * & * & * & * & \cdots & * & \Big| & c_1 \\
0 & & 0 & \cdots & p_2 & * & * & * & * & \cdots & * & \Big| & c_2 \\
0 & & 0 & 0 & 0 & 0 & p_3 & * & * & \cdots & * & \Big| & c_3 \\
\vdots & & \vdots & & \vdots & & 0 & \vdots & \vdots & & \vdots & \Big| & \vdots \\
0 & & 0 & & 0 & & 0 & p_r & * & \cdots & * & \Big| & c_r \\
0 & & 0 & & 0 & & 0 & 0 & 0 & \cdots & 0 & \Big| & c_{r+1} \\
0 & & 0 & 0 & 0 & 0 & 0 & 0 & 0 & \cdots & 0 & \Big| & c_m
\end{bmatrix}$$

The entries denoted by $*$ and $c_i$'s are real numbers; they may or may not be zero. The $p_i$'s denote the pivots; they are non zero.

<!-- Page 1 -->
2) $\begin{bmatrix} 1 & 0 & 0 & 4 \\ 0 & 1 & 0 & -8 \\ 0 & 0 & 1 & 20 \end{bmatrix}$ is in R.E.F.

3) $\begin{bmatrix} 1 & 2 & 3 & 4 & 5 \\ 0 & 0 & 1 & -1 & 2 \\ 0 & 0 & 0 & 1 & 5 \end{bmatrix}$ Is it in R.E.F.? (Yes)

4) $\begin{bmatrix} 2 & -1 & 2 & 1 & 5 \\ 0 & 1 & 1 & -3 & 3 \\ 0 & 2 & 0 & 0 & 5 \\ 0 & 0 & 0 & 3 & 2 \end{bmatrix}$ is not in R.E.F.

5) $\begin{bmatrix} 1 & 0 & 0 & 1/2 & 0 & 1 \\ 0 & 0 & 1 & -1/3 & 0 & 2 \\ 0 & 0 & 0 & 0 & 1 & 3 \end{bmatrix}$ is in R.E.F.

Remark:
$$A \quad \Uparrow \text{Gaussian Elimination}$$

$$U = \begin{bmatrix} 
0 & \cdots & p_1 & * & * & * & * & * & * & \cdots & * \\ 
0 & \cdots & 0 & -0 & p_2 & * & * & * & * & \cdots & * \\ 
0 & \cdots & 0 & 0 & 0 & 0 & p_3 & * & * & \cdots & * \\ 
\vdots & & \vdots & & \vdots & & \vdots & \vdots & & & \vdots \\ 
0 & \cdots & 0 & & 0 & & 0 & p_r & * & \cdots & * \\ 
0 & \cdots & 0 & & 0 & & 0 & 0 & 0 & \cdots & 0 \\ 
0 & \cdots & 0 & & 0 & & 0 & 0 & 0 & \cdots & 0 
\end{bmatrix}$$

<!-- Page 2 -->
Definition:
If the $j^{\text{th}}$ column of $U$ contains a pivot, then $x_j$ is called a \underline{basic variable}; otherwise $x_j$ is called a \underline{free variable}.

In fact, there are \underline{$n-r$ free variables}, where $n$ is the number of columns (unknown) of $A$ (and hence of $U$).

Definition: For a matrix $A$, we define

$$\text{rank}(A) = \text{number of non-zero rows in R.E.F. of } A.$$
$$\text{nullity}(A) = \text{number of free variables in the solution of } A x = 0.$$

Example: If $A = \begin{bmatrix} 1 & 0 & -5 \\ 0 & 1 & 3 \\ 0 & 0 & 0 \end{bmatrix}$, then $\text{rank}(A) = 2$ and $\text{nullity}(A) = 1$.

<!-- Page 3 -->
let us observe an example in which the matrix has repeated eigenvalues and sufficient eigenvectors to span $\mathbb{R}^2$. $\dim(\text{Null space of } M - 3I) = 2$

Example: $M = \begin{bmatrix} 3 & 0 \\ 0 & 3 \end{bmatrix}$, eigenvalues $3, 3$.
$$(M - 3I) v = 0$$
$$\Rightarrow \begin{bmatrix} 0 & 0 \\ 0 & 0 \end{bmatrix} \begin{bmatrix} v_1 \\ v_2 \end{bmatrix} = \begin{bmatrix} 0 \\ 0 \end{bmatrix} \text{, eigenvectors } \underbrace{\begin{bmatrix} 1 \\ 0 \end{bmatrix}}_{v_1}, \underbrace{\begin{bmatrix} 0 \\ 1 \end{bmatrix}}_{v_2}$$

$\text{Null space/eigenspace of } M - \lambda I = M v_1 = 3 v_1$
$\{v \in \mathbb{R}^2 \text{ s.t. } (M - \lambda I) v = 0\} M v_2 = 3 v_2$

Now, we observe an example in which the matrix has repeated eigenvalues, but insufficient eigenvectors to span $\mathbb{R}^n$.

Example: Consider the matrix $M = \begin{bmatrix} 2 & 1 \\ 0 & 2 \end{bmatrix}$, $\dim(\text{Null space of } M - 2I) = 1$

The characteristic polynomial is $(\lambda - 2)^2 = 0$.

<!-- Page 1 -->
The eigenvalues are $2, 2$.

However, there is only one eigenvector ($v_1$) corresponding to the eigenvalue $2$.

Therefore, the eigenvector does not span $\mathbb{R}^2$.

Recall:

$\underline{\text{Rank-Nullity Theorem:}}$

$\underbrace{\text{rank}(A) + \underbrace{\text{nullity}(A)}_{\text{dim(null space of } A)} = \text{no of unknowns } n}$

$\underline{\text{Definition:}}$ For a matrix $A$, we define

$\text{rank}(A) = \text{number of non-zero rows in REF of } A.$

$\text{nullity}(A) = \text{number of free variables in the solution of } Ax=0.$

$\underline{\text{Example:}}$ If $A = \begin{bmatrix} 1 & 0 & -5 \\ 0 & 1 & 3 \\ 0 & 0 & 0 \end{bmatrix}$, then $\text{rank}(A) = 2$ and $\text{nullity}(A) = 1$.

<!-- Page 2 -->
$\underline{\text{Result:}}$ Consider the system:
$$\frac{dx}{dt} = a_{11}x + a_{12}y$$
$$\frac{dy}{dt} = a_{21}x + a_{22}y,$$
where $a_{11}, a_{12}, a_{21}, a_{22}$ are constants.

Assume both roots of the associated characteristic equation
$$\lambda^2 - (a_{11}+a_{22})\lambda + (a_{11}a_{22} - a_{12}a_{21}) = 0$$
are $\underline{\text{equal}}$ and $\underline{\text{real}}$, ie. $\lambda_1, \lambda_2 \in \mathbb{R}$ and $\lambda_1 = \lambda_2$.

$\underline{\text{Case (i): } \text{rank}(M-\lambda_1 I) = 0}$
(ie. $M-\lambda_1 I = 0$ is a zero matrix)

Then, $\text{dim}(\text{null space of }(M-\lambda_1 I)) = 2$. Further, for any two linearly independent eigenvectors $v_1$ and $v_2$ (for the eigenvalue $\lambda_1$), $v_1 e^{\lambda_1 t}$ and $v_2 e^{\lambda_1 t}$ are solutions of the given system and the set $\{v_1 e^{\lambda_1 t}, v_2 e^{\lambda_2 t}\}$ is a linearly independent set.

$\text{rank}(A) + \text{nullity}(A) = \text{number of unknowns } (n)$

<!-- Page 3 -->
Thus, the general solution in this case ($\text{rank}(M-\lambda_1 I) = 0$) is given by
$$\begin{pmatrix} x \\ y \end{pmatrix} = C_1 v_1 e^{\lambda_1 t} + C_2 v_2 e^{\lambda_2 t} \text{ on any interval } [a,b] \text{, where } C_1 \text{ and } C_2 \text{ are arbitrary real constant. }]$$

$\underline{\text{Case (ii): } \text{rank}(M-\lambda_1 I) = 1}$
Then, $\text{dim}(\text{null space of }(M-\lambda_1 I)) = 1$.
Further, there exists $v \in \text{null space of }(M-\lambda_1 I)^2$, $v \notin \text{null space of }(M-\lambda_1 I)$, such that $\{v, (M-\lambda_1 I)v\}$ is a L.I. set.
$$\text{say } u \quad \Rightarrow (M-\lambda_1 I)^2 v = 0 \text{ and } (M-\lambda_1 I)u = 0$$

Also, $u e^{\lambda_1 t}$ and $(ut+v)e^{\lambda_1 t}$ forms a linearly independent solution of the given system on any interval $[a,b]$.
So, the general solution is given by
$$\begin{pmatrix} x \\ y \end{pmatrix} = C_1 u e^{\lambda_1 t} + C_2(ut+v)e^{\lambda_1 t}$$
on any interval $[a,b]$, where $C_1$ and $C_2$ are arbitrary real constants.

$\underline{\text{Proof: Case (i) } \text{rank}(M-\lambda_1 I) = 0.}$
By Rank-Nullity theorem,
$$\text{rank}(M-\lambda_1 I) + \text{nullity}(M-\lambda_1 I) \overset{\text{dim(null space }(M-\lambda_1 I))}{=} \text{dim }\mathbb{R}^2$$

<!-- Page 1 -->
$$\Rightarrow \quad 0 + \text{nullity}(M - \lambda_1 I) = 2$$
$$\Rightarrow \dim(\text{nullspace}(M - \lambda_1 I)) = 2.$$

Let $\{v_1, v_2\}$ be a basis of $\underbrace{\text{nullspace of }(M - \lambda_1 I)}_{\text{Eigenspace}}$.

\underline{Claim:} $\{v_1 e^{\lambda_1 t}, v_2 e^{\lambda_1 t}\}$ forms a linearly independent
set of solutions for the given system on
any interval $[a, b]$.

Let $\alpha, \beta \in \mathbb{R}$ be s.t.
$$\alpha v_1 e^{\lambda_1 t} + \beta v_2 e^{\lambda_1 t} = 0 \quad \forall t \in [a, b].$$
$$\alpha v_1 + \beta v_2 = 0 \quad (e^{\lambda_1 t} \neq 0, \quad \forall t)$$
$$\Rightarrow \alpha = 0 = \beta \quad (\because \{v_1, v_2\} \text{ is LI set})$$

So, $\{v_1 e^{\lambda_1 t}, \overset{x^{(1)}}{v_1 e^{\lambda_1 t}}, v_2 e^{\lambda_1 t}\}$ is LI set on any
interval $[a, b]$.

Now, we verify $v_1 e^{\lambda_1 t} \text{ \& } v_2 e^{\lambda_2 t}$ are solutions
of the given system:

$$\frac{dx}{dt} = a_{11}x + a_{12}y$$
$$\frac{dy}{dt} = a_{21}x + a_{22}y$$

Say $v_1 = \begin{pmatrix} v_{11} \\ v_{21} \end{pmatrix} \in \mathbb{R}^2, \quad v_2 = \begin{pmatrix} v_{12} \\ v_{22} \end{pmatrix} \in \mathbb{R}^2$

<!-- Page 2 -->
$$x^{(1)} = \begin{pmatrix} x \\ y \end{pmatrix} = v_1 e^{\lambda_1 t} = \begin{pmatrix} v_{11} e^{\lambda_1 t} \\ v_{21} e^{\lambda_1 t} \end{pmatrix} \quad \text{using ③ } \lambda_1 v_{11} e^{\lambda_1 t}$$

$$\frac{dx}{dt} = \lambda_1 v_{11} e^{\lambda_1 t}, \quad a_{11}x + a_{12}y = a_{11} v_{11} e^{\lambda_1 t} + a_{12} v_{21} e^{\lambda_1 t}$$

$$\frac{dy}{dt} = \lambda_1 v_{21} e^{\lambda_1 t}, \quad a_{21}x + a_{22}y = a_{21} v_{11} e^{\lambda_1 t} + a_{12} v_{21} e^{\lambda_1 t}$$
$$\hspace{8.5cm} \uparrow \text{ (Typo in image: } a_{12} \text{ instead of } a_{22}\text{)}$$

Since, $M v_1 = \lambda_1 v_1$ \quad using ④ $\lambda_1 v_1 e^{\lambda_1 t}$ \quad $\lambda_1 v_2 e^{\lambda_1 t}$
$$\begin{bmatrix} a_{11} & a_{12} \\ a_{21} & a_{22} \end{bmatrix} \begin{bmatrix} v_{11} \\ v_{21} \end{bmatrix} = \lambda_1 \begin{bmatrix} v_{11} \\ v_{21} \end{bmatrix},$$

we have
$$a_{11}x + a_{12}y = \lambda_1 v_{11} e^{\lambda_1 t} \quad - ③$$
$$a_{21}x + a_{22}y = \lambda_1 v_{21} e^{\lambda_1 t} \quad - ④$$

So, from ①, ②, ③, ④,

$v_1 e^{\lambda_1 t}$ is a solution of the given system.

Similarly, we can check that $v_2 e^{\lambda_1 t}$ is also
a solution of the given system on any interval
$[a, b]$.

So, the general solution is given by
$$\begin{pmatrix} x \\ y \end{pmatrix} = c_1 v_1 e^{\lambda_1 t} + c_2 v_2 e^{\lambda_1 t} \text{ on any interval } [a, b],$$

where $c_1 \ \& \ c_2$ are arbitrary constants.

<!-- Page 3 -->
Case(ii): (a) $\text{rank}(M - \lambda_1 I) = 1$.
Then, $\dim(\text{nullspace of }(M - \lambda_1 I)) = 1$.
Further, there exists $v \in \text{nullspace of }(M - \lambda_1 I)^2$
$v \notin \text{nullspace of }(M - \lambda_1 I)$ and
$$\{v, (M - \lambda_1 I)v\} \text{ is a L.I. set.}$$
$$\hspace{3cm}\underbrace{\ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ \ }_{\text{say } u}$$

(b) Also, $u e^{\lambda_1 t}$ and $(ut + v)e^{\lambda_1 t}$ form linearly
independent solutions of the given system on any
interval $[a, b]$.

So, the general solution is given by
$$\begin{pmatrix} x \\ y \end{pmatrix} = c_1 u e^{\lambda_1 t} + c_2 (ut + v)e^{\lambda_1 t}$$
on any interval $[a, b]$, where $c_1$ and $c_2$ are
arbitrary real constants.

\underline{Proof:} (a) $\text{rank}(M - \lambda_1 I) = 1$. $\quad -\circledast$

By Rank-Nullity theorem,
$\text{rank}(A) + \text{nullity}(A) = n$, where $A$ is $n \times n$ matrix.

Replace '$A$' by $M - \lambda_1 I$, we have
$$\underbrace{\text{rank}(M - \lambda_1 I)}_{1 \text{ (from }\circledast\text{)}} + \text{nullity}(M - \lambda_1 I) = 2.$$

<!-- Page 1 -->
$$\Rightarrow \quad \text{nullity}(M - \lambda_1 I) = 1$$
$$\dim(\text{null space of } (M - \lambda_1 I)) = 1 \quad - (**)$$

The characteristic equation for the matrix '$M$' is $\det(M - \lambda I) = 0$.

Since, multiplicity of $\lambda_1$ is $2$, $\det(M - \lambda I) = (\lambda - \lambda_1)^2 = 0$.

$\xrightarrow{\text{(Cayley Hamilton Theorem)}}$ We know that every matrix satisfies its own characteristic equation. So,
$$(M - \lambda_1 I)^2 = 0 \quad (\text{or } (M - \lambda_1 I)^2 \text{ is a zero matrix}).$$
$$\text{rank}(M - \lambda_1 I)^2 = 0.$$

Then, null space of $(M - \lambda_1 I)^2 = \mathbb{R}^2$.
$$\dim(\text{null space of } (M - \lambda_1 I)^2) = 2 \quad - (***)$$

From $(**)$ and $(***)$, we have
$$\text{null space of } (M - \lambda_1 I) \subsetneq \text{ null space of } (M - \lambda_1 I)^2$$
$$\downarrow_{\text{(one dimension)}} \qquad \uparrow_{\text{(Two dimensions)}}$$

Let $v \in \text{ null space of } (M - \lambda_1 I)^2$ be such that $v \notin \text{ null space of } (M - \lambda_1 I)$.

$$\Rightarrow (M - \lambda_1 I)^2 v = 0 \text{ and } (M - \lambda_1 I) v \neq 0 \quad - (e_1)$$
$$\underbrace{(M - \lambda_1 I)^2 v = 0}_{\downarrow}$$
$$\Rightarrow (M - \lambda_1 I)(M - \lambda_1 I) v = 0$$

<!-- Page 2 -->
$$\Rightarrow (M - \lambda_1 I) v \in \text{ null space of } (M - \lambda_1 I).$$

Set $u = (M - \lambda_1 I) v \neq 0 \quad (\text{from } (e_1))$.

Now, we claim that $\{u, v\}$ is a LI set.

Let $\alpha, \beta \in \mathbb{R}$ be such that $\alpha u + \beta v = 0$.
$$\Rightarrow \alpha (M - \lambda_1 I) v + \beta v = 0 \quad (\because u = (M - \lambda_1 I) v)$$

Apply both sides $M - \lambda_1 I$, we have
$$\Rightarrow \alpha (M - \lambda_1 I)^2 v + \beta (M - \lambda_1 I) v = 0$$

$$\Rightarrow \alpha (0) + \beta (M - \lambda_1 I) v = 0$$
$$\Rightarrow \beta (M - \lambda_1 I) v = 0$$
$$\Rightarrow \beta = 0 \quad (\because (M - \lambda_1 I) v \neq 0, \text{ from } (e_1))$$

Now, $\beta = 0 \Rightarrow \alpha u + \beta v = 0$
$$\Rightarrow \alpha u = 0 \Rightarrow \alpha = 0 \quad (\because u = (M - \lambda_1 I) v \neq 0)$$

Thus, $\alpha u + \beta v = 0 \Rightarrow \alpha = \beta = 0$.
So, $\{u, v\}$ is a LI set.

Next, we claim that $u e^{\lambda_1 t}$ and $(ut + v)e^{\lambda_1 t}$ forms a linearly independent solution of given system on any interval $[a, b]$.

<!-- Page 3 -->
Let $\alpha, \beta \in \mathbb{R}$ be such that
$$\alpha u e^{\lambda_1 t} + \beta (ut + v) e^{\lambda_1 t} = 0, \quad \forall t \in [a, b]$$
$$\Rightarrow \alpha u + \beta (ut + v) = 0, \quad \forall t \in [a, b]$$
$$\Rightarrow (\alpha + \beta t) u + \beta v = 0, \quad \forall t \in [a, b].$$

Put $t = t_0 \in [a, b]$ in the above equation.
$$(\alpha + \beta t_0) u + \beta v = 0$$

$$\Rightarrow \alpha + \beta t_0 = 0, \quad \beta = 0$$
$$(\because \{u, v\} \text{ is LI set})$$

$$\Rightarrow \alpha + 0 \cdot t_0 = 0 \quad (\because \beta = 0)$$
$$\Rightarrow \alpha = \beta = 0.$$

So, $\{ \underbrace{u e^{\lambda_1 t}}_{x^{(1)}}, \underbrace{(ut + v) e^{\lambda_1 t}}_{x^{(2)}} \}$ is a LI set.

Now, we show $\underbrace{u e^{\lambda_1 t}}$ and $\underbrace{(ut + v) e^{\lambda_1 t}}$ are solutions of the given system.

Say $u = \begin{pmatrix} u_1 \\ u_2 \end{pmatrix} \in \mathbb{R}^2, \quad v = \begin{pmatrix} v_1 \\ v_2 \end{pmatrix} \in \mathbb{R}^2$.

Since, $u = (M - \lambda_1 I) v$, we have
$$(M - \lambda_1 I) u = (M - \lambda_1 I)^2 v = 0.$$
$$\Rightarrow Mu = \lambda_1 u \Rightarrow \begin{pmatrix} a_{11} & a_{12} \\ a_{21} & a_{22} \end{pmatrix} \begin{pmatrix} u_1 \\ u_2 \end{pmatrix} = \lambda_1 \begin{pmatrix} u_1 \\ u_2 \end{pmatrix}$$

<!-- Page 1 -->
$$\Rightarrow \begin{aligned} a_{11}u_1 + a_{12}u_2 &= \lambda_1 u_1 && -\text{ (A)} \\ a_{21}u_1 + a_{22}u_2 &= \lambda_1 u_2 && -\text{ (B)} \end{aligned}$$

$$\text{Now, } x^{(1)} = \begin{pmatrix} x \\ y \end{pmatrix} = u e^{\lambda_1 t} = \begin{pmatrix} u_1 e^{\lambda_1 t} \\ u_2 e^{\lambda_1 t} \end{pmatrix}$$

$$\Rightarrow x = u_1 e^{\lambda_1 t}, \quad y = u_2 e^{\lambda_1 t}$$

$$\frac{dx}{dt} = \lambda_1 u_1 e^{\lambda_1 t}, \quad \frac{dy}{dt} = \lambda_1 u_2 e^{\lambda_1 t}$$

$$\text{Claim:} \begin{cases} \dfrac{dx}{dt} = a_{11}x + a_{12}y \\ \dfrac{dy}{dt} = a_{21}x + a_{22}y \end{cases}$$

$$\therefore a_{11}x + a_{12}y = a_{11} u_1 e^{\lambda_1 t} + a_{12} u_2 e^{\lambda_1 t}$$
$$= \lambda_1 u_1 e^{\lambda_1 t} \quad (\because \text{ (A)})$$
$$= \frac{dx}{dt}$$

$$\therefore a_{21}x + a_{22}y = a_{21} u_1 e^{\lambda_1 t} + a_{22} u_2 e^{\lambda_1 t}$$
$$= \lambda_2 u_2 e^{\lambda_1 t} \quad (\because \text{ (B)})$$
$$= \frac{dy}{dt}$$

$$\text{Thus, } \begin{pmatrix} x \\ y \end{pmatrix} = u e^{\lambda_1 t} = \begin{pmatrix} u_1 e^{\lambda_1 t} \\ u_2 e^{\lambda_1 t} \end{pmatrix} \text{ is a solution of}$$
$$\text{the given system.}$$

<!-- Page 2 -->
$$\text{Next, } x^{(2)} = \begin{pmatrix} x \\ y \end{pmatrix} = (ut + v)e^{\lambda_1 t} = \left[ \begin{pmatrix} u_1 \\ u_2 \end{pmatrix} t + \begin{pmatrix} v_1 \\ v_2 \end{pmatrix} \right] e^{\lambda_1 t}$$

$$\Rightarrow \begin{pmatrix} x \\ y \end{pmatrix} = \begin{pmatrix} (u_1 t + v_1)e^{\lambda_1 t} \\ (u_2 t + v_2)e^{\lambda_1 t} \end{pmatrix}$$

$$\frac{dx}{dt} = \lambda_1(u_1 t + v_1)e^{\lambda_1 t} + u_1 e^{\lambda_1 t}$$

$$\frac{dy}{dt} = \lambda_1(u_2 t + v_2)e^{\lambda_1 t} + u_2 e^{\lambda_1 t}$$

$$a_{11}x + a_{12}y = a_{11}(u_1 t + v_1)e^{\lambda_1 t} + a_{12}(u_2 t + v_2)e^{\lambda_1 t}$$

$$= \left[ (a_{11}u_1 + a_{12}u_2)t + (a_{11}v_1 + a_{12}v_2) \right] e^{\lambda_1 t}$$

$$= \left[ \underbrace{(\lambda_1 u_1)}_{\text{(A)}} t + \underbrace{(u_1 + \lambda_1 v_1)}_{\text{(C)}} \right] e^{\lambda_1 t} \longleftarrow (\text{See below})$$

$$= \lambda_1(u_1 t + v_1)e^{\lambda_1 t} + u_1 e^{\lambda_1 t}$$

$$\left\{ \begin{aligned} &u = (M - \lambda_1 I)v \Rightarrow Mv = u + \lambda_1 v \\ \Rightarrow &\begin{bmatrix} a_{11} & a_{12} \\ a_{21} & a_{22} \end{bmatrix} \begin{bmatrix} v_1 \\ v_2 \end{bmatrix} = \begin{pmatrix} u_1 + \lambda_1 v_1 \\ u_2 + \lambda_2 v_2 \end{pmatrix} \\ \Rightarrow & \begin{aligned} a_{11}v_1 + a_{12}v_2 &= u_1 + \lambda_1 v_1 && -\text{ (C)} \\ a_{21}v_1 + a_{22}v_2 &= u_2 + \lambda_2 v_2 && -\text{ (D)} \end{aligned} \end{aligned} \right\}$$

<!-- Page 3 -->
$$a_{21}x + a_{22}y = a_{21}(u_1 t + v_1)e^{\lambda_1 t} + a_{22}(u_2 t + v_2)e^{\lambda_1 t}$$
$$= \left[ \underbrace{(a_{21}u_1 + a_{22}u_2)}_{\text{(B)}} t + \underbrace{(a_{21}v_1 + a_{22}v_2)}_{\text{(D)}} \right] e^{\lambda_1 t}$$
$$= \left[ \underbrace{(\lambda_1 u_2)}_{\text{(B)}} t + \underbrace{(u_2 + \lambda_1 v_2)}_{\text{(D)}} \right] e^{\lambda_1 t} \longleftarrow (\text{See above})$$
$$= \lambda_1(u_2 t + v_2)e^{\lambda_1 t} + u_2 e^{\lambda_1 t}$$

$$\text{Thus, } x^{(2)} = \begin{pmatrix} x \\ y \end{pmatrix} = (ut + v)e^{\lambda_1 t} \text{ is a solution}$$
$$\text{of the given system.}$$

$$\text{Thus, } \{ u e^{\lambda_1 t}, (ut + v)e^{\lambda_1 t} \} \text{ is a LI solution}$$
$$\text{set for a given set on any interval }[a, b].$$

$$\text{So, the general solution is given by}$$
$$\begin{pmatrix} x \\ y \end{pmatrix} = C_1 u e^{\lambda_1 t} + C_2(ut + v)e^{\lambda_1 t}$$
$$\text{on any interval }[a, b] \text{, where } C_1 \text{ and } C_2$$
$$\text{are arbitrary real constants.}$$

<!-- Page 1 -->
Example: Find the general solution of the homogeneous linear system
$$\frac{dx}{dt} = 4x - y, \quad \frac{dy}{dt} = x + 2y$$

Solution: $M = \begin{pmatrix} 4 & -1 \\ 1 & 2 \end{pmatrix}$

The characteristic equation is given by
$$\det(M - \lambda I) = 0$$
$$\begin{vmatrix} 4-\lambda & -1 \\ 1 & 2-\lambda \end{vmatrix} = 0$$

$$\Rightarrow (\lambda-2)(\lambda-4) + 1 = 0$$
$$\Rightarrow \lambda^2 - 6\lambda + 9 = 0$$
$$\Rightarrow (\lambda-3)^2 = 0, \quad \lambda_1 = \lambda_2 = 3 \text{ (Double Repeated Roots)}$$

First, we find the $\dim(\text{null space of } (M-\lambda_1 I))$
For that, we calculate the $\text{rank}(M-\lambda_1 I), (\lambda_1 = 3)$

$$M - 3I = \begin{pmatrix} 1 & -1 \\ 1 & -1 \end{pmatrix} \sim \begin{pmatrix} 1 & -1 \\ 0 & 0 \end{pmatrix}$$

So, $\text{rank}(M-3I) = 1$.
By Rank-Nullity theorem
$$\text{rank}(M-3I) + \text{nullity}(M-3I) = 2$$
$$1 + \text{nullity}(M-3I) = 2$$
$$\text{nullity}(M-3I) = 1$$
Thus, $\dim(\text{null space of } (M-3I)) = 1$

<!-- Page 2 -->
First, we find the eigenvector $u$ for the matrix $M$ corresponding to the eigenvalue $\lambda_1 = 3$.
$$M u = \lambda_1 u$$
$$\begin{pmatrix} 4 & -1 \\ 1 & 2 \end{pmatrix} \begin{pmatrix} u_1 \\ u_2 \end{pmatrix} = 3 \begin{pmatrix} u_1 \\ u_2 \end{pmatrix}$$
$$\left. \begin{aligned} 4u_1 - u_2 &= 3u_1 \\ u_1 + 2u_2 &= 3u_2 \end{aligned} \right\} \Rightarrow \begin{aligned} u_1 - u_2 &= 0 \\ u_1 - u_2 &= 0 \end{aligned}$$

Choose $u_1 = u_2 = 1$, then $u = \begin{pmatrix} 1 \\ 1 \end{pmatrix}$ is an eigenvector.

Now, we find a vector $v \in \mathbb{R}^2$ st
$$(M - 3I) v = u$$
$$\begin{pmatrix} 1 & -1 \\ 1 & -1 \end{pmatrix} \begin{pmatrix} v_1 \\ v_2 \end{pmatrix} = \begin{pmatrix} 1 \\ 1 \end{pmatrix}$$
$$\left. \begin{aligned} v_1 - v_2 &= 1 \\ v_1 - v_2 &= 1 \end{aligned} \right\} \Rightarrow v_1 - v_2 = 1$$

Choose $v_1 = 3, \ v_2 = 2$.
Now, $\{u e^{\lambda_1 t}, (ut + v) e^{\lambda_1 t}\}$ forms a linearly independent solution set for the given system, and the general solution on any interval $[a, b]$ is given by

$$\begin{pmatrix} x \\ y \end{pmatrix} = c_1 \begin{pmatrix} 1 \\ 1 \end{pmatrix} e^{3t} + c_2 \left( \begin{pmatrix} 1 \\ 1 \end{pmatrix} t + \begin{pmatrix} 3 \\ 2 \end{pmatrix} \right) e^{3t}$$

<!-- Page 3 -->
$$\Rightarrow \begin{aligned} x &= c_1 e^{3t} + c_2 (t+3) e^{3t} \\ y &= c_1 e^{3t} + c_2 (t+2) e^{3t} \end{aligned}$$

Where $c_1$ and $c_2$ are arbitrary constants.

<!-- Page 1 -->
# Non Homogeneous System of Equations

Consider the non homogeneous system of equations:

$$\left.\begin{aligned}
\frac{dx_1}{dt} &= a_{11}x_1 + a_{12}x_2 + F_1(t) \\
\frac{dx_2}{dt} &= a_{21}x_1 + a_{22}x_2 + F_2(t)
\end{aligned}\right\} \quad \text{— (1)}$$

An equivalent matrix form can be written as

$$\frac{dX}{dt} = M X + F, \quad M = \begin{bmatrix} a_{11} & a_{12} \\ a_{21} & a_{22} \end{bmatrix}, \quad F(t) = \begin{bmatrix} F_1(t) \\ F_2(t) \end{bmatrix}$$

Let the general solution of the homogeneous system be

$$X(t) = C_1 X_1(t) + C_2 X_2(t), \quad \text{where } \begin{aligned} X_1(t) &= \begin{bmatrix} x_{11}(t) \\ x_{12}(t) \end{bmatrix}, \\ X_2(t) &= \begin{bmatrix} x_{21}(t) \\ x_{22}(t) \end{bmatrix} \end{aligned}$$

Consider the particular solution (1) as follows:

$$X_p(t) = v_1(t) X_1(t) + v_2(t) X_2(t) \quad \text{— (2)}$$

$$\Big\Vert \left[ X_1(t), X_2(t) \right] \begin{bmatrix} v_1(t) \\ v_2(t) \end{bmatrix}$$

$$X_p'(t) = v_1'(t) X_1(t) + v_2'(t) X_2(t) + v_1(t) X_1'(t) + v_2(t) X_2'(t) \quad \text{— (3)}$$

---

<!-- Page 2 -->

Substitute (2) and (3) in (1), we have

$$X_p'(t) - M X_p(t) - F(t) = v_1'(t) X_1(t) + v_2'(t) X_2(t) + v_1(t) X_1'(t) + v_2(t) X_2'(t) - M \left( v_1(t) X_1(t) + v_2(t) X_2(t) \right) - F(t) = 0$$

$$\Rightarrow v_1'(t) X_1(t) + v_2'(t) X_2(t) + v_1(t) \overbrace{\left( X_1'(t) - M X_1(t) \right)}^{\substack{=0}} + v_2(t) \overbrace{\left( X_2'(t) - M X_2(t) \right)}^{\substack{=0}} - F(t) = 0$$

$$\Rightarrow v_1'(t) X_1(t) + v_2'(t) X_2(t) = F(t)$$

$$\Rightarrow v_1'(t) \begin{bmatrix} x_{11}(t) \\ x_{12}(t) \end{bmatrix} + v_2'(t) \begin{bmatrix} x_{21}(t) \\ x_{22}(t) \end{bmatrix} = \begin{bmatrix} F_1(t) \\ F_2(t) \end{bmatrix}$$

$$\Rightarrow \overbrace{\begin{bmatrix} x_{11}(t) & x_{21}(t) \\ x_{12}(t) & x_{22}(t) \end{bmatrix}}^{\text{say } \Phi(t)} \begin{bmatrix} v_1'(t) \\ v_2'(t) \end{bmatrix} = \begin{bmatrix} F_1(t) \\ F_2(t) \end{bmatrix}$$

$$\Rightarrow \begin{bmatrix} v_1'(t) \\ v_2'(t) \end{bmatrix} = \underbrace{\begin{bmatrix} x_{11}(t) & x_{21}(t) \\ x_{12}(t) & x_{22}(t) \end{bmatrix}^{-1}}_{\Phi^{-1}(t)} \begin{bmatrix} F_1(t) \\ F_2(t) \end{bmatrix}$$

$$\begin{bmatrix} v_1(t) \\ v_2(t) \end{bmatrix} = \int \underbrace{\begin{bmatrix} x_{11}(t) & x_{21}(t) \\ x_{12}(t) & x_{22}(t) \end{bmatrix}^{-1}}_{X_1(t) \quad X_2(t)} \begin{bmatrix} F_1(t) \\ F_2(t) \end{bmatrix} dt \quad \text{— } \circledast$$

---

<!-- Page 3 -->

$$\Rightarrow X_p(t) = \underbrace{\begin{bmatrix} X_1(t) & X_2(t) \end{bmatrix}}_{\Phi(t)} \underbrace{\begin{bmatrix} v_1(t) \\ v_2(t) \end{bmatrix}}_{\text{use } \circledast} = \begin{bmatrix} x_{11}(t) & x_{21}(t) \\ x_{12}(t) & x_{22}(t) \end{bmatrix}$$

$$X_p(t) = \begin{bmatrix} X_1(t) & X_2(t) \end{bmatrix} \int \begin{bmatrix} X_1(t) & X_2(t) \end{bmatrix}^{-1} F(t) dt$$

The general solution is given by

$$X(t) = \Phi(t) \underbrace{C}_{\begin{bmatrix} c_1 \\ c_2 \end{bmatrix}} + \underbrace{\Phi(t) \int \Phi^{-1}(t) F(t) dt}_{X_p(t)}$$

