---
course: "differential equations"
source_file: "Lecture notes 10 to 15.pdf"
tags: ["math", "coursework", "differential-equations"]
---

# Lecture notes 10 to 15

<!-- Page 1 -->

## Lecture - 10

**Recall:** <u>Lipschitz condition</u>: Let $f$ be defined on an interval $I$. The function $f$ is said to satisfy Lipschitz condition on $I$ if $\exists$ a constant $L > 0$ such that
$$\lvert f(t_1) - f(t_2) \rvert \le L \lvert t_1 - t_2 \rvert \quad \forall\ t_1, t_2 \in I.$$

### Examples:
(1) Using mean value theorem, we can see that if $f$ is differentiable and the derivative is bounded in some interval $I$, then $f$ is Lipschitz continuous on $I$.

(2) $\sin t$, $\cos t$, $e^t$ etc are Lipschitz in any closed and bounded interval $[a,b]$.

(3) $f(t) = \lvert t \rvert$ is Lipschitz continuous on $[-1,1]$ by triangle inequality but not differentiable.

(4) Lipschitz continuous function must be continuous. (Verify)

(5) $f(t) = \sqrt{t}$ is continuous but not Lipschitz continuous in $[0,1]$.

---

<!-- Page 2 -->

**Solution:** Show that $f(t) = \sqrt{t}$ is continuous in $[0,1]$.
Here, we will show that $f(t)$ is not Lipschitz continuous.
Consider $f(t) = \sqrt{t}$

$$\frac{\lvert f(t_1) - f(t_2) \rvert}{t_1 - t_2} = \frac{\sqrt{t_1} - \sqrt{t_2}}{t_1 - t_2}$$

choose $t_2 = 0$, we have

$$\frac{\lvert f(t_1) - f(0) \rvert}{\lvert t_1 - 0 \rvert} = \frac{\sqrt{t_1}}{t_1} = \frac{1}{\sqrt{t_1}} \to \infty \quad \text{as } t_1 \to 0.$$

Here, $f$ is continuous but not Lipschitz continuous.

(6) The function $f(t) = t^2$ is Lipschitz in $[1,2]$,

$$\begin{aligned}
\lvert f(t_1) - f(t_2) \rvert &= \lvert t_1^2 - t_2^2 \rvert = \lvert t_1 + t_2 \rvert \lvert t_1 - t_2 \rvert \\
&\le \left( \max_{t \in [1,2]} \lvert t_1 + t_2 \rvert \right) \lvert t_1 - t_2 \rvert \\
&\le 4 \lvert t_1 - t_2 \rvert
\end{aligned}$$

Therefore, $f$ is Lipschitz continuous on $[1,2]$.

**Definition:** Let $f$ be defined on a domain $D \subseteq \mathbb{R}^2$. The function $f$ is said to satisfy $y$-Lipschitz condition in $D$ if $\exists$ a constant $L > 0$ such that
$$\lvert f(x, y_1) - f(x, y_2) \rvert \le L \lvert y_1 - y_2 \rvert \quad \forall\ (x, y_1), (x, y_2) \in D.$$

---

<!-- Page 3 -->

### Examples:
Consider $f(x,y) = x \lvert y \rvert$,
$$(x,y) \in D = \{ \lvert x \rvert \le a,\ \lvert y \rvert \le b \}.$$

For any $(x, y_1), (x, y_2) \in D$, we have

$$\begin{aligned}
\lvert f(x, y_1) - f(x, y_2) \rvert &= \lvert x \lvert y_1 \rvert - x \lvert y_2 \rvert \rvert \\
&= \lvert x (\lvert y_1 \rvert - \lvert y_2 \rvert) \rvert \le \lvert x \rvert \big\lvert \lvert y_1 \rvert - \lvert y_2 \rvert \big\rvert \\
&\le \lvert x \rvert \lvert y_1 - y_2 \rvert \le a \lvert y_1 - y_2 \rvert.
\end{aligned}$$

Therefore, $f$ is $y$-Lipschitz continuous on $D$.

---

**Problem:** If $y_1$ and $y_2$ are two solutions to the differential equation $y_i' + y_i = b_i(x)$ for $i=1,2$, show that $y_1 + y_2$ solves $y' + y = b_1 + b_2$. Use this idea to solve $y' + y = \sin x + \cos 2x$.

**Solution:** Given that $y_1$ solves $y' + y = b_1(x)$ and $y_2$ solves $y' + y = b_2(x)$. $\quad (*)$

**Claim:** $y_1 + y_2$ solves $y' + y = b_1 + b_2$.

$$\begin{aligned}
\text{L.H.S.:} \quad (y_1 + y_2)' + (y_1 + y_2) &= y_1' + y_2' + y_1 + y_2 \\
&= (y_1' + y_1) + (y_2' + y_2) \\
&= b_1 + b_2 \quad (\because y_1 \text{ \& } y_2 \text{ solves } *)
\end{aligned}$$

