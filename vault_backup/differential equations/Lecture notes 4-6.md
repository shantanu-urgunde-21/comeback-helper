---
course: "differential equations"
source_file: "Lecture notes 4-6.pdf"
tags: ["math", "coursework", "differential-equations"]
---

# Lecture notes 4-6

<!-- Page 1 -->
$\begin{aligned}& \text { Lecture }-4 \\& \text { First fundamental theorem of calculus. } \\& \text { Let } f \text { be a continuous function on } [a, b]. \text { For } x \in [a, b], \text { define } \\& F(x):=\int_{a}^{x} f(t) \, dt. \\& \text { Then, } F \text { is differentiable on } [a, b] \text { and } \\& F'(x)=f(x) \text { for all } x \in [a, b]. \\& \text { Separable ODE: } \text { An ordinary differential equation of the form } \\& M(x) + N(y) \frac{dy}{dx} = 0 \\& \text { is called a separable ODE, where } \\& M \text { and } N \text { are functions of } x \text { and } y, \text { respectively. } \\& \text { Let } H_1(x) \text { and } H_2(y) \text { be any functions such that } \\& H_1'(x) = M(x) \text { and } H_2'(y) = N(y) \\& \text { Using the chain rule, } \frac{d}{dx} H_2(y) = H_2'(y) \frac{dy}{dx} \\& \text { We obtain } \\& H_1'(x) + H_2'(y) y = 0 \\& \text { Using the chain rule, } \frac{d}{dx} H_2(y) = H_2'(y) \frac{dy}{dx} \\& \text { We obtain } \\& H_1'(x) + H_2'(y) y = 0 \\& \text { Using the chain rule, } \frac{d}{dx} H_2(y) = H_2'(y) \frac{dy}{dx} \\& \text { We obtain } \\& H_1'(x) + H_2'(y) y = 0 \\& \text { Using the chain rule, } \frac{d}{dx} H_2(y) = H_2'(y) \frac{dy}{dx} \\& \text { We obtain } \\& H_1'(x) + H_2'(y) y = 0 \\& \text { Using the chain rule, } \frac{d}{dx} H_2(y) = H_2'(y) \frac{dy}{dx} \\& \text { We obtain } \\& H_1'(x) + H_2'(y) y = 0 \\& \text { Using the chain rule, } \frac{d}{dx} H_2(y) = H_2'(y) \frac{dy}{dx} \\& \text { We obtain } \\& H_1'(x) + H_2'(y) y = 0 \\& \text { Using the chain rule, } \frac{d}{dx} H_2(y) = H_2'(y) \frac{dy}{dx} \\& \text { We obtain } \\& H_1'(x) + H_2'(y) y = 0 \\& \text { Using the chain rule, } \frac{d}{dx} H_2(y) = H_2'(y) \frac{dy}{dx} \\& \text { We obtain } \\& H_1'(x) + H_2'(y) y = 0 \\& \text { Using the chain rule, } \frac{d}{dx} H_2(y) = H_2'(y) \frac{dy}{dx} \\& \text { We obtain } \\& H_1'(x) + H_2'(y) y = 0 \\& \text { Using the chain rule, } \frac{d}{dx} H_2(y) = H_2'(y) \frac{dy}{dx} \\& \text { We obtain } \\& H_1'(x) + H_2'(y) y = 0 \\& \text { Using the chain rule, } \frac{d}{dx} H_2(y) = H_2'(y) \frac{dy}{dx} \\& \text { We obtain } \\& H_1'(x) + H_2'(y) y = 0 \\& \text { Using the chain rule, } \frac{d}{dx} H_2(y) = H_2'(y) \frac{dy}{dx} \\& \text

<!-- Page 2 -->
Here, in leads to
$$\frac{d}{dx}\left(H_1(x) + H_2(y)\right) = 0$$

Integration of (5) gives
$$H_1(x) + H_2(y) = C$$

