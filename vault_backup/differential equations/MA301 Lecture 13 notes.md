---
course: "differential equations"
source_file: "MA301 Lecture 13 notes.pdf"
tags: ["math", "coursework", "differential-equations"]
---

# MA301 Lecture 13 notes

<!-- Page 1 -->
$$\text{Lecture } 13$$

$$\text{Non Homogeneous System of Equations}$$

$$\text{Consider the non homogeneous system of equations:}$$

$$\left.\begin{aligned}
\frac{dx_1}{dt} &= a_{11}x_1 + a_{12}x_2 + F_1(t) \\
\frac{dx_2}{dt} &= a_{21}x_1 + a_{22}x_2 + F_2(t)
\end{aligned}\right\} \text{--- (1)}$$

$$\text{An equivalent matrix form can be written as}$$

$$\frac{dX}{dt} = M X + F, \quad M = \begin{bmatrix} a_{11} & a_{12} \\ a_{21} & a_{22} \end{bmatrix}, \quad F(t) = \begin{bmatrix} F_1(t) \\ F_2(t) \end{bmatrix}, \quad X = \begin{bmatrix} x_1 \\ x_2 \end{bmatrix}$$

$$\text{Let the general solution of the homogeneous system be}$$

$$X_h(t) = C_1 X_1(t) + C_2 X_2(t), \quad \text{where} \quad \begin{aligned} X_1(t) &= \begin{bmatrix} x_{11}(t) \\ x_{12}(t) \end{bmatrix}, \\ X_2(t) &= \begin{bmatrix} x_{21}(t) \\ x_{22}(t) \end{bmatrix} \end{aligned}$$

$$\text{Consider the particular solution (1) [Note: it is (1)] as follows:}$$

$$X_p(t) = v_1(t) X_1(t) + v_2(t) X_2(t) \text{--- (2)}$$
$$\underbrace{\qquad \qquad \qquad [X_1(t), X_2(t)] \begin{bmatrix} v_1(t) \\ v_2(t) \end{bmatrix} \qquad \qquad \qquad}_{||}$$

$$X_p'(t) = v_1'(t) X_1(t) + v_2'(t) X_2(t) + v_1(t) X_1'(t) + v_2(t) X_2'(t) \text{--- (3)}$$

---

<!-- Page 2 -->
$$\text{Substitute (2) and (3) in (1), we have}$$

$$X_p'(t) - M X_p(t) - F(t) = v_1'(t) X_1(t) + v_2'(t) X_2(t) + v_1(t) X_1'(t) + v_2(t) X_2'(t) - M(v_1(t)X_1(t) + v_2(t)X_2(t)) - F(t) = 0$$

$$\Rightarrow v_1'(t) X_1(t) + v_2'(t) X_2(t) + v_1(t) \underbrace{(X_1'(t) - M X_1(t))}_{= 0} + v_2(t) \underbrace{(X_2'(t) - M X_2(t))}_{= 0} - F(t) = 0$$

$$\Rightarrow v_1'(t) X_1(t) + v_2'(t) X_2(t) = F(t)$$

$$\Rightarrow v_1'(t) \begin{bmatrix} x_{11}(t) \\ x_{12}(t) \end{bmatrix} + v_2'(t) \begin{bmatrix} x_{21}(t) \\ x_{22}(t) \end{bmatrix} = \begin{bmatrix} F_1(t) \\ F_2(t) \end{bmatrix}$$

$$\Rightarrow \underbrace{\begin{bmatrix} x_{11}(t) & x_{21}(t) \\ x_{12}(t) & x_{22}(t) \end{bmatrix}}_{\Phi(t)} \begin{bmatrix} v_1'(t) \\ v_2'(t) \end{bmatrix} = \begin{bmatrix} F_1(t) \\ F_2(t) \end{bmatrix}$$

$$\begin{bmatrix} v_1'(t) \\ v_2'(t) \end{bmatrix} = \underbrace{\begin{bmatrix} x_{11}(t) & x_{21}(t) \\ x_{12}(t) & x_{22}(t) \end{bmatrix}^{-1}}_{\Phi^{-1}(t)} \begin{bmatrix} F_1(t) \\ F_2(t) \end{bmatrix}$$

$$\begin{bmatrix} v_1(t) \\ v_2(t) \end{bmatrix} = \int \underbrace{\begin{bmatrix} x_{11}(t) & x_{21}(t) \\ x_{12}(t) & x_{22}(t) \end{bmatrix}^{-1}}_{[X_1(t) \quad X_2(t)]^{-1}} \begin{bmatrix} F_1(t) \\ F_2(t) \end{bmatrix} dt \text{--- (*)}$$