Now, let $b_1 = \sin x$, $b_2 = \cos 2x$.

Consider $y_1$ solves $y_1' + y_1 = \sin x$

<!-- Page 4 -->

Using the result from previous example

$$\text{IF} = e^{\int 1 \cdot dx} = e^x$$

$$(y_1 e^x)' = e^x \sin x$$

$$y_1 e^x = \int e^x \sin x \, dx + c$$

$$= e^x \left( \frac{\sin x - \cos x}{2} \right) + c$$

$$\boxed{y_1(x) = \frac{\sin x - \cos x}{2} + c e^{-x}}$$

Similarly solve for $y_2(x)$, where $y_2(x)$ satisfies $y' + y = \cos 2x$.

Therefore, desired solution is

$$\boxed{y(x) = y_1(x) + y_2(x)}$$

**Problem :** Which of the following functions are Lipschitz continuous in the specified domain.

(a) $f(t) = \frac{1}{t}$ in the interval $[1,2]$.

$\text{Sol}^n :$ We have $t_1, t_2 \ge 1$ or $\frac{1}{t_1 t_2} \le 1$.

$$|f(t_1) - f(t_2)| = \left| \frac{1}{t_1} - \frac{1}{t_2} \right| = \left| \frac{t_2 - t_1}{t_1 t_2} \right|$$

$$= \frac{|t_1 - t_2|}{t_1 t_2} \le |t_1 - t_2|$$

Hence $f$ is Lipschitz with $L = 1$.

<!-- Page 5 -->

(b) Is $f(t) = \frac{t}{t+1}$ Lipschitz on $[0,2]$ ?

$\text{Sol}^n :$ Let $t_1, t_2 \in [0,2]$. Note that

$$|f(t_1) - f(t_2)| \le \left| \frac{t_1}{t_1+1} - \frac{t_2}{t_2+1} \right| = \left| \frac{t_1 - t_2}{(t_1+1)(t_2+1)} \right| \le |t_1 - t_2|$$

Hence, $f$ is Lipschitz on $[0,2]$ with $L = 1$.

(c) Is $f(t) = \sqrt{t} + 1$, $t \in [0,1]$ Lipschitz continuous ?

$\text{Sol}^n :$ Consider $\left| \frac{f(t_1) - f(t_2)}{t_1 - t_2} \right|$

Now, in particular choose $t_2 = 0$, we have

$$\frac{|f(t_1) - f(0)|}{|t_1 - 0|} \le \frac{\sqrt{t_1} + 1 - 1}{t_1} = \frac{1}{\sqrt{t_1}} \to \infty \quad \text{as } t_1 \to 0.$$

Hence, $f$ is not Lipschitz continuous in $[0,1]$.

(d) Is $f(t) = t^2$, $t \in (-\infty, \infty)$ Lipschitz continuous?

$\text{Sol}^n :$ Suppose $f$ is Lipschitz on $(-\infty, \infty)$.
Then, $\exists$ a constant $L > 0$, such that

$$|f(t_1) - f(t_2)| \le L |t_1 - t_2| \quad \forall \ t_1, t_2 \in \mathbb{R}.$$

$$|t_1^2 - t_2^2| = |t_1 - t_2| |t_1 + t_2| \le L |t_1 - t_2|$$

$$\forall \ t_1, t_2 \in \mathbb{R}$$

$$|t_1 + t_2| \le L \quad \forall \ t_1, t_2 \in \mathbb{R}.$$

Therefore, $f$ is not Lipschitz continuous. This is not possible.

<!-- Page 6 -->

(e) $f(x,y) = x + y^{1/3}$ in the rectangle $[0,2] \times [-1,1]$ is $y$-Lipschitz or not ?

$\text{Sol}^n :$ If $f$ is $y$-Lipschitz then

$$|f(x,y_1) - f(x,y_2)| \le L |y_1 - y_2|$$

$$\forall \ (x,y_1), (x,y_2) \in R = [0,2] \times [-1,1]$$

Now consider

$$|f(x,y_1) - f(x,y_2)| = |x + y_1^{1/3} - x - y_2^{1/3}|$$
$$= |y_1^{1/3} - y_2^{1/3}|$$

$$\frac{|f(x,y_1) - f(x,y_2)|}{|y_1 - y_2|} = \frac{|y_1^{1/3} - y_2^{1/3}|}{|y_1 - y_2|} \quad - \ (*)$$

In particular choose points $(x,y_1), (x,0) \in R$.
We have

$$\frac{|f(x,y_1) - f(x,0)|}{|y_1 - 0|} = \frac{|y_1|^{1/3}}{|y_1|} = |y_1|^{-2/3} \to \infty \quad \text{as } y_1 \to 0.$$

Hence, $f$ is not $y$-Lipschitz in $R$.

