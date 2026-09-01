---
course: "differential equations"
source_file: "Lecture 14 notes.pdf"
tags: ["math", "coursework", "differential-equations"]
---

# Lecture 14 notes

<!-- Page 1 -->
$$\text{Lecture } 14$$

$\underline{\text{Recall : }}$ (Initial value problem) let $y'=f(x,y)$ be a DE in an interval $I$ of the $x$ variable and let $x_0\in I$. An initial condition is a prescription of a value $y_0$ of the unknown function $y$ at $x_0$. In short, we write $y(x_0)=y_0$.
A DE along with an initial condition is called an IVP. That is
$$\begin{cases} y'(x) = f(x,y) & \text{(Differential Equation)} \\ y(x_0) = y_0 & \text{(Initial Condition)} \end{cases}$$

$\underline{\text{Definition : }}$ Initial value problem for 
$$\boxed{y^{(n)} = f(x, y, y', \dots, y^{(n-1)})}$$
is to find a solution $\boxed{y(x) \in C^n(I)}$ that satisfies
$$\boxed{y^{(n)} = f(x, y, y', \dots, y^{(n-1)})}\quad \text{for } x \in (a,b)$$
and the $\underline{n}$ initial conditions (IC)
$$y(x_0)=y_0, \quad y'(x_0)=y_1, \dots, y^{(n-1)}(x_0)=y_{n-1},$$
where $\underline{x_0 \in (a,b)}$ and $\underline{y_0, y_1, \dots, y_{n-1}}$ are given constants.

<!-- Page 2 -->
$\underline{\text{Remark : }}$ For a differential equation of $\underline{n^{\text{th}}\text{ order}}$, $\underline{n}$ initial conditions are specified in order to assure uniqueness.

$\underline{\text{Example : }}$ ① The differential equation $y'=y$, $y(0)=1$ admits a unique solution.

② The differential equation $y'=\sqrt{y}$, $y(0)=0$, admits at least two solutions.
A solution $y_1(x) = \frac{x^2}{4}$ can be obtained by variable separable method and by inspection $y_2(x)=0$ is also a solution.

③ The DE $|y'|+|y|=0$, $y(0)=3$ admits no solution. Also, $|y'|+|y|+1=0$ also admits no solution for whatever initial condition we impose.

④ The DE $y'(x)=\sqrt{x}$, $y(0)=0$ admits the unique solution $y(x) = \frac{2}{3} x^{3/2}$.

<!-- Page 3 -->
$\underline{\text{Problem : }}$ Consider the equation $y'=y$; $y(0)=1$. Show that $y=e^x$ is the only solution of the above differential equation.
$\underline{\text{Existence of Solution : }}$
Substitute $y=e^x$ in the equation $y'=y$ and show that it satisfies the differential equation and the initial condition.

$\underline{\text{Uniqueness : }}$ let $y_1=e^x$ and $y_2$ be any other solution of the ODE $y'=y$; $y(0)=1$.

In general, to prove uniqueness we either prove $y_2-y_1=0$ or $\frac{y_2}{y_1}=1$. Here, since $y_1(x) \neq 0$, we will show that $\frac{y_2}{y_1}=1$.

$$\begin{aligned}
\text{Now } \left(\frac{y_2}{y_1}\right)' &= \frac{e^x y_2' - e^x y_2}{e^{2x}} \\
&= e^{-x}(y_2' - y_2) = 0, \text{ since } y_2(x)
\end{aligned}$$
satisfies the differential equation.
This implies $\frac{y_2}{y_1}=k$. Now $y_1(0)=1=y_2(0)$.
$$\implies k=1.$$

<!-- Page 1 -->
What can we observe about the existence/
uniqueness of the IVP $y'=f(t,y)$, $y(x_0)=y_0$?

Hadamard's criterion for well-posed IVP:

An IVP is said to be well-posed if
(i) it has a solution
(ii) the solution is unique and,
(iii) the solution depends continuously on the
initial data $y_0$ and $f$.

Why "Existence of solution":

1) Not every differential equation can be solved
explicitly, even implicit relations are difficult
to obtain.

2) Mathematicians are not interested in finding
a solution for an approximate problem and
live happily thereafter.

3) So we look for some results which would
tell us there exists a solution to the DE.

<!-- Page 2 -->
4) There are basically three types of differential
equations:
(i) Equations for which solution is known to
exist.
(ii) Equations which does not admit any solution.
(iii) A third class of equations for which none
of the existing theory provides a solution.

5) In fact the third type is really a huge
class and the mathematicians are generally
excited when a new differential equation
is solved which is relevent to the
other branches of science. Navier-Stokes
equations, Clay mathematics institute etc.

6) Theoretical existence result gives a green
signal for the engineers to solve them
numerically.

<!-- Page 3 -->
Most of the times a differential equation
along with its initial conditions corresponds to
a real life problem or a physical process.

Uniqueness of solution
These physical problems should have a unique
solution. Still if we could find more than
one solution to the differential equation, we
may need to go back to our basics. Sometimes
we would have ignored certain other factors
which describes the physical system or our
understanding of the process was wrong.

Lipschitz condition:
Let $f$ be defined on an interval I. The function
$f$ is said to satisfy Lipschitz condition in I
if $\exists$ a constant $L>0$ such that

$$|f(t_1) - f(t_2)| \le L |t_1 - t_2| \quad \forall \, t_1, t_2 \in I.$$

<!-- Page 1 -->
Examples: 1) Using mean value theorem, we can see that if $f$ is differentiable and the derivative is bounded in some interval $I$, then $f$ is Lipschitz continuous on $I$.

2) $\sin t$, $\cos t$, $e^t$ etc. are Lipschitz in any closed and bounded interval $[a, b]$.