Where C is an arbitrary constant.

Question: Why do such functions $H_1(x)$ and $H_2(y)$ exist?

Justification: Since M and N are continuous functions of x and y, respectively, on $[a, b]$. Define
$$H_1(x) = \int_{a}^{x} M(x) dx$$
and
$$H_2(y) = \int_{a}^{y} N(y) dy$$

Using the first fundamental theorem of calculus, $H_1(x)$ and $H_2(y)$ are differentiable functions and
$$H_1'(x) = M(x)$$
$$H_2'(y) = N(y).$$

Question: Why do we call it a separable ODEs?

Reason: Note that if we compare (1) with
$$y' = f(x, y)$$
then
$$f(x, y) = -M(x) \left(\frac{1}{N(y)}\right).$$
Write
$$h(x) = -M(x)$$
and
$$g(y) = \frac{1}{N(y)}$$
with
$$N(y) \neq 0.$$

<!-- Page 3 -->
$\left|f(x, y)\right| = h(x) g(y)$

This is why these ODEs are called separable ODEs.

Examples of separable ODEs:

Find the solution to the initial value problem

$\frac{dy}{dx} = \frac{y \cos x}{1 + 2y^2}, \quad y(0) = 1$

Initial value problem

Assume $y(x) \neq 0$. Then,

On integrating, we get

$\ln |y| + y^2 = \sin x + c$

If we choose the initial condition $y(0) = 1$, then we get $c = 1$. Hence, a particular solution to the IVP is

$\ln |y| + y^2 = \sin x + 1$

Remark: Note that $y(x) = 0$ is a solution to the given DE, but it is not a solution to the given IVP.

<!-- Page 4 -->
```markdown
# Remark
In finding a one parameter family of solutions in the separation process, we assume that \( N(y) \neq 0 \). Therefore, some solutions may be lost in the formal separation process.

## Example
Solve the DE \( y' = -2xy - \frac{1}{y} \).

### Solution
Separating the variables, we get:
\[ 2x + \frac{y'}{y} = 0 \]
\[ \ln |y| + x^2 = C_1 \]
\[ \ln |y| = C_1 - x^2 \]
\[ y(x) = C_1 e^{-x^2} \]

### Implicit Solution
\[ \ln |y| + x^2 = C_1 \]
\[ y(x) = C_1 e^{-x^2} \]

### Explicit Solution
\[ y(x) = C_1 e^{-x^2} \]

How do the solutions look like?
If we are given an initial condition \( y(x_0) = y_0 \), then we get:
\[ y_0 = C_1 e^{-x_0^2} \]
or
\[ C_1 = y_0 e^{-x_0^2} \]

And from:
\[ \frac{y(x)}{y(x_0)} = e^{(x - x_0)^2} \]
\[ y(x) = y_0 e^{(x - x_0)^2} \]

In particular, if we choose \( y_0 = -e^{-x_0^2} \), then:
```

<!-- Page 5 -->
$y(x) = e^{x^2}$ and the graph of solution is

$f(x) = e^{x^2}$

Area $f(x) = \sqrt{\pi}$

$y_0 = e^{x_0^2}$

Note: $y(x) = 0$ is a solution of the original equation (*) which was lost in the separation process.

Example: Given an amount of a radioactive substance, say 1 gm, find the amount present at any later time.

As we have already seen, the relevant ODE is

$\frac{dy}{dt} = -ky$

The initial amount given is 1 gm at time $t = 0$, i.e., $y(0) = 1$.

By the method of separation of variables, we have $\frac{dy}{y} = -kdt$, $y(0) \neq 0$.

Integration of the above leads to

$\ln y = -kt + \ln C$

<!-- Page 6 -->
$\text { Therefore, } \quad y(x) = c e^{-kt} \quad \text { for an arbitrary constant } c, \text { is a solution of the above ODE. Now, } y(0) = 1 \Rightarrow c = 1. \text { Hence, a particular solution to the above ODE with the given initial condition is } y(x) = e^{-kt}.$