(f) $f(x,y) = x + y^{1/3}$ in the rectangle $[0,2] \times [1,3]$ is $y$-Lipschitz or not ?

$\text{Sol}^n :$ Like problem (e), one can do this problem. Note that, right hand side function is same but domain is different.

<!-- Page 1 -->

### Lecture – 11 & 12

**Definition:** Let $f$ be a real valued function defined on $D$, where $D$ is a subset of $\mathbb{R}^2$. The function $f$ is said to be bounded in $D$, if there exists a positive number $M$ such that
$$|f(x,y)| \le M \quad \forall \ (x,y) \in D.$$

**Definition:** (Extremum value property) :
Let $f$ be defined and continuous on a closed rectangle $R = [a,b] \times [c,d]$. Then $\exists \ P, Q \in R$ such that, $f(P)$ is the maximum value of $f$ and $f(Q)$ is the minimum value of $f$ in $R$. In this case, $f$ is bounded in $R$.

**Result:** If $f$ is continuous function, such that, $\frac{\partial f}{\partial y}$ exists and bounded in $D$, then $f$ satisfies Lipschitz condition with respect to $y$ in $D$. The best Lipschitz constant is
$$M = \sup_{D} \left| \frac{\partial f}{\partial y} \right|$$

---

<!-- Page 2 -->

**Proof:** The mean value theorem implies
$$f(x,y_1) - f(x,y_2) = (y_1 - y_2) \frac{\partial f}{\partial y}(x,\eta), \quad y_1 < \eta < y_2$$

Now,
$$\begin{aligned}
|f(x,y_1) - f(x,y_2)| &= \left| \frac{\partial f}{\partial y}(x,\eta) \right| |y_1 - y_2| \\
&\le \sup_{D} \left| \frac{\partial f}{\partial y} \right| |y_1 - y_2| \\
&\le M |y_1 - y_2| \quad \leftarrow \text{Lipschitz constant}
\end{aligned}$$

**Example:** $f(x,y) = y^2, \quad (x,y) \in D = \{|x| \le a, |y| \le b\}$.

Clearly, $f_y = 2y$ is bounded in $D$ due to maximum value property. The best Lipschitz constant is
$$M = \sup_{D} \left| \frac{\partial f}{\partial y} \right| = \sup_{D} |2y| = 2b$$

**Exercise:** Verify Lipschitz condition directly!

**Hint:**
$$\left| \frac{f(x,y_2) - f(x,y_1)}{y_2 - y_1} \right| = |y_2 + y_1|$$

**Example:** Consider $f(x,y) = x|y|$ where $(x,y) \in D = \{|x| \le a, |y| \le b\}$.

$\frac{\partial f}{\partial y}$ does not exist for any point $(x,0) \in D$, still $f$ satisfies Lipschitz condition.

---

<!-- Page 3 -->

For
$$\begin{aligned}
|f(x,y_1) - f(x,y_2)| &= |x|y_1| - x|y_2|| \\
&= |x| \cdot \big| |y_1| - |y_2| \big| \\
&\le |x| |y_1 - y_2| \\
&\le a |y_1 - y_2|
\end{aligned}$$

**Remark:** 
1. Existence of bounded derivative $\frac{\partial f}{\partial y}$ is a sufficient (but not necessary) condition for Lipschitz property to hold true.
2. Lipschitz continuity $\implies$ Continuity?  
If $f$ satisfies Lipschitz condition with respect to $y$ in $D$, then for each fixed $x$, the resulting function of $y$ is a continuous function of $y$, for all $(x,y) \in D$.

**Example:** Let $f(x,y) = y + [x]$. For fixed $x$,
$$\begin{aligned}
f(x,y_1) - f(x,y_2) &= y_1 + [x] - y_2 - [x] \\
&= y_1 - y_2
\end{aligned}$$

That is,
$$|f(x,y_1) - f(x,y_2)| = |y_1 - y_2| \le 1 \cdot |y_1 - y_2|$$

Therefore, $f$ is Lipschitz continuous with respect to $y$. But we know that $f$ is discontinuous with respect to $x$ for every integral value of $x$.

<!-- Page 1 -->

**Remark:** It is to note that the condition of Lipschitz continuity with respect to $y$ implies nothing concerning the continuity of $f$ with respect to $x$.

---

### Picard's / Peano's theorem for first order ODE

**Theorem:** Let $f(x,y)$ be a continuous function defined on a rectangle $R$ with the center $(x_0, y_0)$;
$$R = \{ |x - x_0| \le a, \quad |y - y_0| \le b \}.$$

Let $M = \max_R |f(x,y)|$ and $\alpha = \min \left\{ a, \frac{b}{M} \right\}$.

Then the IVP $y' = f(x,y), \quad y(x_0) = y_0$