---

<!-- Page 3 -->
$$\Rightarrow X_p(t) = \underbrace{\begin{bmatrix} X_1(t) & X_2(t) \end{bmatrix}}_{||} \begin{bmatrix} v_1(t) \\ v_2(t) \end{bmatrix}$$

$$\underbrace{\begin{bmatrix} x_{11}(t) & x_{21}(t) \\ x_{12}(t) & x_{22}(t) \end{bmatrix}}_{\Phi(t)} \quad \text{use } (*)$$

$$X_p(t) = \begin{bmatrix} X_1(t) & X_2(t) \end{bmatrix} \int \begin{bmatrix} X_1(t) & X_2(t) \end{bmatrix}^{-1} F(t) dt$$

$$\text{The general solution is given by}$$

$$X(t) = \underbrace{\Phi(t) \underbrace{C}_{\begin{bmatrix} C_1 \\ C_2 \end{bmatrix}}}_{X_h(t)} + \underbrace{\Phi(t) \int \Phi^{-1}(t) F(t) dt}_{X_p(t)}$$

<!-- Page 1 -->
Remark:
Using matrix form of the system another approach is as follows:

Consider $U(t) = \begin{bmatrix} u_1(t) \\ u_2(t) \end{bmatrix}$, $\phi(t) = \begin{bmatrix} x_{11} & x_{21} \\ x_{12} & x_{22} \end{bmatrix}$

$$X_p(t) = \phi(t) \, U(t)$$
(Fundamental matrix)

Substitute $X' = M X + F(t)$
$$X_p'(t) = \phi(t) U'(t) + \phi'(t) U(t)$$

$$\phi(t) U'(t) + \phi'(t) U(t) = M \phi(t) U(t) + F(t)$$
$$\phi(t) U'(t) + \underbrace{(\phi'(t) - M \phi(t))}_{= 0} U(t) = F(t)$$

$\Rightarrow \phi(t) U'(t) = F(t)$

$\Rightarrow U'(t) = \phi^{-1}(t) F(t)$

$\Rightarrow U(t) = \int \phi^{-1}(t) F(t) \, dt$

$$X_p(t) = \phi(t) \int \phi^{-1}(t) F(t) \, dt.$$

The general solution is given by

$$X = \underbrace{\phi(t) C}_{X_h(t)} + \underbrace{\phi(t) \int \phi^{-1}(t) F(t) \, dt}_{X_p(t)}$$

---

<!-- Page 2 -->
Example:
$$\text{Solve the system } X' = \begin{pmatrix} -3 & 1 \\ 2 & -4 \end{pmatrix} X + \begin{pmatrix} 3t \\ e^{-t} \end{pmatrix}.$$

Solution:
Two linearly independent solutions are
$$X_1(t) = \begin{pmatrix} 1 \\ 1 \end{pmatrix} e^{-2t} = \begin{pmatrix} e^{-2t} \\ e^{-2t} \end{pmatrix}, \quad X_2(t) = \begin{pmatrix} 1 \\ -2 \end{pmatrix} e^{-5t} = \begin{pmatrix} e^{-5t} \\ -2e^{-5t} \end{pmatrix}$$

$$\phi(t) = \begin{bmatrix} e^{-2t} & e^{-5t} \\ e^{-2t} & -2e^{-5t} \end{bmatrix}, \quad \phi^{-1}(t) = \begin{pmatrix} \frac{2}{3}e^{2t} & \frac{1}{3}e^{2t} \\ \frac{1}{3}e^{5t} & -\frac{1}{3}e^{5t} \end{pmatrix} \quad (\text{Verify}!)$$

$$X_p(t) = \phi(t) \int \phi^{-1}(t) F(t) \, dt$$
$$= \begin{bmatrix} e^{-2t} & e^{-5t} \\ e^{-2t} & -2e^{-5t} \end{bmatrix} \int \left( \begin{pmatrix} \frac{2}{3}e^{2t} & \frac{1}{3}e^{2t} \\ \frac{1}{3}e^{5t} & -\frac{1}{3}e^{5t} \end{pmatrix} \begin{pmatrix} 3t \\ e^{-t} \end{pmatrix} \right) dt$$

$$= \begin{pmatrix} \frac{6}{5}t - \frac{27}{50} + \frac{1}{4}e^{-t} \\ \frac{3}{5}t - \frac{21}{50} + \frac{1}{2}e^{-t} \end{pmatrix} \quad (\text{Verify}!)$$

---

<!-- Page 3 -->
The general solution is

