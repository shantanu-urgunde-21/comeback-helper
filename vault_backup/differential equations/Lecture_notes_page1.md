---
course: "differential equations"
source_file: "Lecture_notes_page1.pdf"
tags: ["math", "coursework", "differential-equations"]
---

# Lecture_notes_page1

<!-- Page 1 -->
$\text { Lecture - 4 }$

$\text { First fundamental theorem of calculus }$

Let $f$ be a continuous function on $[a, b]$. For $x \in [a, b]$, define

$F(x) := \int_{a}^{x} f(t) dt$

Then, $F$ is differentiable on $[a, b]$ and

$F'(x) = f(x)$ for all $x \in [a, b]$.

$\text { Separable ODE }$

An ordinary differential equation of the form

$M(x) + N(y) \frac{dy}{dx} = 0$

is called a separable ODE, where $M$ and $N$ are functions of $x$ and $y$, respectively.

Let $H_1(x)$ and $H_2(y)$ be any functions such that

$H_1'(x) = M(x)$ and $H_2'(y) = N(y)$

Using the chain rule,

$\frac{d}{dx} (H_2(y)) = H_2'(y) \frac{dy}{dx}$

Thus,

$H_1'(x) + H_2'(y) y = 0$

This completes the solution.