* **(Peano)** has at least one solution $y(x)$ defined for all $x$ in the interval
  $$I_\alpha [x_0] = \{ x : |x - x_0| < \alpha \},$$
  where $\alpha = \min \left\{ a, \frac{b}{M} \right\}$.

* **(Picard)** Further if $f$ satisfies the $y$-Lipschitz condition in $R$, i.e.
  $$|f(x, y_1) - f(x, y_2)| \le L |y_1 - y_2|,$$
  then the solution is unique.

<!-- Page 2 -->

**(5)**

### Illustration of the theorem statement by examples:

**Example:** Consider the ODE
$$y' = 1 + y^2, \quad y(0) = 0.$$
Consider the rectangle $R = \{(x,y) \in \mathbb{R}^2 : |x| \le 100, \quad |y| \le 1\}$
$$\begin{array}{|c|}
\hline
|x - 0| \le 100, \quad x_0 = 0 \\
|y - 0| \le 1, \quad y_0 = 0 \\
\hline
\end{array}$$

(i) $f$ is continuous in $R$.

(ii) **Boundedness of $f$ on rectangle:**
Here, $f(x,y) = 1 + y^2$
$$|f(x,y)| = |1 + y^2| = 1 + y^2 \le 2 \quad \forall (x,y) \in R.$$

(iii) **Lipschitz continuity of $f$ with respect to $y$:**
For $(x, y_1), (x, y_2) \in R$, we have
$$|f(x, y_1) - f(x, y_2)| = |1 + y_1^2 - 1 - y_2^2|$$
$$= |y_1^2 - y_2^2| = |y_1 + y_2| |y_1 - y_2|$$
$$\le 2 |y_1 - y_2|$$

The assumptions of Picard's and Peano's theorem are satisfied, hence there exists a unique solution in the nbhd of $x_0 = 0$.

Since the rectangle is specified, we can find $M = 2$ and $\alpha = \min \left\{ 100, \frac{1}{2} \right\} = \frac{1}{2}$.

So by the theorem, the solution exists for all $x \in \left(-\frac{1}{2}, \frac{1}{2}\right)$.

<!-- Page 3 -->

**(6)**

But, in this example, we can explicitly find out the solution $y(x) = \tan x$.

The solution is valid in the interval $\left(-\frac{\pi}{2}, \frac{\pi}{2}\right)$ which is much bigger than $\left(-\frac{1}{2}, \frac{1}{2}\right)$.

$$\alpha = \frac{1}{2}, \quad (x_0, y_0) = (0, 0)$$

---

**Example:** Find all the solutions to the initial value problem
$$y' = f(x,y) = \sin y; \quad y(0) = 0.$$

**Answer:** $y(x) \equiv 0$ is the only solution by Picard's / Peano's theorem.

**Hint:**
(i) Consider a rectangle $R$ containing the point $(x_0, y_0) = (0, 0)$.
(ii) Show that $f$ is continuous on $R$ and find $M$.
(iii) Show that $f$ is $y$-Lipschitz in $R$.

<!-- Page 1 -->

**Example:** Consider the ODE $y' = x^2 + y^2$, $y(0) = 1$. \hfill $(7)$

Here $f(x,y) = x^2 + y^2$ which is continuous and $y$-Lipschitz in any rectangle around the point $(x_0, y_0) = (0,1)$.

Thus, the assumptions of Peano's theorem and Picard's theorem are applicable and hence there exists an unique solution $y(x)$ when $|x| < \alpha$. Note that the $\alpha$ depends on the dimension of the rectangle we choose.

$$R = \{ (x,y) \in \mathbb{R}^2 : |x| \le 1, |y-1| \le 1 \}$$

$$\left[ \begin{aligned} -1 &\le y-1 \le 1 \\ 0 &\le y \le 2 \end{aligned} \right]$$

$$-1 \le x \le 1$$

![Diagram showing rectangle $R = [-1, 1] \times [0, 2]$ centered around $(0,1)$ with solution curve]

$$\text{Example} : \quad \text{Consider the IVP} \quad \frac{dy}{dx} = x + |\sin y|, \quad y(0) = \frac{\pi}{2}.$$

Clearly, $f$ is continuous on any rectangle

$$R = [-a, a] \times \left[ \frac{\pi}{2} - b, \frac{\pi}{2} + b \right]$$

around the initial condition $\left( 0, \frac{\pi}{2} \right)$.

$$M = \max_R |f(x,y)| = |a + 1| \qquad \boxed{\begin{aligned} \therefore |x| &\le a \\ |\sin y| &\le 1 \end{aligned}}$$

Now, by Peano's theorem IVP admits a solution in the interval $I_\alpha (x_0) = (-\alpha, \alpha)$ where

---

<!-- Page 2 -->

$$\alpha = \min \left\{ a, \frac{b}{a+1} \right\}$$

![Diagram of rectangle $R$ around initial point $(0, \pi/2)$]

