---
course: "differential equations"
source_file: "MA301 Lecture 15 notes.pdf"
tags: ["math", "coursework", "differential-equations"]
---

# MA301 Lecture 15 notes

<!-- Page 1 -->
$$\underline{\text{Lecture}-15}$$
$$\text{Picard's / Peano's theorem for first order ODE}$$

$\underline{\text{Theorem}}$: Let $f(x,y)$ be a continuous function defined on a rectangle $R$ with the center $(x_0,y_0)$;
$$R = \{|x-x_0|\le a,\ |y-y_0|\le b\}.$$

Let $M = \max_R |f(x,y)|$ and $\alpha = \min\left\{a, \frac{b}{M}\right\}$.

Then, the IVP $\quad y'=f(x,y),\ y(x_0)=y_0$

- (Peano) has at least one solution $y(x)$ defined for all $x$ in the interval
$$I_\alpha[x_0] = \{x: |x-x_0|<\alpha\}.$$

- (Picard) Further if $f$ satisfies the $y$-Lipschitz condition in $R$, i.e.
$$|f(x,y_1)-f(x,y_2)| \le L|y_1-y_2|,$$
then the solution is unique.

<!-- Page 2 -->
$$\text{Illustration of the theorem statement by examples}$$

$\underline{\text{Example}}$: Consider the ODE $y'=1+y^2,\ y(0)=0.$

Consider the rectangle $R = \{(x,y)\in\mathbb{R}^2:\ |x|\le 100,\ |y|\le 1\}$
$$\begin{aligned}
&|x-0|\le 100,\ x_0=0 \\
&|y-0|\le 1,\ y_0=0
\end{aligned}$$

(i) $f$ is continuous in $R$.

(ii) Boundedness of $f$ on rectangle:
$$\begin{aligned}
\text{Here,}\quad f(x,y) &= 1+y^2 \\
|f(x,y)| &= |1+y^2| \\
&= 1+y^2 \le \underbrace{2}_{M}\quad \forall (x,y)\in R
\end{aligned}$$

(iii) Lipschitz continuity of $f$ with respect to $y$:

$$\begin{aligned}
\text{For }(x,y_1), (x,y_2) &\in R,\ \text{we have} \\
|f(x,y_1)-f(x,y_2)| &= |1+y_1^2 - 1 - y_2^2| \\
&= |y_1^2 - y_2^2| \\
&= |y_1+y_2|\ |y_1-y_2| \\
&\le \underbrace{2}_{L}\ |y_1-y_2|
\end{aligned}$$

The assumptions of the Picard's and Peano's theorem are satisfied, hence there exists a unique solution in the neighbourhood of $x_0=0$.

<!-- Page 3 -->
Since, the rectangle is specified, we can find $M=2$ and $\alpha = \min\{100, 1/2\} = 1/2$. So by the theorem, the solution exists for all $x\in(-1/2, 1/2)$.

But, in this example we can explicitly find out the solution $y(x)=\tan x$.

This solution is valid in the interval $(-\frac{\pi}{2}, \frac{\pi}{2})$ which is much bigger than $(-1/2, 1/2)$.

$$\alpha = \frac{1}{2},\ (x_0,y_0)=(0,0)$$

<!-- Page 1 -->
Illustration of the theorem statement:

Example: Consider the ODE $y' = x^2 + y^2$, $y(0) = 1$.
Here $f(x,y) = x^2 + y^2$ which is continuous and $y$-Lipschitz in any rectangle around the point $(x_0, y_0) = (0,1)$. Thus, the assumptions of Peano's theorem and Picard's theorem are applicable and hence there exists a unique solution $y(x)$ when $|x| < \alpha$. Note that $\alpha$ depends on the dimension of the rectangle we choose.

Example: Consider the ODE $y' = 1 + y^2$, $y(0) = 0$.

Consider the rectangle $R = \{(x,y) : |x| \le 100, |y| \le 1\}$.
Again the assumptions of the Picard's/Peano's theorem are satisfied, hence there exists a unique solution in the neighbourhood of $x_0 = 0$.
Since, the rectangle is specified, we can find $M=2$ and $\alpha = \min\{100, \frac{1}{2}\} = \frac{1}{2}$. So, by the theorem, the solution exists when $x \in (-\frac{1}{2}, \frac{1}{2})$.