$$X(t) = \begin{pmatrix} e^{-2t} & e^{-5t} \\ e^{-2t} & -2e^{-5t} \end{pmatrix} \begin{pmatrix} C_1 \\ C_2 \end{pmatrix} + \begin{pmatrix} \frac{6}{5}t - \frac{27}{50} + \frac{1}{4}e^{-t} \\ \frac{3}{5}t - \frac{21}{50} + \frac{1}{2}e^{-t} \end{pmatrix}$$
$$= C_1 \begin{pmatrix} 1 \\ 1 \end{pmatrix} e^{-2t} + C_2 \begin{pmatrix} 1 \\ -2 \end{pmatrix} e^{-5t} + \begin{pmatrix} \frac{6}{5} \\ \frac{3}{5} \end{pmatrix} t - \begin{pmatrix} \frac{27}{50} \\ \frac{21}{50} \end{pmatrix} + \begin{pmatrix} \frac{1}{4} \\ \frac{1}{2} \end{pmatrix} e^{-t}$$

Exercise:
Solve the following systems using the method of variation of parameters:

1)
$$X' = \begin{bmatrix} 1 & 3 \\ 3 & 1 \end{bmatrix} X + \begin{bmatrix} -2t^2 \\ t + 5 \end{bmatrix}$$

Answer:
$$X(t) = C_1 \begin{pmatrix} 1 \\ 1 \end{pmatrix} e^{-2t} + C_2 \begin{pmatrix} 1 \\ -1 \end{pmatrix} e^{4t} + \begin{pmatrix} -1/4 \\ 3/4 \end{pmatrix} t^2 + \begin{pmatrix} 1/4 \\ -1/4 \end{pmatrix} t + \begin{pmatrix} -2 \\ 3/4 \end{pmatrix}$$

2)
$$X' = \begin{pmatrix} 4 & 1/3 \\ 9 & 6 \end{pmatrix} X + \begin{pmatrix} -3 \\ 10 \end{pmatrix} e^t$$

Answer:
$$X(t) = C_1 \begin{pmatrix} 1 \\ -3 \end{pmatrix} e^{3t} + C_2 \begin{pmatrix} 1 \\ 9 \end{pmatrix} e^{7t} + \begin{pmatrix} \frac{55}{36} \\ -\frac{19}{4} \end{pmatrix} e^t$$

<!-- Page 1 -->
# Method of Undeterminant Coefficients

**Example:** Solve the system
$$X' = \begin{bmatrix} 6 & 1 \\ 4 & 3 \end{bmatrix} X + \begin{bmatrix} 6t \\ -10t+4 \end{bmatrix} \quad \text{--- (1)}$$

**Solution:**
The eigenvalues and corresponding eigenvectors of the associated homogeneous system are
$$\lambda_1 = 2, \quad \lambda_2 = 7 \quad \text{and}$$

$$v_1 = \begin{pmatrix} 1 \\ -4 \end{pmatrix}, \quad v_2 = \begin{pmatrix} 1 \\ 1 \end{pmatrix}$$

$$X_h(t) = c_1 \begin{pmatrix} 1 \\ -4 \end{pmatrix} e^{2t} + c_2 \begin{pmatrix} 1 \\ 1 \end{pmatrix} e^{7t}$$

Now, $F(t)$ can be written as
$$F(t) = \begin{bmatrix} 6 \\ -10 \end{bmatrix} t + \begin{bmatrix} 0 \\ 4 \end{bmatrix}.$$

We will try a solution of the form:
$$X_p(t) = \begin{bmatrix} A_2 \\ B_2 \end{bmatrix} t + \begin{bmatrix} A_1 \\ B_1 \end{bmatrix} \quad \text{--- (2)}$$

<!-- Page 2 -->
$$X_p'(t) = \begin{bmatrix} A_2 \\ B_2 \end{bmatrix} \quad \text{--- (3)}$$

Substituting (2) and (3) in (1), we have

$$\begin{bmatrix} A_2 \\ B_2 \end{bmatrix} = \begin{bmatrix} 6 & 1 \\ 4 & 3 \end{bmatrix} \left( \begin{bmatrix} A_2 \\ B_2 \end{bmatrix} t + \begin{bmatrix} A_1 \\ B_1 \end{bmatrix} \right) + \begin{bmatrix} 6 \\ -10 \end{bmatrix} t + \begin{bmatrix} 0 \\ 4 \end{bmatrix}$$

$$\begin{bmatrix} 0 \\ 0 \end{bmatrix} = \begin{bmatrix} (6A_2 + B_2 + 6)t + (6A_1 + B_1) - A_2 \\ (4A_2 + 3B_2 - 10)t + 4A_1 + 3B_1 - B_2 + 4 \end{bmatrix}$$