<!-- Page 7 -->
$\text { Definition (solution of an ODE of order } n) \text { A function } \phi(x) \text { is said to be a solution of an } n\text { -th order ODE } y^{(n)} = f(x, y, y', \ldots, y^{(n-1)}) \text { in an interval } \alpha < x < \beta \text { if } \phi \text { has at least } n \text { derivatives: } \phi', \phi'', \ldots, \phi^{(n)} \text { and } \phi^{(n)}(x) = f(x, \phi(x), \phi'(x), \ldots, \phi^{(n-1)}(x)) \text { in an interval } \alpha < x < \beta. \text { Remarks: } \text { ① The interval } \alpha < x < \beta \text { is known as the interval of existence or interval of definition for the solution. ② A solution to a DE is also known as an integral of the equation and its graph is called a solution curve or an integral curve. ③ Explicit and Implicit solution solution: An explicit solution solution of the n-th order ODE is a solution (real valued) in which the dependent variable is expressed in terms of the independent variable and constants. }$

<!-- Page 8 -->
That is, an explicit solution is a solution $y(x)$ of the form $y = \phi(x)$ on $\alpha < x < \beta$.

**Implicit solution:** A relation $g(x, y) = 0$ is called an implicit solution if this relation defines at least one function $\phi(x)$ in an interval $\alpha < x < \beta$ such that the function $\phi(x)$ is an explicit solution of the equation.

**Example:** Consider $x + yy' = 0$. The equation $x^2 + y^2 - 25 = 0$ is an implicit solution of $x + yy' = 0$ in $-5 < x < 5$ because it defines two functions $\phi_1(x) = \sqrt{25 - x^2}$ and $\phi_2(x) = -\sqrt{25 - x^2}$, which are explicit solutions of the ODE.

**Exercise:** Show that the function $\phi(x) = x^2 - x^1$ is an explicit solution to the ODE.

**Hint:** Substitute $\phi(x)$ in the equation.

**Hint:** Substitute $\phi(x)$ in the equation.

<!-- Page 9 -->
Formal solution: A relation $g(x, y) = 0$ is called a formal solution of $y^{(n)} = f(x, y, y', \ldots, y^{(n)})$, if on differentiating the former in times w.r.t. $x$, we get back the latter.

Example: Consider $x^2 + y^2 + 25 = 0$

$\Rightarrow x + y^2 = 0 \Rightarrow y^2 = -x^2$

We say $x^2 + y^2 + 25 = 0$ formally satisfies $x + y^2 = 0$. But it is not an implicit solution of the differential equation (DE) as this relation does not yield $\phi$ which is an explicit solution of the DE on any real interval I.

If we try to write $y = \pm \sqrt{-25 - x^2}$

Then $y(x)$ is not a solution for the differential equation in any real interval.

<!-- Page 10 -->
$\text { Homogeneous equation: }$

$\text { Definition: }$

A function $f(x_1, x_2, \ldots, x_n)$ is called homogeneous of degree $d$ if

$f(t x_1, t x_2, \ldots, t x_n) = t^d f(x_1, \ldots, x_n)$

for some $d \in \mathbb{Z}$ and for any scalar $t$.

The number $d \in \mathbb{Z}$ is called the degree of $f(x_1, \ldots, x_n)$.

Example: $f(x, y) = x^2 + xy + y^2$ is homogeneous of degree 2.

$f(x, y) = y + x \cos^2(\frac{y}{x})$ is homogeneous of degree 1.

Definition: The first order ODE

$M(x, y) + N(x, y) \frac{dy}{dx} = 0$

is called homogeneous if $M$ and $N$ are homogeneous functions of degree $d$.

Example: $(y^2 - x^2) \frac{dy}{dx} + 2xy = 0$

Let $M(x, y) + N(x, y) \frac{dy}{dx} = 0$, where $M$ and $N$ are homogeneous functions of degree $d$.

Let $\frac{y}{x} = v$. Then, $\frac{dy}{dx} = x \frac{dv}{dx} + v$.

<!-- Page 11 -->
Substituting this in the given ODE,

$M(x, v(x)) + N(x, v(x)) (x \frac{dv}{dx} + v) = 0$

Thus,

$x \frac{dM}{dx} + x \frac{dN}{dx} (x \frac{dv}{dx} + v) = 0$

Let $x \neq 0$. Then,

$M(1, v) + N(1, v) v + N(1, v) x \frac{dv}{dx} = 0$

Thus,

$\frac{dx}{x} + \frac{N(1, v)}{M(1, v) + N(1, v) v} dv = 0$

This is a separable equation.

Exercise: Let $\frac{dy}{dx} = f(x, y)$, where $f(x, y)$ is homogeneous of degree $0$. Show that it can be reduced to a separable equation.

Hint: Substitute $y = x v$ and obtain

$\frac{dx}{x} = \frac{dv}{f(1, v) - v}$

Example: Solve the ODE

$(y^2 - x^2) \frac{dy}{dx} + 2xy = 0$

<!-- Page 12 -->
```markdown
# Solution

We can write
$$\frac{dy}{dx} = \frac{2xy}{x^2 - y^2}$$

The RHS is homogeneous of degree 0.

Hence,
$$\frac{dx}{x} = \frac{dv}{\frac{2v}{1-v^2} - v} = \frac{(1-v^2)dv}{v + v^3}$$

On integrating, we get
$$\ln|x| = \int \left[\frac{1}{v} - \left(\frac{2v}{v^2 + 1}\right)\right]dv + c_1$$

or
$$\ln|x| + \ln(v^2 + 1) - \ln|v| = c_1$$

or
$$\ln|x(v^2 + 1)| = c_1$$

Hence,
$$\frac{x(v^2 + 1)}{v} = 2cy$$

or
$$y^2 + x^2 = 2cy^2$$

or
$$x^2 + (y - c)^2 = c^2$$

# Problem

Solve the following differential equation
$$\frac{dy}{dx} = \frac{x^2 + xy + y^2}{x^2}$$

Solution:
Note that $f(x, y) = \frac{x^2 + xy + y^2}{x^2}$ is a homogeneous function of degree 0.

As discussed before, the substitution $y = vx$ leads to
$$\frac{dv}{dx} = \frac{f(1, v) - v}{x}$$
```

<!-- Page 13 -->
Now
$f(1, v) = \frac{1 + v + v^2}{1} = 1 + v + v^2$

$\frac{dv}{dx} = \frac{1 + v + v^2 - v}{x} = \frac{1 + v^2}{x}$

$\Rightarrow \frac{1}{x} dx = \frac{1}{1 + v^2} dv$

$\Rightarrow \tan^{-1} v = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) - \ln |x| = c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln |x| + c$

$\Rightarrow \tan^{-1} (y/x) = \ln

<!-- Page 14 -->
Given that $x \rightarrow \infty$, $y(x) \rightarrow \pi / 2$.

Note that as $x \rightarrow \infty$, $\frac{1}{x^2} \rightarrow 0$.

$y(x) \rightarrow \frac{\pi}{2}$, $\cos y \rightarrow 0$.

Substituting $(**)$ in $(*)$, we obtain $|c = 0|$.

Therefore, the particular solution of the given ODE is $\left|\frac{1}{x^2} - \cos y = 0\right|$.

Problem: Solve the differential equation $y'(x) = f(x)$ for $x \in \mathbb{R}$, where $y(x) = f(x)$ for $x \in \mathbb{R}$.

Solution: Note that the right-hand side function $f(x)$ is continuous for $x \in \mathbb{R}$. Therefore, by the first fundamental theorem of calculus, $y(x)$ is differentiable.

$\frac{dy}{dx} = e^2$ if $x < 2$.

$\frac{dy}{dx} = e^2$ if $x < 2$.

Since $y(x)$ is continuous, $y(x)$ is differentiable.

$\lim_{x \rightarrow 2^-} y(x) = y(2)$.

$\lim_{x \rightarrow 2^-} y(x) = y(2)$.

$\lim_{x \rightarrow 2^-} y(x) = y(2)$.

$\lim_{x \rightarrow 2^-} y(x) = y(2)$.

$\lim_{x \rightarrow 2^-} y(x) = y(2)$.

$\lim_{x \rightarrow 2^-} y(x) = y(2)$.

$\lim_{x \rightarrow 2^-} y(x) = y(2)$.

$\lim_{x \rightarrow 2^-} y(x) = y(2)$.

$\lim_{x \rightarrow 2^-} y(x) = y(2)$.

$\lim_{x \rightarrow 2^-} y(x) = y(2)$.

$\lim_{x \rightarrow 2^-} y(x) = y(2)$.

$\lim_{x \rightarrow 2^-} y(x) = y(2)$.

$\lim_{x \rightarrow 2^-} y(x) = y(2)$.

$\lim_{x \rightarrow 2^-} y(x) = y(2)$.

$\lim_{x \rightarrow 2^-} y(x) = y(2)$.

$\lim_{x \rightarrow 2^-} y(x) = y(2)$.

$\lim_{x \rightarrow 2^-} y(x) = y(2)$.

$\lim_{x \rightarrow 2^-} y(x) = y(2)$.

$\lim_{x \rightarrow 2^-} y(x) = y(2)$.

$\lim_{x \rightarrow 2^-} y(x) = y(2)$.

$\lim_{x \rightarrow 2^-} y(x) = y(2)$.

$\lim_{x \rightarrow 2^-} y(x) = y(2)$.

$\lim_{x \rightarrow 2^-} y(x) = y(2)$.

$\lim_{x \rightarrow 2^-} y(x) = y(2)$.

$\lim_{x \rightarrow 2^-} y(x) = y(2)$.

$\lim_{x \rightarrow 2^-} y(x) = y(2)$.

$\lim_{x \rightarrow 2^-} y(x) = y(2)$.

$\lim_{x \rightarrow 2^-} y(x) = y(2)$.

$\lim_{x \rightarrow 2^-} y(x) = y(2)$.

$\lim_{x \rightarrow 2^-} y(x) = y(2)$.

$\lim_{x \rightarrow 2^-} y(x) = y(2)$.

$\lim_{x \rightarrow 2^-} y(x) = y(2)$.

$\lim_{x \rightarrow 2^-} y(x) = y(2)$.

$\lim_{x \rightarrow 2^-} y(x) = y(2)$.

$\lim_{x \rightarrow 2^-} y(x) = y(2)$.

$\lim_{x \rightarrow 2^-} y(x) = y(2)$.

$\lim_{x \rightarrow 2^-} y(x) = y(2)$.

$\lim_{x \rightarrow 2^-} y(x) = y(2)$.

$\lim_{x \rightarrow 2^-} y(x) = y(2)$.

$\lim_{x \rightarrow 2

<!-- Page 15 -->
For $x \geq 2$, $\frac{4y}{ax} = e^x$.

Using (*) in (a) and (b), we get

$e^2 + c_2 = e^2 \cdot 2 + c_1$

$\Rightarrow c_2 - c_1 = e^2$

$\Rightarrow c_2 = c_1 + e^2$

From (a), (b) and (c), we have

$y(x) = \begin{cases} e^2x + c_1 & x < 2 \\ e^x + 1 + c_1 & x \geq 2 \end{cases}$

Choose $c_1 = 1$, then $c_2 = 1 + e^2$

and $y(x) = \begin{cases} e^2x + 1 & x < 2 \\ e^x + 1 + e^2 & x \geq 2 \end{cases}$