But, in this example we can explicitly find out the solution $y(x) = \tan x$.

<!-- Page 2 -->
This solution is valid in the interval $(-\frac{\pi}{2}, \frac{\pi}{2})$ which is much bigger than $(-\frac{1}{2}, \frac{1}{2})$.

<!-- Page 3 -->
Example: Find all the solutions to the initial value problem
$$y' = \sin y; \quad y(0) = 0.$$

Answer: $y(x) \equiv 0$ is the only solution by Picard's theorem.

More examples: Illustration of Peano's/Picard's theorem:

Consider the IVP $\frac{dy}{dx} = x + |\sin y|$, $y(0) = \frac{\pi}{2}$.

Here $(x_0, y_0) = (0, \frac{\pi}{2})$ and $f(x,y) = x + |\sin y|$.
Clearly, $f$ is continuous on any rectangle
$$R = [-a, a] \times [\frac{\pi}{2} - b, \frac{\pi}{2} + b]$$
around the initial condition $(0, \frac{\pi}{2})$.
$$M = \max_R |f(x,y)| = |a+1| \quad \begin{aligned} \because \quad &|x| \le a \\ &|\sin y| \le 1 \end{aligned}$$

Now, by Peano's theorem IVP admits a solution in the interval $I_\alpha(x_0) = (-\alpha, \alpha)$, where
$$\alpha = \min\left\{a, \frac{b}{a+1}\right\}$$

<!-- Page 1 -->
It is left as an easy exercise to verify that the function $f(x,y)$ is Lipschitz in any rectangle around $(0,\frac{\pi}{2})$ and hence the solution is unique.

$$\underline{\text{Example:}}$$ Consider the IVP $y' = y^{2/3}, y(0)=0$ in $R = \{|x| \le a, |y| \le b\}$. Hence, $f(x,y)=y^{2/3}$ is continuous in $R$ and so Peano's theorem assures the existence of at least one solution. But, note that $y^{2/3}$ is not $y$-Lipschitz (!) and the assumption of Picard's theorem is not satisfied, so we cannot conclude if the uniqueness is true or not. But, we can construct a family of solutions
$$y_k(x) = \begin{cases} \dfrac{(x-k)^3}{27} & \text{if } x \ge k \\ 0 & \text{if } x \le k \end{cases}$$
which solves the IVP in $\mathbb{R}$. Hence no uniqueness.

<!-- Page 2 -->
$$\underline{\text{Exercise:}}$$ Consider the ODE $y' = y^{2/3}, y(0)=1$. Discuss if Picard's theorem is applicable or not here.

$$\underline{\text{First fundamental theorem of Calculus:}}$$

Let $f$ be continuous on $[a,b]$. For $x \in [a,b]$, define
$$F(x) := \int_a^x f(t) \, dt.$$

Then, $F$ is differentiable on $[a,b]$ and $F'(x) = f(x)$ for all $x \in [a,b]$.

<!-- Page 3 -->
$$\underline{\text{Outline of the proof:}}$$ Our aim is to solve the ($\text{Existence part}$) IVP:
$$y' = f(x,y), \quad y(x_0) = y_0 . \quad \text{---} \, \textcircled{1}$$

Suppose there exists a solution $y(x)$ for $\textcircled{1}$, then integrating on both sides, we obtain
$$y(x) = y_0 + \int_{x_0}^x f(t,y(t)) \, dt . \quad \text{---} \, \textcircled{2}$$

Now conversely suppose that $y$ is a continuous function and $y$ satisfies the integral identity given in $\textcircled{2}$. Then we can show that $y$ is a solution for the IVP $\textcircled{1}$. Only step involved here is to find $\dfrac{d}{dx} \int_{x_0}^x f(t,y(t)) \, dt$. If we define $g(t) = f(t,y(t))$. Then, the function $g$ is continuous since $f$ and $y$ are continuous. Now by the first fundamental theorem of Calculus, we have
$$\boxed{\frac{d}{dx} \int_{x_0}^x f(t,y(t)) \, dt = f(x,y(x)) .}$$