$$b = \frac{\pi}{2}, \quad a = 1$$

$$R : |x-0| \le 1, \quad \left| y - \frac{\pi}{2} \right| \le \frac{\pi}{2}$$

It is left as an easy exercise to verify that the function $f(x,y)$ is Lipschitz in any rectangle around $\left(0, \frac{\pi}{2}\right)$ and hence the solution is unique.

**Example:** Consider the IVP $y' = y^{2/3}$, $y(0) = 0$ in $R = \{ |x| \le a, |y| \le b \}$. Here $f(x,y) = y^{2/3}$ is continuous in $R$ and so Peano's theorem assures the existence of at least one solution. But, note that $y^{2/3}$ is not $y$-Lipschitz and the assumption of Picard's theorem is not satisfied, so we can not conclude if the uniqueness is true or not. But we can construct a family of solutions

$$y_k(x) = \begin{cases} \dfrac{(x-k)^3}{27} & \text{if } x \ge k, \\ 0 & \text{if } x \le k \end{cases} \qquad (k \ge 0)$$

which solves the IVP in $R$. Hence no uniqueness.

![Diagram showing non-unique solution curves y_k(x)]

**Exercise:** Consider the ODE $y' = y^{2/3}$, $y(0) = 1$. Discuss if Picard theorem is applicable or not.

---

<!-- Page 3 -->

11/04/2025 \hfill Lecture – 13 \hfill $(1)$

### Picard's / Peano's theorem for first order ODEs

**Theorem:** Let $f(x,y)$ be a continuous function defined on a rectangle $R$ with the center $(x_0, y_0)$;

$$R = \{ |x-x_0| \le a, \quad |y-y_0| \le b \}.$$

Let $M = \max_R |f(x,y)|$ and $\alpha = \min \left\{ a, \dfrac{b}{M} \right\}$.

Then the IVP $y' = f(x,y)$, $y(x_0) = y_0$:

* **(Peano):** has at least one solution $y(x)$ defined for all $x$ in the interval

$$I_\alpha [x_0] = \{ x : |x-x_0| < \alpha \} \quad \text{where } \alpha = \min \left\{ a, \frac{b}{M} \right\}.$$

* **(Picard):** Further if $f$ satisfies the $y$-Lipschitz condition in $R$, i.e.

$$|f(x, y_1) - f(x, y_2)| \le L |y_1 - y_2|,$$

then the solution is unique.

![Diagram showing rectangle R centered at (x_0, y_0) with interval [x_0 - alpha, x_0 + alpha]]