3) $f(t) = |t|$ is Lipschitz continuous on $[-1, 1]$ by triangle inequality, but not differentiable.

4) Lipschitz continuous function must be continuous. $\text{Verify!}$

5) $f(t) = \sqrt{t}$ is continuous but not Lipschitz continuous in $[0, 1]$.

Solution: Note that, we have to show $\frac{|f(t_1)-f(t_2)|}{|t_1-t_2|} \leq L \quad \forall t_1, t_2 \in [0, 1]$

$f(t) = \sqrt{t}$. $\frac{|f(t_1)-f(t_2)|}{|t_1-t_2|} = \frac{\sqrt{t_1}-\sqrt{t_2}}{|t_1-t_2|}$.

Choose $t_2 = 0$,

<!-- Page 2 -->
$|f(t_1)-f(0)| = \frac{\sqrt{t_1}}{t_1} = \frac{1}{\sqrt{t_1}} \to \infty$ as $t_1 \to 0$. ($\text{show!}$)

Here $f$ is continuous, but not Lipschitz continuous.

6) The function $f(t) = t^2$ is Lipschitz in $[1, 2]$ (locally Lipschitz)

$|f(t_1)-f(t_2)| = |t_1^2 - t_2^2| = |t_1+t_2||t_1-t_2|$
$\leq \left(\max_{t\in[1,2]} |t_1+t_2|\right)|t_1-t_2|$
$\leq 4 |t_1-t_2|$

Therefore, $f$ is Lipschitz continuous on $[1, 2]$ ($\text{open, connected set}$)

Definition: Let $f$ be defined on a domain $D \subset \mathbb{R}^2$. The function $f$ is said to satisfy $y$-Lipschitz condition in $D$ if $\exists$ a constant $L > 0$, such that
$|f(x, y_1) - f(x, y_2)| \leq L |y_1 - y_2| \quad \forall (x, y_1), (x, y_2) \in D$.

<!-- Page 3 -->
Definition: Let $f$ be a real valued function defined on $D$, where $D$ is a subset of $\mathbb{R}^2$. The function $f$ is said to be bounded in $D$ if there exists a positive number $M$, such that,
$|f(x, y)| \leq M \quad \forall (x, y) \in D$.

Result: If $f$ is a continuous function such that $\frac{\partial f}{\partial y}$ exists and bounded in $D$, then $f$ satisfies Lipschitz condition with respect to $y$ in $D$. The best Lipschitz constant is
$$L = \sup_D \left|\frac{\partial f}{\partial y}\right|$$

Proof: The Mean Value theorem implies
$f(x, y_1) - f(x, y_2) = (y_1 - y_2) \frac{\partial f}{\partial y}(x, \eta), \quad y_1 < \eta < y_2$.

Now,
$|f(x, y_1) - f(x, y_2)| = \left|\frac{\partial f}{\partial y}(x, \eta)\right| |y_1 - y_2|$
$\leq L |y_1 - y_2|$. ($\text{Lipschitz constant}$)

<!-- Page 1 -->
$$\text{Example: } f(x,y) = y^2, \quad (x,y) \in D = \{|x| \le a, |y| \le b\}.$$

Clearly, $f_y = 2y$ is bounded in $D$ due to maximum value property. The best Lipschitz constant is

$$M = \sup_D \left|\frac{\partial f}{\partial y}\right| = \sup_D |2y| = 2b \text{ .}$$

$$\text{Exercise: Verify Lipschitz condition directly!}$$

$$\text{Hint: } \left| \frac{f(x,y_2) - f(x,y_1)}{y_2 - y_1} \right| = |y_2 + y_1| \text{ .}$$

$$\text{Example: Consider } f(x,y) = x |y|, \quad (x,y) \in D = \{|x| \le a, |y| \le b\}.$$

$\frac{\partial f}{\partial y}$ does not exist for any point $(x,0) \in D$ (Why?)
Still $f$ satisfies Lipschitz condition! For

$$|f(x,y_1) - f(x,y_2)| = |x|y_1| - x|y_2||$$
$$= |x| \big( |y_1| - |y_2| \big)$$
$$\le |x| |y_1 - y_2|$$
$$\le a |y_1 - y_2| \text{ .}$$

<!-- Page 2 -->
$$\text{Remark: Existence of bounded derivative } \frac{\partial f}{\partial y}$$
$$\text{is a sufficient (but not necessary)}$$
$$\text{condition for Lipschitz property to hold true.}$$

$$\text{Lipschitz condition } \Rightarrow \text{ Continuity?}$$
$$\text{If } f \text{ satisfies lipschitz condition with respect}$$
$$\text{to } y \text{ in } D \text{, then for each fixed } x \text{, the}$$
$$\text{resulting function of } y \text{ is a continuous}$$
$$\text{function of } y \text{, for all } (x,y) \text{ in } D \text{.}$$

$$\text{Example: let } f(x,y) = y + [x]. \text{ For fixed } x \text{,}$$

$$f(x,y_1) - f(x,y_2) = y_1 + [x] - y_2 - [x]$$
$$= y_1 - y_2$$
$$\text{That is,}$$
$$|f(x,y_1) - f(x,y_2)| = |y_1 - y_2|$$
$$\le 1 \cdot |y_1 - y_2|$$

$$\text{Therefore, } f \text{ is lipschitz continuous with respect}$$
$$\text{to } y \text{. But, we know that } f \text{ is \underline{discontinuous} with}$$
$$\text{respect to } x \text{ for every integral value of } x \text{.}$$
$$\text{Note that the condition of lipschitz continuity}$$
$$\text{implies \underline{nothing} concerning the continuity of } f$$
$$\text{with respect to } x \text{.}$$