Comparing powers of '$t$' on both sides, we have

$$\begin{aligned}
6A_2 + B_2 + 6 &= 0 \quad \text{and} & 6A_1 + B_1 - A_2 &= 0 \\
4A_2 + 3B_2 - 10 &= 0 & 4A_1 + 3B_1 - B_2 + 4 &= 0
\end{aligned}$$

Solving the first two equations, we obtain $A_2 = -2, \, B_2 = 6$.

Similarly, the last two equations yield $A_1 = -\frac{4}{7}, \, B_1 = \frac{10}{7}$.

Therefore, $X_p = \begin{bmatrix} -2 \\ 6 \end{bmatrix} t + \begin{bmatrix} -4/7 \\ 10/7 \end{bmatrix}$.

<!-- Page 3 -->
The general solution is given by
$$X = X_h + X_p = \underbrace{c_1 \begin{pmatrix} 1 \\ -4 \end{pmatrix} e^{2t} + c_2 \begin{pmatrix} 1 \\ 1 \end{pmatrix} e^{7t}}_{X_h(t)} + \underbrace{\begin{bmatrix} -2 \\ 6 \end{bmatrix} t + \begin{bmatrix} -4/7 \\ 10/7 \end{bmatrix}}_{X_p(t)}$$

**Example:** Solve the system
$$X' = \begin{pmatrix} -1 & 2 \\ -1 & 1 \end{pmatrix} X + \begin{pmatrix} -8 \\ 3 \end{pmatrix}$$

**Solution:**
The characteristic equation for associated homogeneous system

$$\det(M - \lambda I) = \begin{vmatrix} -1 - \lambda & 2 \\ -1 & 1 - \lambda \end{vmatrix} = \lambda^2 + 1 = 0 \implies \lambda = \pm i$$

General Real valued solution:
$$X_h(t) = c_1 \begin{bmatrix} \cos t + \sin t \\ \cos t \end{bmatrix} + c_2 \begin{bmatrix} \cos t - \sin t \\ -\sin t \end{bmatrix}$$

<!-- Page 1 -->
Since $F(t)$ is a constant vector, we assume a particular solution as
$$X_p(t) = \begin{bmatrix} A_1 \\ B_1 \end{bmatrix}, \quad X_p'(t) = 0$$

Substituting in the equation, we obtain
$$ \left. \begin{array}{l} 0 = -A_1 + 2B_1 - 8 \\ 0 = -A_1 + B_1 + 3 \end{array} \right\} \Rightarrow \begin{array}{l} A_1 = 14 \\ B_1 = 11 \end{array} $$

Therefore, $X_p(t) = \begin{bmatrix} 14 \\ 11 \end{bmatrix}$

Hence, the general solution is
$$X = c_1 \begin{bmatrix} \cos t + \sin t \\ \cos t \end{bmatrix} + c_2 \begin{bmatrix} \cos t - \sin t \\ -\sin t \end{bmatrix} + \begin{bmatrix} 14 \\ 11 \end{bmatrix}$$

<u>Example</u>: Find the particular solution $X_p(t)$ for the system
$$ \begin{cases} \frac{dx}{dt} = 5x + 3y - 2e^{-t+1} \\ \frac{dy}{dt} = -x + y + e^{-t} - 5t + 7 \end{cases} $$

---

<!-- Page 2 -->
Solution: $\text{Hint:}$ Here $F(t) = \binom{-2}{1} e^{-t} + \binom{0}{-5} t + \binom{1}{7}$

Consider a particular solution of the form:
$$X_p(t) = \binom{A_3}{B_3} e^{-t} + \binom{A_2}{B_2} t + \binom{A_1}{B_1}$$

$\text{Complete!}$

<u>Exercise</u>: 1) Use the method of undetermined coefficients to solve:
$$ \begin{cases} \frac{dx}{dt} = 2x + 3y - 7 \\ \frac{dy}{dt} = -x - 2y + 5 \end{cases}, \text{ Choose } X_p(t) = \begin{bmatrix} A_1 \\ B_1 \end{bmatrix} $$

2) $x' = \begin{bmatrix} 1 & 3 \\ 3 & 1 \end{bmatrix} X + \binom{-2t^2}{t+5}$

3) $\frac{dx}{dt} = 5x + 9y + 2, \quad \frac{dy}{dt} = -x + 11y + 6$

4) $x' = \begin{pmatrix} 1 & -4 \\ 4 & 1 \end{pmatrix} X + \binom{4t + 9e^{6t}}{-t + e^{6t}}$