<!-- Page 1 -->
Outline of the proof: (Picard's theorem)
Our aim is to solve the I.V.P.:
$$y' = f(x,y), \quad y(x_0) = y_0 \quad - (1)$$

Claim: The function $y(x)$ is a solution of $(1)$ if and only if it satisfies the integral equation
$$y(x) = \underbrace{y_0}_{y(x_0)} + \int_{x}^{x} f(t,y(t)) \, dt \quad - (2)$$

Proof: $(1) \implies (2)$
Suppose there exists a solution $y(x)$ for $(1)$, then $y(x)$ satisfies the integral equation $(2)$.
Integrating both sides with respect to $x$ from $x_0$ to $x$, we have
$$y(x) = y(x_0) + \int_{x_0}^{x} f(t,y(t)) \, dt \quad - (2)$$
Hence proved!

$(2) \implies (1)$ Now conversely suppose that $y$ is a continuous function and $y$ satisfies the integral identity given in $(2)$. Then we can show that $\dot{y}$ is solution for the I.V.P. $(1)$. Only step involved here

<!-- Page 2 -->
is to find
$$\frac{d}{dx} \int_{x_0}^{x} \underbrace{f(t,y(t))}_{g(t)} \, dt$$
Now by the fundamental theorem of integral calculus, we have
$$\boxed{\frac{d}{dx} \int_{x_0}^{x} f(t,y(t)) \, dt = f(x,y(x))} \quad - (3)$$

Differentiating $(2)$ with respect to $x$ and using $(3)$ to arrive at
$$\boxed{\frac{dy(x)}{dx} = f(x,y(x))}$$
Hence proved!

❀ Main idea of the proof: Construction of solution by Picard method:
Define an iterative sequence
$$y_1(x) = y_0 + \int_{x_0}^{x} f(t,y_0) \, dt$$
$$y_2(x) = y_0 + \int_{x_0}^{x} f(t,y_1(t)) \, dt$$
$$y_3(x) = y_0 + \int_{x_0}^{x} f(t,y_2(x)) \, dt$$
$$\vdots$$
$$y_n(x) = y_0 + \int_{x_0}^{x} f(t,y_{n-1}(t)) \, dt$$
and etc.

<!-- Page 3 -->
Under the assumptions of the Picard's theorem, the sequence $\{y_n\}$ can be shown to converge to some continuous function $y(x)$ in the interval $I_\alpha(x_0)$ and the limiting function must solve the I.V.P. Proof uses certain results on the uniform convergence of sequence of functions and is not a part of the syllabus.

Proof of Uniqueness: Suppose $\phi_1$ and $\phi_2$ be two solutions of the I.V.P. For ease of notations, assume that $x_0 = 0$, then
$$\phi_1(x) = y_0 + \int_{0}^{x} f(t,\phi_1(t)) \, dt$$
and
$$\phi_2(x) = y_0 + \int_{0}^{x} f(t,\phi_2(t)) \, dt$$
So,
$$\phi_1(x) - \phi_2(x) = \int_{0}^{x} [f(t,\phi_1(t)) - f(t,\phi_2(t))] \, dt$$

Let us consider the case $x > 0$ and the case $x < 0$ can be treated similarly with the necessary modifications. Using the $y$-Lipschitz condition, we can write
$$|\phi_1(x) - \phi_2(x)| \le L \int_{0}^{x} |\phi_1(x) - \phi_2(x)| \, dt$$

<!-- Page 1 -->

Let us define
$$w(x) = \int_{0}^{x} |\phi_1(t) - \phi_2(t)| \, dt$$

Then, $w'(x) = |\phi_1(x) - \phi_2(x)|$ and hence we can obtain
$$w'(x) - L w(x) \le 0.$$

Multiplying the above relation by $e^{-Lx}$ on both sides we get
$$\boxed{(e^{-Lx} w)' \le 0}$$

Since $(e^{-Lx} w)' \le 0$ the function $e^{-Lx} w(x)$ must be decreasing in the interval $(0, \alpha)$. By the definition of $w(x)$ clearly $w(0) = 0$ and hence
$$e^{-Lx} w(x) \le e^{-L \cdot 0} w(0) = 0.$$

Therefore, we obtain that
$$w(x) \le 0.$$

Again, from the definition we can see that $w$ has to be a non-negative function. From both the cases we find the function

<!-- Page 2 -->

$$w(x) = \int_{0}^{x} |\phi_1(t) - \phi_2(t)| \, dt$$

must be identically zero. It is possible only if $\phi_1(t) = \phi_2(t)$ for all $t$. Hence the uniqueness.

### Examples of Picard's iteration:

**Problem:** Solve $y' = xy$, $y(0) = 1$ using Picard's iteration method. Here $x_0 = 0$ and $y_0 = 1$.

**Sol$^n$:** The integral equation is
$$y(x) = 1 + \int_{x_0}^{x} t y \, dt.$$

Here $y_0 = 1$.

The Picard method of successive approximations are
$$y_n(x) = y_0 + \int_{x_0}^{x} f(t, y_{n-1}(t)) \, dt.$$

The successive approximations are:

For $n = 1$,
$$y_1(x) = 1 + \int_{0}^{x} t \cdot 1 \, dt = 1 + \frac{x^2}{2}.$$

For $n = 2$,
$$y_2(x) = 1 + \int_{0}^{x} t \left(1 + \frac{t^2}{2}\right) dt = 1 + \frac{x^2}{2} + \frac{x^4}{2 \cdot 4}.$$

$$\vdots$$

$$y_n(x) = 1 + \frac{x^2}{2} + \frac{1}{2!} \left(\frac{x^2}{2}\right)^2 + \cdots + \frac{1}{n!} \left(\frac{x^2}{2}\right)^n \quad (\text{By induction})$$

$$\boxed{y(x) = \lim_{n \to \infty} y_n(x) = e^{x^2/2}}$$

<!-- Page 3 -->

15/04/2021 | Lecture - 14 & 15

### Homogeneous linear differential equation:

Consider the initial value problem $y' + p(x)y = 0$; $y(x_0) = 1$. By Picard's theorem the above IVP must admit a unique solution $u(x)$, where $p(x)$ is a bounded continuous function in an interval $I$ containing $x_0$.

**Theorem:** Let $u$ be the unique solution of the homogeneous linear differential equation $y' + p(x)y = 0$ with initial condition $y(x_0) = 1$. If $y_n$ is a solution of $y' + p(x)y = 0$, then $y_n(x) = c u(x)$ for some real constant $c$.

**Proof:** Consider the function $z(x) = \frac{y_n(x)}{u(x)}$

$(\text{Why } u(x) \neq 0 \, ?)$

**Claim:** $z'(x) = 0$.

Now,
$$z'(x) = \frac{u'(x) y_n(x) - u(x) y_n'(x)}{(u(x))^2} \quad - (*)$$

Note that, $u(x)$ satisfies $y' + p(x) y = 0$, $y(x_0) = 1$ and $y_n(x)$ satisfies $y' + p(x) y = 0$

$$\Rightarrow \boxed{\begin{aligned} y_n'(x) &= -p(x) y_n \\ u'(x) &= -p(x) u \end{aligned}} \quad - (**)$$

<!-- Page 1 -->

Using $(**)$ in $(*)$, we obtain

$$z'(x) = 0 \implies z(x) = C \quad (\text{an arbitrary constant})$$

$$\frac{y_h(x)}{u(x)} = C$$

or

$$y_h(x) = C u(x), \quad \text{for some constant } C.$$

### Inhomogeneous linear differential equation:

Consider the inhomogeneous linear differential equation

$$y' + p(x) y = q(x). \qquad \text{--- } (A)$$

It can be verified that $y_p(x) = e^{-P(x)} \int e^{P(x)} q(x) dx$ is a particular solution of the differential equation $y' + p(x) y = q(x)$, where $P(x) = \int p(x) dx$.

Let $\tilde{y}$ be any other solution of $y' + p(x) y = q(x)$. Then, we let $z = \tilde{y} - y_p$, then $z$ solves the homogeneous DE

$$z' + p(x) z = 0. \qquad \text{--- } (B)$$

From the previous theorem, we obtain

$$z(x) = C u(x).$$

$$\tilde{y} = y_p + C u(x)$$

In other words, we say that:
The general solution of an inhomogeneous DE = a particular solution + constant multiple of a solution of homogeneous equation.

---

<!-- Page 2 -->

### Justification:
$y_p$ is a particular solution of equation (A).

$$y_p(x) = e^{-\int p(x) dx} \left( \int e^{\int p(x) dx} q(x) dx \right)$$

$$y_p'(x) = (-p(x)) \left( e^{-\int p(x) dx} \right) \left( \int e^{\int p(x) dx} q(x) dx \right) + e^{-\int p(x) dx} e^{\int p(x) dx} q(x)$$

$$= -p(x) y_p(x) + q(x) \qquad (\text{Use of fundamental theorem of calculus})$$

$$y_p'(x) + p(x) y_p(x) = q(x)$$

Therefore, $y_p(x)$ satisfies the DE (A).

### Justification:
$z$ solves (B), $z = \tilde{y} - y_p$.

$$\begin{aligned}
y_p' + p(x) y_p &= q(x) \\
\tilde{y}' + p(x) \tilde{y} &= q(x)
\end{aligned} \implies \underbrace{(\tilde{y} - y_p)'}_{z'} + p(x) \underbrace{(\tilde{y} - y_p)}_{z} = 0$$

$$\Downarrow$$

$$z' + p(x) z = 0$$

### Hadamard's criterion for well posed IVP:

An IVP is said to be well posed if
* it has a solution,
* the solution is unique and,
* the solution continuously depends on $y_0$ and $f$.

---

<!-- Page 3 -->

### Remark:
Consider the two sets of initial value problems:

$$\frac{dy}{dx} = f(x,y), \quad y(x_0) = y_0$$

and

$$\frac{dy}{dx} = f_\epsilon(x,y), \quad y(x_0) = y_\epsilon .$$

### Stability or continuous dependence of data:

Let $y$ and $y_\epsilon$ be their respective solutions (assume it exists and is unique). Suppose $f_\epsilon(x,y)$ and $y_\epsilon$ are perturbations of $f(x,y)$ and $y_0$, respectively. What can we say about their corresponding solutions?

Why do we need to consider such perturbed problems?
1. Due to some measurement error in $y_0$.
2. Due to some inherent error in mathematical modeling of the physical phenomenon.
3. As long as, $f$ is continuously differentiable the stability of the system can be expected.

### Examples of non stable systems:

1. Initially mathematicians used to think that a small change in the initial data should give only a small change in the final solution. But, a meteorologist Edward Lorentz discovered that it is not always true; phenomenon was explained

<!-- Page 1 -->

using chaos theory / Butterfly effect.

Examples: Weather prediction, Double Pendulum

(2) How did he propose the chaos theory while doing the computer simulation of a weather prediction

(3) "Does the flap of a butterfly's wings in Brazil cause a hurricane in Texas". This was the famous title of a talk of Edward Lorenz who proposed the butterfly effect.

(4) (i) Computer simulation of Double pendulum experiment  
(ii) Butterfly effect

### Summary of first order differential equations:

(1) Fundamental theorem of calculus and $y' = f(x)$ when $f$ is continuous.

(2) Nonlinear equations  
(i) Variable separable  
(ii) Reducible to variable separable  
(iii) Exact equations, Integrating factors  

(3) Existence and uniqueness results for IVP
$$y' = f(x, y), \quad y(x_0) = y_0$$
(i) Peano's Existence theorem  
(ii) Picard's uniqueness theorem  

---

<!-- Page 2 -->

(4) Picard's method of successive approximations for solving IVP

(5) Linear equations  
(i) Formula for finding the general solution of linear inhomogeneous equation  
(ii) Equations reducible to linear first order equations, Bernoulli  

---

<!-- Page 3 -->

### Second Order linear ODE:

The second order linear ODE's are among the most important from the point of view of physics and engineering applications. They model the physical world's phenomena in ideal situations.

A standard / normal / monic form of a general second order linear ODE is given by

$$\boxed{\frac{d^2 y}{d x^2} + p(x) \frac{dy}{dx} + q(x) y = r(x)}$$

A study of the existence, uniqueness and/or number of solutions of such ODE's and their mathematical behaviour like estimating number of zeros etc. is called a qualitative analysis.

**Examples:** Some of the important second order linear ODE's are:

1) $y'' + \mu^2 y = 0 \quad$ (Sturm-Liouville equation)
2) $(1 - x^2) y'' - 2 x y' + n(n+1) y = 0 \quad$ (Legendre equation)
3) $x^2 y'' + x y' + (x^2 - \nu^2) y = 0 \quad$ (Bessel equation)

