---
course: "Measure and Probability"
source_file: "Continuous mixing of two measurable functions is measurable.pdf"
tags: ["math", "coursework", "measure-and-probability"]
---

# Continuous mixing of two measurable functions is measurable

<!-- Page 1 -->
Continuous mixing of two measurable function is measurable

25 August 2026 12:03

Thm: Suppose $E \in \mathcal{M}$. Define
$$A := \{f : E \longrightarrow \mathbb{R} \mid f \text{ is measurable}\}$$

Then $(A, +, \cdot)$ is a vector space over $\mathbb{R}$.

$$(f + g)(x) := f(x) + g(x)$$
$c \in \mathbb{R},\ f$
$$(c \cdot f)(x) := c f(x)$$

$F: \mathbb{R} \times \mathbb{R} \xrightarrow[\text{Continuous}]{\quad} \mathbb{R}, \quad f,g: E \xrightarrow[\text{m'ble}]{\quad} \mathbb{R}$

We'll show $h: E \xrightarrow[\text{m'ble}]{\quad} \mathbb{R}$
$$x \longmapsto F(f(x), g(x))$$

Pf: $a \in \mathbb{R}$.
$$\begin{aligned}
A := \{x \in E \mid h(x) > a\} &= \{x \in E \mid F(f(x), g(x)) > a\} \\
&= \{x \in E \mid (f(x), g(x)) \in F^{-1}(a, \infty)\} \\
&\phantom{= \{x \in E \mid (f(x), g(x)) \in {}} \underbrace{\text{open in } \mathbb{R}^2}_{\text{countable union of}} \\
&\phantom{= \{x \in E \mid (f(x), g(x)) \in {}} \underbrace{\phantom{\text{open in } \mathbb{R}^2}}_{\text{open rectangle}} \\
&\phantom{= \{x \in E \mid (f(x), g(x)) \in {}} \bigcup_{n=1}^\infty R_n \\
&= \left\{x \in E \mid (f(x), g(x)) \in \bigcup_{n=1}^\infty R_n\right\} \\
&= \bigcup_{n=1}^\infty \{x \in E \mid (f(x), g(x)) \in R_n\} \\
&= \bigcup_{n=1}^\infty \left\{x \in E \mid (f(x), g(x)) \in (a_1^{(n)}, b_1^{(n)}) \times (a_2^{(n)}, b_2^{(n)})\right\}
\end{aligned}$$

New Section 1 Page 1

<!-- Page 2 -->
$$\begin{aligned}
&= \bigcup_{n=1}^\infty \left\{x \in E \mid (f(x), g(x)) \in (a_1^{(n)}, b_1^{(n)}) \times (a_2^{(n)}, b_2^{(n)})\right\} \\
&\phantom{= \bigcup_{n=1}^\infty \{x \in E \mid (f(x), g(x)) \in (a_1^{(n)}, b_1^{(n)}) \times (a_2^{(n)}, b_2^{(n)}) \text{ where } R_n = (a_1^{(n)}, b_1^{(n)}) \times (a_2^{(n)}, b_2^{(n)})\}} \text{where } R_n = (a_1^{(n)}, b_1^{(n)}) \times (a_2^{(n)}, b_2^{(n)}). \\
&= \bigcup_{n=1}^\infty \{x \in E \mid f(x) \in (a_1^{(n)}, b_1^{(n)}), g(x) \in (a_2^{(n)}, b_2^{(n)})\} \\
&= \bigcup_{n=1}^\infty \left( \{x \in E \mid f(x) \in (a_1^{(n)}, b_1^{(n)})\} \cap \{x \in E \mid g(x) \in (a_2^{(n)}, b_2^{(n)})\}\right) \\
&= \bigcup_{n=1}^\infty \left( f^{-1}(a_1^{(n)}, b_1^{(n)}) \cap g^{-1}(a_2^{(n)}, b_2^{(n)})\right) \in \mathcal{M}.
\end{aligned}$$

New Section 1 Page 2