In the above equations, $\mu, n, \nu$, respectively are parameters.

The domain intervals are $\mathbb{R}$, $(-1, 1)$, $(0, \infty)$ respectively.

<!-- Page 1 -->

Main theorem for IVP for $2^{nd}$ order homogeneous ODE :

**$\text{Def}^n$ : (IVP for $2^{nd}$ order linear homogeneous ODE)**

Let $p(x), q(x)$ be continuous on an open or closed interval $I$ with $x_0 \in I$. An initial value problem of a second order homogeneous linear ODE is of the form
$$y'' + p(x) y' + q(x) y = 0 ; \quad y(x_0) = a, \ y'(x_0) = b \qquad (*)$$

The following result represents the existence and uniqueness result for second order linear ODE's with prescribed initial values:

**Theorem : (Existence and Uniqueness) :** An IVP of a second order linear homogeneous ODE $(*)$ in an interval $I$ has an unique solution in the said interval.

$\Rightarrow$ The existence / uniqueness theorem can be proved by a version of Picard's theorem iteration for vector valued functions (not in syllabus)

**Recall :** We proved the theorem :

**Theorem :** Let $u$ be the unique solution of the homogeneous linear differential equation

<!-- Page 2 -->

$y' + p(x) y = 0$ with initial condition $y(x_0) = 1$. If $y_h$ is any solution of the homogeneous DE $y' + p(x) y = 0$, then necessarily $y_h(x) = C u(x)$ for some real constant $C$.

**Question :** What could be the equivalent result for a second order linear differential equation?

**Main results to be proved :** Any solution $y_h$ must be equal to $C_1 y_1 + C_2 y_2$ for some real constants $C_1, C_2$ and $y_1, y_2$ are two linearly independent solutions of an associated initial value problem.

### Linear dependence and independence :

A set of functions $\{\phi_1(x), \phi_2(x), \dots, \phi_n(x)\}$ are said to be **linearly independent** on an interval $I$ if for some constants $C_1, C_2, \dots, C_n \in \mathbb{R}$,
$$\sum_{j=1}^{n} C_j \phi_j(x) = 0 \quad \forall x \in I \implies C_1 = C_2 = \dots = C_n = 0.$$

**Linear dependence :** A set of functions $\{\phi_1, \dots, \phi_n\}$ are said to be **linearly dependent** on an interval $I$ if there exists some constants $C_1, \dots, C_n \in \mathbb{R}$ at least one

<!-- Page 3 -->

of the $C_j$ is non zero and
$$\sum_{j=1}^{n} C_j \phi_j(x) = 0 \quad \forall x \in I.$$

**Remark :** A set of two functions $\{\phi_1(x), \phi_2(x)\}$ are linearly dependent if
(a) at least one of them is a zero function
(b) or $\phi_1(x) = C \phi_2(x) \quad \forall x \in I$.

### Examples of linearly dependent / independent functions

(1) $\{\sin x, \cos x\}$ in the interval $[0, 2\pi]$
(2) $\{1, x\}$ in the interval $[0, 1]$
(3) $\{1, x, x^3\}$ in the interval $[0, 1]$
(4) $\{\sin x, \cos x, \sin x + 5 \cos x\}$ in the interval $[0, 2\pi]$
(5) $\{1, e^x, e^{2x}\}$ in the interval $(-\infty, \infty)$
(6) $\{1 + 2x, 1 + x, x\}$ in the interval $(-1, 1)$
(7) $\{\sin x, \sin^2 x\}$
(8) $\{\sin^2 x, \cos^2 x\}$
(9) $\{\sin^2 x, \cos^2 x, 1\}$
(10) $\{\sin^2 x, \cos^2 x, \cos 2x\}$

**Answer :**
- **Linearly dependent** — (4), (6), (9), (10)
- **Linearly independent** — (1), (2), (3), (5), (7), (8)

**Remark :** We will see if there is any other method to check the linear independence of collection of functions.

