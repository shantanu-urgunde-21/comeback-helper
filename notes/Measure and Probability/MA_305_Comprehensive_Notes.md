---
course: "Measure and Probability"
source_file: "MA_305_Comprehensive_Notes.pdf"
tags: ["math", "coursework", "measure-and-probability"]
---

# MA_305_Comprehensive_Notes

<!-- Page 1 -->

# Measure and Probability (MA 305)

## Condensed Comprehensive Course Treatise
*From Riemann's Breakdown to Lebesgue Integration & Measurable Dynamics*

### IIT Goa Course Compendium
Complete Synthesis with Extended Pedagogical Guides

Academic Year 2025–2026

#### Abstract
This monograph synthesizes and consolidates the entire lecture series of MA 305 (Measure and Probability) spanning: (1) Revision of the Classical Riemann Integral and Its Critical Points of Failure, (2) Null Sets and Singular Geometries (Cantor Set), (3) Axiomatic Wish-Lists and Vitali's Impossibility Theorem, (4) Lebesgue Outer Measure and Carathéodory's Measurability Criterion, (5) Abstract $\sigma$-Algebras, Pullback/Pushforward Dynamics, and Measure Space Completion, and (6) Measurable Functions, Extended-Real Extremes, Pointwise Limits, and the Devil's Staircase. Every incremental slide variation has been condensed into unified, unified theorems without omission. For students who are new to measure theory, detailed intuition callouts, plain-language translations of abstract notation, and pedagogical visual diagrams are embedded throughout.

## Contents

**1 Introduction & Guide to Abstract Notation** **3**

**2 Lecture 1: The Riemann Integral & Why It Breaks Down** **4**  
2.1 Darboux Partitions, Upper and Lower Sums . . . . . . . . . . . . . . . . . . . . . . . . . . . 4  
2.2 Classical Results of Riemann Integration . . . . . . . . . . . . . . . . . . . . . . . . . . . . 5  
2.3 Two Fatal Flaws of Riemann's Formulation . . . . . . . . . . . . . . . . . . . . . . . . . . . 5  
2.3.1 Flaw 1: Pathological Discontinuity (The Dirichlet Function) . . . . . . . . . . . . 5  
2.3.2 Flaw 2: Breakdown Under Pointwise Limits . . . . . . . . . . . . . . . . . . . . . 5  
2.4 Lebesgue's Insight: Cutting the Range Instead of the Domain . . . . . . . . . . . . . . . . . 6  

**3 Lecture 2: Null Sets & The Singular Cantor Set** **8**  
3.1 Probability Motivation: Singletons in Continuous Spaces . . . . . . . . . . . . . . . . . . . . 8  
3.2 Definition and Arithmetic of Null Sets . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8  
3.3 The Cantor Middle-Third Set: An Uncountable Null Set . . . . . . . . . . . . . . . . . . . . 9  

**4 Lecture 3: The Measure Wish-List & Vitali's Impossibility Theorem** **10**  
4.1 The Four Demands for a Length Measure . . . . . . . . . . . . . . . . . . . . . . . . . . . 10  
4.2 Vitali's Construction of a Non-Measurable Set (1905) . . . . . . . . . . . . . . . . . . . . . 10  
4.3 Which Axiom Must Be Sacrificed? . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 12  

**5 Lecture 4: Lebesgue Outer Measure & Carathéodory's Split** **13**  
5.1 Definition of Lebesgue Outer Measure . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 13  
5.2 Carathéodory's Measurability Criterion . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 13  
5.3 Fundamental Classes of Measurable Sets . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14  

1

<!-- Page 2 -->

MA 305: Measure & Probability — Condensed Course Notes \hfill 2

---

**6 Lecture 5: $\sigma$-Algebras, Constructions, & Completion** **16**  
6.1 Abstract $\sigma$-Algebras . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 16  
6.2 The Borel $\sigma$-Algebra . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 16  
6.3 Pullback and Pushforward Constructions . . . . . . . . . . . . . . . . . . . . . . . . . . . . 17  
6.4 Measure Space Completion: $\mathcal{M} = \text{Completion}(\mathcal{B})$ . . . . . . . . . . . . . . . . . . . . . . . 17  

**7 Lecture 6: Measurable Functions, Limits, & The Devil's Staircase** **19**  
7.1 Definition and Equivalent Characterizations . . . . . . . . . . . . . . . . . . . . . . . . . . 19  
7.2 Algebra of Measurable Functions . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19  
7.3 Positive and Negative Parts of a Function . . . . . . . . . . . . . . . . . . . . . . . . . . . . 20  
7.4 Sequences of Functions: Supremum, Infimum, and Pointwise Limits . . . . . . . . . . . . . . 20  
7.5 The Devil's Staircase (Cantor Ternary Function) . . . . . . . . . . . . . . . . . . . . . . . . 21  

**8 Comprehensive Topic Synthesis & Study Map** **22**

<!-- Page 3 -->

MA 305: Measure & Probability — Condensed Course Notes \hfill 3

---

## 1 Introduction & Guide to Abstract Notation

Measure theory often seems intimidating to newcomers because familiar intuitive notions (such as "area", "length", and "volume") are recast in the language of point-set topology, boolean operations, and abstract functionals. Below is a translation guide for the core notation used throughout these notes:

> ### Deciphering Core Notational Conventions
> 
> - $\mathcal{P}(X)$: The **Power Set** of $X$, i.e., the set of all possible subsets of $X$. If $|X| = n$, then $|\mathcal{P}(X)| = 2^n$.
> 
> - $E^c$ or $X \setminus E$: The **Complement** of set $E$ relative to $X$, representing all points in $X$ that are *not* in $E$.
> 
> - $A \sqcup B$: A **Disjoint Union**, meaning $A \cup B$ under the strict assumption that $A \cap B = \emptyset$.
> 
> - $\mathbf{1}_E$ or $\chi_E$: The **Indicator Function** (or characteristic function) of $E$, defined by $\mathbf{1}_E(x) = 1$ if $x \in E$ and $0$ if $x \notin E$.
> 
> - $f^{-1}(B)$: The **Preimage** (or inverse image) of $B \subseteq Y$ under $f : X \to Y$, defined as $\{x \in X : f(x) \in B\}$. *Warning: $f$ does **not** need to be invertible for $f^{-1}(B)$ to exist!*
> 
> - $\lim_{n \to \infty} \sup f_n$ ($\limsup$) and $\lim_{n \to \infty} \inf f_n$ ($\liminf$): The largest and smallest accumulation limits of an oscillating sequence of functions.
> 
> - $\sigma(\mathcal{E})$: The **$\sigma$-algebra generated by $\mathcal{E}$**, which is the smallest $\sigma$-algebra containing all collections in $\mathcal{E}$.
> 
> - $E_n \uparrow E$ (Continuity from below): An increasing sequence of nested sets $E_1 \subseteq E_2 \subseteq \dots$ whose union is $\bigcup_{n=1}^\infty E_n = E$.
> 
> - $E_n \downarrow E$ (Continuity from above): A decreasing sequence of nested sets $E_1 \supseteq E_2 \supseteq \dots$ whose intersection is $\bigcap_{n=1}^\infty E_n = E$.

<!-- Page 4 -->
MA 305: Measure & Probability --- Condensed Course Notes &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 4

## 2 Lecture 1: The Riemann Integral & Why It Breaks Down

### 2.1 Darboux Partitions, Upper and Lower Sums

The classical Riemann integral seeks to calculate the area under the curve of a bounded function $f:[a, b]\rightarrow\mathbb{R}$ by slicing its domain $[a, b]$ into vertical strips.

**Definition 2.1** (Partition & Darboux Sums). Let $[a, b]$ be a compact interval ($a < b$).

1. A **partition** $P$ of $[a, b]$ is a finite ordered subset $P = \{a = x_0 < x_1 < x_2 < \dots < x_n = b\}$.
2. For each subinterval $I_i = [x_{i-1}, x_i]$, its length is $\Delta x_i = x_i - x_{i-1}$.
3. The local supremum and infimum on subinterval $I_i$ are denoted:
   $$M_i = \sup_{x \in I_i} f(x), \qquad m_i = \inf_{x \in I_i} f(x)$$
4. The **Upper Darboux Sum** $U(f, P)$ and **Lower Darboux Sum** $L(f, P)$ are defined as:
   $$U(f, P) = \sum_{i=1}^n M_i \Delta x_i, \qquad L(f, P) = \sum_{i=1}^n m_i \Delta x_i$$

**Proposition 2.2** (Ordering Property). *For any partition $P$, $L(f, P) \leq U(f, P)$. Furthermore, if $P^*$ is a refinement of $P$ ($P \subseteq P^*$), then:*
$$L(f, P) \leq L(f, P^*) \leq U(f, P^*) \leq U(f, P)$$

*Consequently, every lower sum is bounded above by every upper sum across arbitrary partitions $P_1, P_2$: $L(f, P_1) \leq U(f, P_2)$.*

**Definition 2.3** (The Riemann Integral). The **Upper Riemann Integral** and **Lower Riemann Integral** are defined by:
$$\overline{\int_a^b} f(x)\,dx = \inf_P U(f, P), \qquad \underline{\int_a^b} f(x)\,dx = \sup_P L(f, P)$$

Always, $L(f, P) \leq \underline{\int_a^b} f \leq \overline{\int_a^b} f \leq U(f, P)$. The function $f$ is **Riemann integrable** on $[a, b]$ (denoted $f \in \mathcal{R}[a, b]$) if and only if:
$$\underline{\int_a^b} f(x)\,dx = \overline{\int_a^b} f(x)\,dx$$

Their common value is called the Riemann integral, written $\int_a^b f(x)\,dx$.

**Example 2.4** (Canonical Computation): $f(x) = x^2$ on $[0, 1]$. Choose the uniform partition $P_n = \{0, \frac{1}{n}, \frac{2}{n}, \dots, 1\}$. Since $f(x) = x^2$ is strictly increasing, $m_i = f(\frac{i-1}{n}) = (\frac{i-1}{n})^2$ and $M_i = f(\frac{i}{n}) = (\frac{i}{n})^2$. Using $\sum_{k=1}^n k^2 = \frac{n(n+1)(2n+1)}{6}$:
$$L_n = \frac{1}{n} \sum_{k=1}^{n-1} \left(\frac{k}{n}\right)^2 = \frac{(n-1)(2n-1)}{6n^2}, \qquad U_n = \frac{1}{n} \sum_{k=1}^n \left(\frac{k}{n}\right)^2 = \frac{(n+1)(2n+1)}{6n^2}$$

Taking limits as $n \to \infty$: $\lim L_n = \lim U_n = \frac{1}{3}$. Since the limits coincide, $\int_0^1 x^2\,dx = \frac{1}{3}$.

---

<!-- Page 5 -->
MA 305: Measure & Probability --- Condensed Course Notes &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 5

### 2.2 Classical Results of Riemann Integration

**Theorem 2.5** (Standard Integrability Classes). *The following classes of functions on $[a, b]$ are always Riemann integrable:*
1. *Every continuous function $f \in C[a, b]$.*
2. *Every monotonic (increasing or decreasing) function on $[a, b]$.*
3. *Every bounded piecewise continuous function on $[a, b]$ (e.g., $f(x) = x$ for $x < 1/2$, and $x + 1$ for $x \ge 1/2$).*

**Theorem 2.6** (Fundamental Theorems of Calculus). 
1. *$\textbf{FTC Part I}$: If $f : [a, b] \to \mathbb{R}$ is continuous and $F(x) = \int_a^x f(t)\,dt$, then $F$ is differentiable on $(a, b)$ with $F'(x) = f(x)$.*
2. *$\textbf{FTC Part II}$: If $f$ is continuous and $F$ is an antiderivative ($F' = f$), then $\int_a^b f(x)\,dx = F(b) - F(a)$.*
3. *$\textbf{Mean Value Theorem for Integrals}$: If $f$ is continuous, $\exists c \in [a, b]$ such that $\int_a^b f(x)\,dx = f(c)(b - a)$.*

**Theorem 2.7** (Invariance Under Finite Alterations). *Let $f, g : [a, b] \to \mathbb{R}$ be bounded. If $f(x) = g(x)$ except at finitely many points, then $f \in \mathcal{R}[a, b] \iff g \in \mathcal{R}[a, b]$, and when integrable, $\int_a^b f(x)\,dx = \int_a^b g(x)\,dx$.*

### 2.3 Two Fatal Flaws of Riemann's Formulation

Despite its historical power, Riemann integration breaks down under two foundational demands of modern mathematical analysis:

#### 2.3.1 Flaw 1: Pathological Discontinuity (The Dirichlet Function)

Consider the Dirichlet indicator function on $[0, 1]$:
$$f(x) = \mathbf{1}_{\mathbb{Q} \cap [0, 1]}(x) = \begin{cases} 1, & x \in \mathbb{Q} \cap [0, 1] \\ 0, & x \notin \mathbb{Q} \cap [0, 1] \end{cases}$$

By the density of rationals and irrationals, every non-trivial subinterval $I_i = [x_{i-1}, x_i]$ contains points from both $\mathbb{Q}$ and $\mathbb{R} \setminus \mathbb{Q}$. Consequently, *for every partition $P$*:
$$M_i = \sup_{x \in I_i} f(x) = 1, \qquad m_i = \inf_{x \in I_i} f(x) = 0 \implies U(f, P) = \sum 1 \cdot \Delta x_i = 1, \quad L(f, P) = \sum 0 \cdot \Delta x_i = 0$$

Thus $\overline{\int_0^1} f = 1 \neq 0 = \underline{\int_0^1} f$. The function fails to be Riemann integrable.

#### 2.3.2 Flaw 2: Breakdown Under Pointwise Limits

The fatal flaw in analysis is the failure of limits to pass inside the integral. Enumerate all rationals in $[0, 1]$: $\mathbb{Q} \cap [0, 1] = \{q_1, q_2, q_3, \dots\}$, and define the sequence of functions:
$$f_n(x) = \mathbf{1}_{\{q_1, q_2, \dots, q_n\}}(x)$$

* Each $f_n$ is non-zero at only $n$ isolated points (finitely many discontinuities). Thus each $f_n$ is Riemann integrable, and $\int_0^1 f_n(x)\,dx = 0$.
* As $n \to \infty$, $f_n(x)$ increases monotonically and converges pointwise to the Dirichlet function:
  $$f_n(x) \uparrow \mathbf{1}_{\mathbb{Q} \cap [0, 1]}(x) \quad \text{for every } x \in [0, 1]$$

---

<!-- Page 6 -->
MA 305: Measure & Probability --- Condensed Course Notes &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 6

* Yet, the pointwise limit $\lim_{n\to\infty} f_n$ **is not Riemann integrable!**
$$\lim_{n\to\infty} \int_0^1 f_n(x)\,dx = 0 \quad \text{but} \quad \int_0^1 \left(\lim_{n\to\infty} f_n(x)\right) dx \quad \textbf{does not exist in Riemann's theory!}$$

```
                Riemann: Partition Domain (X-Axis)                     |                Lebesgue: Partition Range (Y-Axis)
                    Hostage to local oscillation                       |                 Controlled oscillation on preimages
3.0 --                                                                 |  3.0 --
                                                                       |         Preimage f^{-1}(J_n)
2.5 --                                                                 |  2.5 --
                                                                       |
2.0 --                                                                 |  2.0 --
                                                                       |
1.5 --                                                                 |  1.5 --
                                                                       |
1.0 --                                                                 |  1.0 --
                                                                       |
0.0 --+-------+-------+-------+-------+-------+-------+-------+        |  0.0 --+-------+-------+-------+-------+-------+-------+-------+
     0.5     1.0     1.5     2.0     2.5     3.0     3.5     4.0  4.5  |       0.5     1.0     1.5     2.0     2.5     3.0     3.5     4.0  4.5
                               Domain intervals I_i = [x_{i-1}, x_i]   |                         x (domain elements mapping into J_n)
```

Figure 1: **Domain Partitioning vs. Range Partitioning**. Riemann slices the $x$-axis into intervals $I_i$, making the method hostage to wild oscillations inside each interval. Lebesgue slices the $y$-axis into intervals $J_n$, grouping all points $x$ where $f(x) \in J_n$ together into a preimage set $f^{-1}(J_n)$. Oscillation on each slice is bounded by $|J_n|$ by design.

### 2.4 Lebesgue's Insight: Cutting the Range Instead of the Domain

Lebesgue observed that the breakdown of the Riemann integral stems directly from the geometry of partitioning the domain. If a function jumps wildly between $0$ and $1$ (like $\mathbf{1}_{\mathbb{Q}}$), any interval in the domain contains extreme oscillation.

* **Riemann's Strategy**: Partition the domain: $\sum_i f(\xi_i) |I_i|$. Needs $f$ nearly constant on each $I_i$. Hostage to local oscillation.
* **Lebesgue's Strategy**: Partition the range: choose intervals $J_n \subset \mathbb{R}$ of size $\le \epsilon$, select tags $c_n \in J_n$, and gather all domain points that map into $J_n$:
  $$\sum_n c_n \, m(f^{-1}(J_n))$$

By definition, the oscillation of $f$ on the preimage set $f^{-1}(J_n)$ cannot exceed the width $|J_n|$!

**Example 2.8** (Integrating the Dirichlet Function via Lebesgue's Cut). To integrate $\mathbf{1}_{\mathbb{Q} \cap [0, 1]}$, we partition its range into two intervals:
$$J_1 = \left[-\frac{1}{2}, \frac{1}{2}\right) \quad \text{with tag } c_1 = 0; \quad J_2 = \left[\frac{1}{2}, \frac{3}{2}\right) \quad \text{with tag } c_2 = 1$$

The preimages in the domain $[0, 1]$ are:
$$f^{-1}(J_1) = [0, 1] \setminus \mathbb{Q} \quad (\text{irrationals, size } 1); \quad f^{-1}(J_2) = [0, 1] \cap \mathbb{Q} \quad (\text{rationals, size } 0)$$

The Lebesgue sum computes the exact value immediately without limits:
$$\sum_n c_n \, m(f^{-1}(J_n)) = 0 \cdot m([0, 1] \setminus \mathbb{Q}) + 1 \cdot m([0, 1] \cap \mathbb{Q}) = 0 \cdot 1 + 1 \cdot 0 = 0$$

<!-- Page 7 -->
$$\text{MA 305: Measure \& Probability — Condensed Course Notes} \hfill 7$$

$$\begin{array}{|l|}
\hline
\textbf{The Foundational Question of Measure Theory} \\
\hline
\text{Lebesgue's approach resolves the oscillation issue, but it introduces a crucial prerequisite:} \\
\mathbf{The\ sum\ } \sum c_n m(f^{-1}(J_n))\ \mathbf{only\ makes\ sense\ if\ we\ have\ a\ rigorous\ way\ to\ define} \\
\mathbf{the\ "size"\ or\ "measure"\ } m(E)\ \mathbf{of\ complicated\ sets\ like\ } E = f^{-1}(J_n).\text{ Thus, before} \\
\text{we can integrate, we must develop a theory of measurable sets!} \\
\hline
\end{array}$$

---

<!-- Page 8 -->
$$\text{MA 305: Measure \& Probability — Condensed Course Notes} \hfill 8$$

## 3 Lecture 2: Null Sets & The Singular Cantor Set

### 3.1 Probability Motivation: Singletons in Continuous Spaces

In discrete probability on a finite set $S = \{1, 2, \dots, 10\}$ under a uniform distribution, every singleton has positive probability: $P(\{k\}) = \frac{1}{10}$.

However, when selecting a point uniformly at random from a continuous interval $S = [0, 1]$, there are infinitely many possibilities. If singletons had any positive probability $c > 0$, then choosing $N > \frac{1}{c}$ points would yield a total probability exceeding $1$, which is impossible. Thus:

$$P(\{x\}) = 0 \quad \text{for every individual point } x \in [0, 1]$$

Similarly, any finite set $A = \{x_1, \dots, x_n\}$ has probability $P(A) = \sum_{k=1}^n P(\{x_k\}) = 0$. What happens if a set contains *countably infinitely* many points, such as $\mathbb{Q} \cap [0, 1]$?

### 3.2 Definition and Arithmetic of Null Sets

**Definition 3.1** (Null Set / Measure Zero Set). A subset $E \subseteq \mathbb{R}$ is called a **null set** (or set of measure zero) if for every $\epsilon > 0$, there exists a countable sequence of open intervals $\{I_n\}_{n=1}^\infty$ such that:

$$E \subseteq \bigcup_{n=1}^\infty I_n \quad \text{and} \quad \sum_{n=1}^\infty |I_n| < \epsilon$$

where $|I_n|$ denotes the Euclidean length of the interval $I_n$.

**Proposition 3.2** (Properties of Null Sets). 
1. *Singletons are Null:* For $E = \{a\}$ and $\epsilon > 0$, take $I = (a - \frac{\epsilon}{4}, a + \frac{\epsilon}{4})$. Then $E \subseteq I$ and $|I| = \frac{\epsilon}{2} < \epsilon$.
2. *Subsets of Null Sets are Null:* If $A \subseteq E$ and $E$ is null, any interval cover of $E$ of total length $< \epsilon$ automatically covers $A$.
3. *Countable Unions of Null Sets are Null:* Let $\{E_k\}_{k=1}^\infty$ be null sets. Given $\epsilon > 0$, cover each $E_k$ with intervals $\{I_{k,j}\}_{j=1}^\infty$ such that $\sum_{j=1}^\infty |I_{k,j}| < \frac{\epsilon}{2^k}$. Then the union $\bigcup_{k=1}^\infty E_k$ is covered by the collection $\{I_{k,j}\}_{k,j}$ with total length $\sum_{k=1}^\infty \sum_{j=1}^\infty |I_{k,j}| < \sum_{k=1}^\infty \frac{\epsilon}{2^k} = \epsilon$.

**Theorem 3.3** (Every Countable Set is Null). *Every countable set $E = \{x_1, x_2, x_3, \dots\} \subset \mathbb{R}$ is a null set.*

*Proof.* Given $\epsilon > 0$, surround the $n$-th element $x_n$ with an open interval $I_n = \left(x_n - \frac{\epsilon}{2^{n+2}}, x_n + \frac{\epsilon}{2^{n+2}}\right)$ of length $|I_n| = \frac{\epsilon}{2^{n+1}}$. Then $E \subseteq \bigcup_{n=1}^\infty I_n$, and:

$$\sum_{n=1}^\infty |I_n| = \sum_{n=1}^\infty \frac{\epsilon}{2^{n+1}} = \frac{\epsilon}{2} < \epsilon$$

Thus $E$ is null. $\square$

**Corollary 3.4.** The set of rational numbers inside $[0, 1]$, $\mathbb{Q} \cap [0, 1]$, is countable and therefore null. Under the uniform distribution on $[0, 1]$, $P(\mathbb{Q} \cap [0, 1]) = 0$. Consequently, a uniformly chosen real number in $[0, 1]$ is irrational with probability $1$.

$$\begin{array}{|l|}
\hline
\textbf{Density vs. Measure: A Vital Distinction} \\
\hline
\mathbb{Q} \cap [0, 1]$ is topologically \textbf{dense} in $[0, 1]$: every real number has rationals arbitrarily close \\
to it. Yet, its total ``size'' (measure) is zero! Measure does not care about topological \\
density; it cares about containment volume. \\
\hline
\end{array}$$

---

<!-- Page 9 -->
$$\text{MA 305: Measure \& Probability — Condensed Course Notes} \hfill 9$$

$$\text{Cantor Middle-Third Set Construction (Total remaining measure} \to 0\text{)}$$

$$\begin{array}{r@{\quad}l}
C\_0 \text{ (rem: } (2/3)^0\text{)} & \rule{10cm}{2pt} \\
C\_1 \text{ (rem: } (2/3)^1\text{)} & \rule{4.5cm}{2pt} \hspace{0.5cm} \rule{4.5cm}{2pt} \\
C\_2 \text{ (rem: } (2/3)^2\text{)} & \rule{2cm}{2pt} \hspace{0.5cm} \rule{2cm}{2pt} \hspace{1.5cm} \rule{2cm}{2pt} \hspace{0.5cm} \rule{2cm}{2pt} \\
C\_3 \text{ (rem: } (2/3)^3\text{)} & \rule{0.8cm}{2pt} \hspace{0.4cm} \rule{0.8cm}{2pt} \hspace{0.8cm} \rule{0.8cm}{2pt} \hspace{0.4cm} \rule{0.8cm}{2.pt} \hspace{1.9cm} \rule{0.8cm}{2pt} \hspace{0.4cm} \rule{0.8cm}{2pt} \hspace{0.8cm} \rule{0.8cm}{2pt} \hspace{0.4cm} \rule{0.8cm}{2pt} \\
& \underset{0}{\perp} \hspace{6.3cm} \underset{1/3}{\perp} \hspace{4.4cm} \underset{2/3}{\perp} \hspace{4.4cm} \underset{1}{\perp}
\end{array}$$

**Figure 2:** **Cantor Middle-Third Set Construction.** Starting from $C_0 = [0, 1]$, successive open middle thirds are removed. At stage $n$, $2^n$ closed intervals of length $3^{-n}$ remain, yielding a total length of $(2/3)^n \to 0$.

### 3.3 The Cantor Middle-Third Set: An Uncountable Null Set

Is every null set countable? The answer is an **emphatic no**. The canonical counterexample is the Cantor middle-third set $\mathcal{C}$.

**Definition 3.5** (Cantor Set Construction). 
* Stage $0$: $C_0 = [0, 1]$.
* Stage $1$: Remove the open middle third $(\frac{1}{3}, \frac{2}{3})$: $C_1 = [0, \frac{1}{3}] \cup [\frac{2}{3}, 1]$.
* Stage $n$: Remove the open middle third of each of the $2^{n-1}$ intervals of $C_{n-1}$. What remains is $C_n$, consisting of $2^n$ disjoint closed intervals, each of length $3^{-n}$.
  The **Cantor Set** is the intersection of all stages: $\mathcal{C} = \bigcap_{n=0}^\infty C_n$.

**Theorem 3.6** ($\mathcal{C}$ is Null and Uncountable). 
1. $\mathcal{C}$ is a Null Set: *The total length of intervals comprising $C_n$ is $2^n \times 3^{-n} = \left(\frac{2}{3}\right)^n$. Given $\epsilon > 0$, choose $n$ large enough that $(2/3)^n < \epsilon$. Since $\mathcal{C} \subseteq C_n$, $\mathcal{C}$ is covered by intervals of total length $< \epsilon$.*
2. $\mathcal{C}$ is Uncountable: *Every point $x \in [0, 1]$ can be written in base-$3$ (ternary): $x = \sum_{k=1}^\infty \frac{a_k}{3^k}$ where $a_k \in \{0, 1, 2\}$. Removing middle thirds is equivalent to removing numbers whose ternary expansion requires the digit $1$. Thus, $\mathcal{C}$ consists precisely of all numbers in $[0, 1]$ whose ternary expansion contains only $0\text{s}$ and $2\text{s}$. Replacing each $2$ with a $1$ produces a bijection from $\mathcal{C}$ onto the set of all binary expansions of numbers in $[0, 1]$. Therefore, $|\mathcal{C}| = |[0, 1]| = 2^{\aleph_0}$ (uncountable).*

$$\begin{array}{|l|cc|}
\hline
\textbf{Set} & \textbf{Countable?} & \textbf{Null (Measure Zero)?} \\
\hline
\text{Singleton } \{x\} & \text{Yes} & \text{Yes} \\
\text{Finite set } F & \text{Yes} & \text{Yes} \\
\text{Natural numbers } \mathbb{N} & \text{Yes} & \text{Yes} \\
\text{Rational numbers } \mathbb{Q} & \text{Yes} & \text{Yes} \\
\text{Cantor Set } \mathcal{C} & \textbf{No} & \textbf{Yes} \\
\text{Unit interval } [0, 1] & \text{No} & \text{No} \\
\hline
\end{array}$$

$$\text{Table 1: Classification of Cardinality vs. Null Measure.}$$

<!-- Page 10 -->
$$\text{MA 305: Measure \& Probability — Condensed Course Notes}$$

# 4 Lecture 3: The Measure Wish-List \& Vitali’s Impossibility Theorem

## 4.1 The Four Demands for a Length Measure

We want to construct a map $m: \mathcal{P}(\mathbb{R}) \to [0, +\infty]$ generalizing Euclidean interval length. We require four natural properties:

* **(M1) Universality:** $m(E)$ is defined for \emph{every} subset $E \subseteq \mathbb{R}$.
* **(M2) Normalization:** For every bounded interval $I$, $m(I) = \ell(I) = b - a$.
* **(M3) Countable Additivity:** If $\{E_n\}_{n=1}^{\infty}$ are pairwise disjoint sets ($E_i \cap E_j = \emptyset$ for $i \neq j$), then:
  $$m\left(\bigcup_{n=1}^{\infty} E_n\right) = \sum_{n=1}^{\infty} m(E_n)$$
* **(M4) Translation Invariance:** For every $E \subseteq \mathbb{R}$ and $x \in \mathbb{R}$, $m(E + x) = m(E)$, where $E + x = \{e + x : e \in E\}$.

**Proposition 4.1** (Free Properties from (M1)–(M4)).
1. $m(\emptyset) = 0$ (otherwise $m(\emptyset) = m(\emptyset) + m(\emptyset) \implies m(\emptyset) \in \{0, \infty\}$; if $\infty$, then $m(I) = \infty$, violating (M2)).
2. Finite additivity: $m(\bigsqcup_{k=1}^n E_k) = \sum_{k=1}^n m(E_k)$ (pad with empty sets).
3. Monotonicity: If $A \subseteq B$, write $B = A \sqcup (B \setminus A) \implies m(B) = m(A) + m(B \setminus A) \ge m(A)$.
4. Countable subadditivity: $m(\bigcup_n E_n) \le \sum_n m(E_n)$ (via disjointification $F_n = E_n \setminus \bigcup_{k=1}^{n-1} E_k$).

## 4.2 Vitali's Construction of a Non-Measurable Set (1905)

**Theorem 4.2** (Vitali's Impossibility Theorem). There does \textbf{not} exist any set function $m : \mathcal{P}(\mathbb{R}) \to [0, +\infty]$ satisfying demands (M1), (M2), (M3), and (M4) simultaneously. The four axioms are mutually contradictory!

\emph{Complete Step-by-Step Proof.} **Step 1: Construct the Equivalence Relation.** Define a relation $\sim$ on $[0, 1]$ by:
$$x \sim y \iff x - y \in \mathbb{Q}$$

This is an equivalence relation:
* Reflexive: $x - x = 0 \in \mathbb{Q}$.
* Symmetric: $x - y \in \mathbb{Q} \implies y - x = -(x - y) \in \mathbb{Q}$.
* Transitive: $x - y \in \mathbb{Q}$ and $y - z \in \mathbb{Q} \implies x - z = (x - y) + (y - z) \in \mathbb{Q}$.

Thus, $[0, 1]$ is partitioned into disjoint equivalence classes $[x] = (x + \mathbb{Q}) \cap [0, 1]$. Each class is countable and dense in $[0, 1]$. Since $[0, 1]$ is uncountable, there are uncountably many such classes.

**Step 2: Choose the Vitali Set $V$.** By the \textbf{Axiom of Choice}, select exactly one representative point from each equivalence class to form a set $V \subset [0, 1]$.

**Step 3: Enumerate Rational Translates.** Enumerate the countable set of rationals in $[-1, 1]$:
$$Q = \mathbb{Q} \cap [-1, 1] = \{q_1, q_2, q_3, \dots\}$$

For each $q \in Q$, define the translate $V_q = V + q = \{v + q : v \in V\}$.

**Step 4: Three Fundamental Geometric Facts.**

<!-- Page 11 -->
$$\text{MA 305: Measure \& Probability — Condensed Course Notes}$$

1. \textbf{Pairwise Disjointness:} If $q \neq q'$, then $V_q \cap V_{q'} = \emptyset$. Suppose $x \in V_q \cap V_{q'}$. Then $x = v + q = v' + q'$ for $v, v' \in V$. Hence $v - v' = q' - q \in \mathbb{Q}$, meaning $v \sim v'$. But $V$ contains exactly one element from each equivalence class, so $v = v'$, forcing $q = q'$, a contradiction.
2. \textbf{The Translates Cover $[0, 1]$:} For any $x \in [0, 1]$, its equivalence class $[x]$ has a representative $v \in V$. Thus $x - v = q \in \mathbb{Q}$. Since $x, v \in [0, 1]$, we have $-1 \le x - v \le 1$, meaning $q \in Q$. Therefore, $x = v + q \in V_q$, establishing $[0, 1] \subseteq \bigcup_{q \in Q} V_q$.
3. \textbf{The Translates Stay Bounded:} For any $x \in V_q$, $x = v + q$ with $v \in [0, 1]$ and $q \in [-1, 1]$. Hence $-1 \le x \le 2$. Thus $\bigcup_{q \in Q} V_q \subseteq [-1, 2]$.

$$\text{The Vitali Sandwich: } [0, 1] \subseteq \bigcup_{q \in Q} V_q \subseteq [-1, 2]$$

$$
\begin{tikzpicture}
\node[above] at (0, 0.5) {\tiny $\text{Disjoint Union } \bigcup_{q \in Q} V_q$};
\draw[line width=1mm, red] (-1, 0) -- (2, 0);
\foreach \x in {-0.8, -0.4, 0.0, 0.4, 0.8, 1.2, 1.6} {
    \draw[line width=0.5mm, dashed, blue!50!black] (\x, -0.2) -- (\x + 0.3, -0.2);
}
\draw[line width=1mm, green!40!black] (0, -0.5) -- (1, -0.5);
\draw[line width=1mm, red] (-1, -0.5) -- (2, -0.5);
\node[below] at (0.5, -0.5) {\tiny $[0, 1] \, (\text{Length} = 1)$};
\node[below] at (0.5, -0.8) {\tiny $[-1, 2] \, (\text{Length} = 3)$};
\node[below] at (-1, -1.2) {\tiny $-1$};
\node[below] at (0, -1.2) {\tiny $0$};
\node[below] at (1, -1.2) {\tiny $1$};
\node[below] at (2, -1.2) {\tiny $2$};
\draw[->] (-1.5, -1) -- (2.5, -1);
\end{tikzpicture}
$$

**Figure 3: The Vitali Sandwich.** A countable disjoint union of identical translates $\bigsqcup_{q \in Q} V_q$ is trapped between $[0, 1]$ (measure 1) and $[-1, 2]$ (measure 3).

**Step 5: The Contradiction via Monotonic Squeeze.** We have trapped the countable disjoint union:
$$[0, 1] \subseteq \bigsqcup_{q \in Q} V_q \subseteq [-1, 2]$$

Assuming $m$ exists on all sets:
* By (M1), $V$ has a measure, say $m(V) = a \in [0, +\infty]$.
* By translation invariance (M4), $m(V_q) = m(V + q) = m(V) = a$ for all $q \in Q$.
* By countable additivity (M3), the measure of the disjoint union is:
  $$m\left(\bigsqcup_{q \in Q} V_q\right) = \sum_{q \in Q} m(V_q) = \sum_{n=1}^{\infty} a$$
* Applying monotonicity (Property 3) and normalization (M2) to the sandwich:
  $$m([0, 1]) \le m\left(\bigsqcup_{q \in Q} V_q\right) \le m([-1, 2]) \implies 1 \le \sum_{n=1}^{\infty} a \le 3$$

The series $\sum_{n=1}^{\infty} a$ has only two possibilities:
* If $a = 0$: $\sum_{n=1}^{\infty} 0 = 0 \ge 1$ (False: $V$ is "too small").
* If $a > 0$: $\sum_{n=1}^{\infty} a = +\infty \le 3$ (False: $V$ is "too big").

Both cases yield a contradiction. No such measure $m$ can exist! $\square$

<!-- Page 12 -->
$$\text{MA 305: Measure \& Probability — Condensed Course Notes}$$

## 4.3 Which Axiom Must Be Sacrificed?

* \textbf{Drop Normalization (M2)?} Then $m \equiv 0$ works, but it measures nothing.
* \textbf{Drop Translation Invariance (M4)?} Useful in general probability, but not for geometric length.
* \textbf{Drop Countable Additivity (M3)?} Banach showed finitely additive measures exist, but without countable additivity, limit theorems and analysis fail.
* \textbf{Drop Universality (M1): This is the path of modern analysis.} We do \emph{not} attempt to measure every subset of $\mathbb{R}$. We construct a distinguished collection $\mathcal{M} \subsetneq \mathcal{P}(\mathbb{R})$ of \textbf{measurable sets}. The Vitali set $V$ is excluded: $V \notin \mathcal{M}$.

<!-- Page 13 -->
MA 305: Measure & Probability --- Condensed Course Notes 13

# 5 Lecture 4: Lebesgue Outer Measure & Carathéodory's Split

## 5.1 Definition of Lebesgue Outer Measure

Since we cannot assign an additive measure to every set, we begin with a looser set function defined on all subsets that satisfies monotonicity and subadditivity, but relaxes strict additivity.

**Definition 5.1** (Lebesgue Outer Measure). For any subset $E \subseteq \mathbb{R}$, the **Lebesgue outer measure** $m^*(E) \in [0, \infty]$ is:
$$m^*(E) = \inf \left\{ \sum_{k=1}^\infty \ell(I_k) : E \subseteq \bigcup_{k=1}^\infty I_k, I_k \text{ open intervals} \right\}$$

**Remark 5.2** (Well-Definedness). Since $\mathbb{R} = \bigcup_{n=1}^\infty (-n, n)$, every set $E$ has at least one valid countable open cover. The set of covering lengths is non-empty and bounded below by $0$, so the infimum exists in $[0, \infty]$. Furthermore, replacing open intervals with closed intervals yields the exact same infimum.

**Proposition 5.3** (Properties of Outer Measure).
1. $m^*(\emptyset) = 0$ and $m^*(\{x\}) = 0$.
2. **Monotonicity**: $A \subseteq B \implies m^*(A) \le m^*(B)$.
3. **Translation Invariance**: $m^*(E + x) = m^*(E)$ for all $x \in \mathbb{R}$.
4. **Countable Subadditivity**: For any sequence of sets $\{E_n\}_{n=1}^\infty \subseteq \mathcal{P}(\mathbb{R})$:
   $$m^* \left( \bigcup_{n=1}^\infty E_n \right) \le \sum_{n=1}^\infty m^*(E_n)$$

*Proof of Countable Subadditivity.* If $\sum_n m^*(E_n) = \infty$, the inequality is trivially true. Assume $\sum_n m^*(E_n) < \infty$. Fix $\epsilon > 0$. For each $n \in \mathbb{N}$, choose an open interval cover $E_n \subseteq \bigcup_{k=1}^\infty I_{n,k}$ such that:
$$\sum_{k=1}^\infty \ell(I_{n,k}) \le m^*(E_n) + \frac{\epsilon}{2^n}$$

The double collection $\{I_{n,k}\}_{n,k=1}^\infty$ is countable and covers $\bigcup_{n=1}^\infty E_n$. By the definition of the infimum:
$$m^* \left( \bigcup_{n=1}^\infty E_n \right) \le \sum_{n=1}^\infty \sum_{k=1}^\infty \ell(I_{n,k}) \le \sum_{n=1}^\infty \left( m^*(E_n) + \frac{\epsilon}{2^n} \right) = \sum_{n=1}^\infty m^*(E_n) + \epsilon$$

Since $\epsilon > 0$ was arbitrary, the result follows. $\square$

## 5.2 Carathéodory's Measurability Criterion

How do we identify which sets are "clean" and belong to $\mathcal{M}$? Carathéodory (1914) introduced the following criterion:

**Definition 5.4** (Carathéodory Measurability). A set $E \subseteq \mathbb{R}$ is said to be **Lebesgue measurable** ($E \in \mathcal{M}$) if for *every* test set $A \subseteq \mathbb{R}$:
$$m^*(A) = m^*(A \cap E) + m^*(A \cap E^c)$$

---
<!-- Page 14 -->
MA 305: Measure & Probability --- Condensed Course Notes 14

### Geometric Interpretation of Carathéodory

Think of $E$ as a razor blade. When you drop any arbitrary set $A$ on $E$, $E$ cleanly cuts $A$ into two pieces: the part inside $E$ ($A \cap E$) and the part outside $E$ ($A \cap E^c$). If the outer measures add up with no loss or interference for *every possible* test set $A$, then $E$ is declared measurable.

---

**Remark 5.5** (The One-Sided Simplification). By subadditivity, $m^*(A) \le m^*(A \cap E) + m^*(A \cap E^c)$ is **always true** for every set. Therefore, to prove $E \in \mathcal{M}$, one only needs to verify the reverse inequality:
$$m^*(A) \ge m^*(A \cap E) + m^*(A \cap E^c) \quad \text{for all } A \subseteq \mathbb{R} \text{ with } m^*(A) < \infty$$

## 5.3 Fundamental Classes of Measurable Sets

**Proposition 5.6.**
1. $\emptyset \in \mathcal{M}$ and $\mathbb{R} \in \mathcal{M}$.
2. $E \in \mathcal{M} \iff E^c \in \mathcal{M}$ (Carathéodory's condition is symmetric in $E$ and $E^c$).
3. **Null Sets are Measurable**: If $m^*(E) = 0$, then $E \in \mathcal{M}$.

*Proof.* For any test set $A$, $A \cap E \subseteq E \implies m^*(A \cap E) \le m^*(E) = 0$. Furthermore, $A \cap E^c \subseteq A \implies m^*(A \cap E^c) \le m^*(A)$. Thus:
$$m^*(A \cap E) + m^*(A \cap E^c) \le 0 + m^*(A) = m^*(A) \implies E \in \mathcal{M}$$
$\square$

**Theorem 5.7** (Intervals are Measurable). Every ray of the form $(a, \infty)$ is measurable: $(a, \infty) \in \mathcal{M}$.

*Proof.* Let $A \subseteq \mathbb{R}$ with $m^*(A) < \infty$. Given $\epsilon > 0$, cover $A \subseteq \bigcup_k I_k$ with $\sum \ell(I_k) \le m^*(A) + \epsilon$. For each interval $I_k$, slice it at $a$:
$$I'_k = I_k \cap (a, \infty), \quad I''_k = I_k \cap (-\infty, a] \implies \ell(I'_k) + \ell(I''_k) = \ell(I_k)$$

The family $\{I'_k\}$ covers $A \cap (a, \infty)$ and $\{I''_k\}$ covers $A \cap (-\infty, a]$. Therefore:
$$m^*(A \cap (a, \infty)) + m^*(A \cap (-\infty, a]) \le \sum_k \ell(I'_k) + \sum_k \ell(I''_k) = \sum_k \ell(I_k) \le m^*(A) + \epsilon$$

Since $\epsilon > 0$ is arbitrary, $(a, \infty) \in \mathcal{M}$. $\square$

**Theorem 5.8** ($\mathcal{M}$ is Closed Under Finite Unions). If $E_1, E_2 \in \mathcal{M}$, then $E_1 \cup E_2 \in \mathcal{M}$.

*Proof.* Apply the Carathéodory condition of $E_2$ using test set $A \cap E_1^c$:
$$m^*(A \cap E_1^c) = m^*(A \cap E_1^c \cap E_2) + m^*(A \cap E_1^c \cap E_2^c)$$

Insert this into the Carathéodory split for $E_1$:
$$m^*(A) = m^*(A \cap E_1) + m^*(A \cap E_1^c \cap E_2) + m^*(A \cap (E_1 \cup E_2)^c)$$

By subadditivity, $m^*(A \cap E_1) + m^*(A \cap E_1^c \cap E_2) \ge m^*(A \cap (E_1 \cup E_2))$. Thus:
$$m^*(A) \ge m^*(A \cap (E_1 \cup E_2)) + m^*(A \cap (E_1 \cup E_2)^c) \implies E_1 \cup E_2 \in \mathcal{M}$$
$\square$

---
<!-- Page 15 -->
MA 305: Measure & Probability --- Condensed Course Notes 15

**Theorem 5.9** (Disjoint Additivity on Test Sets). Let $\{E_k\}_{k=1}^n$ be pairwise disjoint measurable sets. Then for any test set $A \subseteq \mathbb{R}$:
$$m^*(A) = \sum_{k=1}^n m^*(A \cap E_k) + m^* \left( A \cap \left( \bigcup_{k=1}^n E_k \right)^c \right)$$

**Definition 5.10** (Lebesgue Measure Space). Restricting outer measure $m^*$ to the collection $\mathcal{M}$ gives the **Lebesgue measure** $m = m^*|_{\mathcal{M}}$. The triple $(\mathbb{R}, \mathcal{M}, m)$ forms the complete Lebesgue measure space.

**Proposition 5.11** (Continuity Properties of Lebesgue Measure).
1. **Excision**: If $E \subseteq F$ with $m(E) < \infty$, then $m(F \setminus E) = m(F) - m(E)$.
2. **Continuity from Below**: If $E_1 \subseteq E_2 \subseteq \dots$ and $E = \bigcup_n E_n$, then $\lim_{n \to \infty} m(E_n) = m(E)$.
3. **Continuity from Above**: If $E_1 \supseteq E_2 \supseteq \dots$, $E = \bigcap_n E_n$, **and** $m(E_1) < \infty$, then $\lim_{n \to \infty} m(E_n) = m(E)$.

**Remark 5.12** (Finiteness in Continuity from Above is Essential). Consider $E_n = [n, \infty)$. We have $E_1 \supseteq E_2 \supseteq \dots \downarrow \emptyset$, so $m(\bigcap E_n) = m(\emptyset) = 0$. However, $m(E_n) = \infty$ for all $n$, so $\lim_{n \to \infty} m(E_n) = \infty \neq 0$. The condition $m(E_1) < \infty$ cannot be omitted.

<!-- Page 16 -->
MA 305: Measure & Probability --- Condensed Course Notes
16

# 6 Lecture 5: $\sigma$-Algebras, Constructions, & Completion

## 6.1 Abstract $\sigma$-Algebras

**Definition 6.1** ($\sigma$-Algebra). Let $X$ be a set. A collection $\mathcal{A} \subseteq \mathcal{P}(X)$ is called a $\sigma$-algebra on $X$ if:

1. $\emptyset \in \mathcal{A}$ (contains empty set).
2. $E \in \mathcal{A} \implies E^c \in \mathcal{A}$ (closed under complementation).
3. $\{E_n\}_{n=1}^\infty \subseteq \mathcal{A} \implies \bigcup_{n=1}^\infty E_n \in \mathcal{A}$ (closed under countable unions).

An **algebra** satisfies (1), (2), and closure under *finite* unions only.

**Example 6.2** (Canonical Examples & Near Misses).
1. **Trivial & Discrete:** $\mathcal{A}_{\text{triv}} = \{\emptyset, X\}$ (smallest) and $\mathcal{A}_{\text{pow}} = \mathcal{P}(X)$ (largest).
2. **Generated by a Single Set:** For $\emptyset \neq E \neq X$, $\sigma(\{E\}) = \{\emptyset, E, E^c, X\}$.
3. **Generated by a Finite Partition:** If $X = \bigsqcup_{i=1}^n A_i$, then $\sigma(\{A_1, \dots, A_n\})$ has exactly $2^n$ elements, formed by arbitrary unions of the atoms $A_i$.
4. **Countable-Cocountable $\sigma$-Algebra:** $\mathcal{A} = \{E \subseteq X : E \text{ is countable or } E^c \text{ is countable}\}$ is a $\sigma$-algebra.
5. **Near Miss 1 (Finite-Cofinite):** $\mathcal{A}_0 = \{E \subseteq \mathbb{R} : E \text{ finite or } E^c \text{ finite}\}$ is an algebra, but **not** a $\sigma$-algebra, because $\mathbb{N} = \bigcup_{n=1}^\infty \{n\} \notin \mathcal{A}_0$.
6. **Near Miss 2 (Increasing Union):** If $\mathcal{A}_1 \subseteq \mathcal{A}_2 \subseteq \dots$ are $\sigma$-algebras, their union $\bigcup_{n=1}^\infty \mathcal{A}_n$ is generally **not** a $\sigma$-algebra (e.g., $\mathcal{A}_n = \sigma(\{1\}, \dots, \{n\})$ on $\mathbb{N}$; the set of even numbers is not in any individual $\mathcal{A}_n$).

## 6.2 The Borel $\sigma$-Algebra

**Definition 6.3** (Borel $\sigma$-Algebra). The **Borel $\sigma$-algebra** on $\mathbb{R}$, denoted $\mathcal{B}$ or $\mathcal{B}(\mathbb{R})$, is the $\sigma$-algebra generated by all open subsets of $\mathbb{R}$:
$$\mathcal{B} := \sigma(\{O \subseteq \mathbb{R} : O \text{ is open}\})$$

**Proposition 6.4** (Multiple Generators, One $\sigma$-Algebra). *The Borel $\sigma$-algebra can be generated by several simpler families:*
$$\mathcal{B} = \sigma(\{(a, b)\}) = \sigma(\{(a, \infty)\}) = \sigma(\{[a, b]\}) = \sigma(\{(q, \infty) : q \in \mathbb{Q}\})$$

*The Standard Move.* To prove $\sigma(\mathcal{E}_1) = \sigma(\mathcal{E}_2)$, show that every generator of $\mathcal{E}_1$ lies in $\sigma(\mathcal{E}_2)$ and vice-versa:
$$(-\infty, b) = \bigcup_{n=1}^\infty \left(b - \frac{1}{n}, \infty\right)^c, \quad (a, b) = (a, \infty) \cap (-\infty, b), \quad (a, \infty) = \bigcup_{q \in \mathbb{Q}, q > a} (q, \infty)$$
$\square$

---
<!-- Page 17 -->
MA 305: Measure & Probability --- Condensed Course Notes
17

## 6.3 Pullback and Pushforward Constructions

When mapping between spaces $f : X \to Y$, how do $\sigma$-algebras transport?

**Proposition 6.5** (Pullback $\sigma$-Algebra (Initial $\sigma$-Algebra)). *Let $f : X \to Y$ and let $\mathcal{G}$ be a $\sigma$-algebra on $Y$. The **pullback collection** $\colon$*
$$f^{-1}(\mathcal{G}) := \{f^{-1}(G) : G \in \mathcal{G}\}$$
*is a $\sigma$-algebra on $X$.*

*Proof.* Preimages preserve all set operations:
1. $f^{-1}(Y) = X \in f^{-1}(\mathcal{G})$.
2. $X \setminus f^{-1}(G) = f^{-1}(Y \setminus G) \in f^{-1}(\mathcal{G})$ since $G^c \in \mathcal{G}$.
3. $\bigcup_n f^{-1}(G_n) = f^{-1}(\bigcup_n G_n) \in f^{-1}(\mathcal{G})$ since $\bigcup_n G_n \in \mathcal{G}$.

$\square$

**Example 6.6** (Applications of Pullback in Probability and Analysis).
1. **Random Variables:** For $X : \Omega \to \mathbb{R}$, $\sigma(X) := X^{-1}(\mathcal{B}(\mathbb{R}))$ is the $\sigma$-algebra generated by $X$, containing all events $\{X \le a\}, \{a < X \le b\}$. It represents the information about $\Omega$ revealed by $X$.
2. **Constant Map:** If $f \equiv y_0$, then $f^{-1}(G) = X$ (if $y_0 \in G$) or $\emptyset$ (if $y_0 \notin G$). Thus $f^{-1}(\mathcal{G}) = \{\emptyset, X\}$ (generates zero information).
3. **Coordinate Projections & Products:** For $\pi_1(x, y) = x$, $\pi_1^{-1}(\mathcal{B}) = \{B \times \mathbb{R} : B \in \mathcal{B}\}$ (vertical cylinders). The product $\sigma$-algebra is generated by their union: $\mathcal{B} \otimes \mathcal{B} = \sigma(\pi_1^{-1}(\mathcal{B}) \cup \pi_2^{-1}(\mathcal{B})) = \mathcal{B}(\mathbb{R}^2)$.
4. **Coin Toss Filtrations:** On $\Omega = \{0, 1\}^\mathbb{N}$, truncation $T_n(\omega) = (\omega_1, \dots, \omega_n)$ yields $\mathcal{F}_n = T_n^{-1}(\mathcal{P}(\{0, 1\}^n))$. $|\mathcal{F}_n| = 2^2$, giving the filtration $\mathcal{F}_1 \subseteq \mathcal{F}_2 \subseteq \mathcal{F}_3 \subseteq \dots$

**Definition 6.7** (Pushforward $\sigma$-Algebra (Final $\sigma$-Algebra)). If $(\Omega, \mathcal{F})$ is a measurable space and $f : \Omega \to Y$, the **pushforward** is:
$$f_*\mathcal{F} := \{B \subseteq Y : f^{-1}(B) \in \mathcal{F}\}$$
It is the largest $\sigma$-algebra on $Y$ that makes $f$ measurable.

## 6.4 Measure Space Completion: $\mathcal{M} = \text{Completion}(\mathcal{B})$

**Definition 6.8** (Complete Measure Space). A measure space $(\Omega, \Sigma, \mu)$ is **complete** if every subset of a measure-zero set is measurable:
$$E \in \Sigma, \quad \mu(E) = 0, \quad N \subseteq E \implies N \in \Sigma$$
The abstract completion is $\Sigma = \sigma(\mathcal{F} \cup \mathcal{N})$, where $\mathcal{N} = \{N \subseteq A : A \in \mathcal{F}, \mu(A) = 0\}$.

**Theorem 6.9** (Approximation by Open Sets & $G_\delta$ Hull). *Let $A \subseteq \mathbb{R}$.*
1. *For every $\epsilon > 0$, there exists an open set $U \supseteq A$ such that $m^*(A) \le m(U) \le m^*(A) + \epsilon$.*
2. *There exists a Borel $G_\delta$ set $B = \bigcap_{n=1}^\infty U_n$ such that $A \subseteq B$ and $m(B) = m^*(A)$.*

---
<!-- Page 18 -->
MA 305: Measure & Probability --- Condensed Course Notes
18

![Measure Space Completion: E = B \setminus N with m(N)=0. Bore Hull B \in \mathcal{B}, N = B \setminus E with m(B \setminus E) = 0, Measurable E \in \mathcal{M}](measure_space_completion.png)

Figure 4: **Structure of the Lebesgue Completion.** Every Lebesgue measurable set $E \in \mathcal{M}$ is sandwiched inside a Borel set $B \in \mathcal{B}$ with $m(B \setminus E) = 0$.

**Theorem 6.10** ($\mathcal{M}$ is the Completion of $\mathcal{B}$). *Let $\mathcal{C}$ be the completion of the Borel $\sigma$-algebra $\mathcal{B}$ with respect to Lebesgue measure. Then:*
$$\mathcal{M} = \mathcal{C}$$

*Proof.* **Direction 1:** $\mathcal{C} \subseteq \mathcal{M}$. The Lebesgue space $(\mathbb{R}, \mathcal{M}, m)$ is complete and contains all open sets (hence contains $\mathcal{B}$). Since $\mathcal{C}$ is the smallest complete $\sigma$-algebra containing $\mathcal{B}$, $\mathcal{C} \subseteq \mathcal{M}$.

**Direction 2:** $\mathcal{M} \subseteq \mathcal{C}$. Let $E \in \mathcal{M}$. By the $G_\delta$ approximation theorem, there exists a Borel set $B \in \mathcal{B}$ such that $E \subseteq B$ and $m(B) = m^*(E) = m(E)$.
* Define $N = B \setminus E$. Then $N$ is a Lebesgue measurable set and $m(N) = m(B) - m(E) = 0$.
* Since $N \in \mathcal{M}$ with $m(N) = 0$, there exists a Borel set $L \in \mathcal{B}$ such that $N \subseteq L$ and $m(L) = 0$.
* Thus $N$ is a subset of a Borel null set $L$, which by the definition of completion means $N \in \mathcal{C}$.
* Now observe: $E = B \setminus N = B \cap N^c$. Since $B \in \mathcal{B} \subseteq \mathcal{C}$ and $N \in \mathcal{C}$, we must have $E \in \mathcal{C}$.

Therefore, $\mathcal{M} \subseteq \mathcal{C}$. Combining both directions yields $\mathcal{M} = \mathcal{C}$.

$\square$

<!-- Page 19 -->
$$\text{MA 305: Measure \& Probability — Condensed Course Notes}$$

## 7 Lecture 6: Measurable Functions, Limits, \& The Devil's Staircase

### 7.1 Definition and Equivalent Characterizations

**Definition 7.1** (Measurable Function). Let $E \in \mathcal{M}$. A function $f : E \to \mathbb{R}$ is called **Lebesgue measurable** if for every open set $U \subseteq \mathbb{R}$, the preimage belongs to $\mathcal{M}$:
$$f^{-1}(U) = \{x \in E : f(x) \in U\} \in \mathcal{M}$$

**Theorem 7.2** (Four Equivalent Slicing Criteria). Let $E \in \mathcal{M}$ and $f : E \to \mathbb{R}$. The following are equivalent:
1. $f$ is measurable ($f^{-1}(U) \in \mathcal{M}$ for all open $U$).
2. $\{x \in E : f(x) > a\} \in \mathcal{M}$ for all $a \in \mathbb{R}$ (or all $a \in \mathbb{Q}$).
3. $\{x \in E : f(x) \ge a\} \in \mathcal{M}$ for all $a \in \mathbb{R}$.
4. $\{x \in E : f(x) < a\} \in \mathcal{M}$ for all $a \in \mathbb{R}$.
5. $\{x \in E : f(x) \le a\} \in \mathcal{M}$ for all $a \in \mathbb{R}$.

*Proof.* The relationships follow from set-theoretic identities:
$$\{f \ge a\} = \bigcap_{n=1}^{\infty} \left\{f > a - \frac{1}{n}\right\}, \quad \{f < a\} = E \setminus \{f \ge a\}, \quad \{f \le a\} = E \setminus \{f > a\}$$

Since $\mathcal{M}$ is closed under complements and countable intersections, if any one holds for all $a$, all hold. $\square$

**Proposition 7.3** (Basic Examples).
1. *Continuous functions are measurable (preimage of an open set is open, and open sets are in $\mathcal{M}$).*
2. *An indicator $\mathbf{1}_A$ is measurable $\iff A \in \mathcal{M}$.*

### 7.2 Algebra of Measurable Functions

**Theorem 7.4** (Continuous Two-Variable Combinations). If $f, g : E \to \mathbb{R}$ are measurable and $F : \mathbb{R}^2 \to \mathbb{R}$ is continuous, then $h(x) = F(f(x), g(x))$ is measurable.

*Proof.* Let $a \in \mathbb{R}$. The set $U = \{(u, v) \in \mathbb{R}^2 : F(u, v) > a\} = F^{-1}((a, \infty))$ is open in $\mathbb{R}^2$. Every open set in $\mathbb{R}^2$ is a countable union of open rational rectangles: $U = \bigcup_{n=1}^{\infty} (\alpha_n, \beta_n) \times (\gamma_n, \delta_n)$. Then:
$$\{x \in E : h(x) > a\} = \bigcup_{n=1}^{\infty} \Big(\{x \in E : \alpha_n < f(x) < \beta_n\} \cap \{x \in E : \gamma_n < g(x) < \delta_n\}\Big)$$

Each component is an intersection of measurable sets, hence measurable. The countable union is measurable. $\square$

**Corollary 7.5.** If $f, g$ are measurable, then $f \pm g$, $cf$, $fg$, $|f|$, $\max(f, g)$, and $\min(f, g)$ are measurable. Furthermore, $f/g$ is measurable on $\{x : g(x) \neq 0\}$.

**Remark 7.6** (The Asymmetry of Compositions).
- If $f$ is measurable and $g$ is **continuous**, then $g \circ f$ is measurable because $(g \circ f)^{-1}(U) = f^{-1}(g^{-1}(U))$, and $g^{-1}(U)$ is open.

---
<!-- Page 20 -->
$$\text{MA 305: Measure \& Probability — Condensed Course Notes}$$

- The converse ($f \circ g$) is **false** in general: the composition of two Lebesgue measurable functions need not be Lebesgue measurable!

**Example 7.7** (Measurability of $|f|$ Does Not Imply Measurability of $f$). Let $V \subset [0, 1]$ be a non-measurable Vitali set. Define:
$$f(x) = \mathbf{1}_V(x) - \mathbf{1}_{[0,1] \setminus V}(x) = \begin{cases} +1, & x \in V \\ -1, & x \notin V \end{cases}$$

Then $|f(x)| = 1$ for all $x$, which is a constant function and therefore measurable. However, $\{x : f(x) > 0\} = V \notin \mathcal{M}$. Thus $f$ is not measurable!

### 7.3 Positive and Negative Parts of a Function

**Definition 7.8** (Positive and Negative Decomposition). For any function $f : E \to \mathbb{R}$, define:
$$f^+(x) = \max(f(x), 0), \quad f^-(x) = \max(-f(x), 0) = -\min(f(x), 0)$$

Both $f^+$ and $f^-$ are non-negative functions ($f^+ \ge 0$, $f^- \ge 0$), and:
$$f = f^+ - f^-, \quad |f| = f^+ + f^-$$

**Theorem 7.9.** *A function $f$ is measurable $\iff$ both $f^+$ and $f^-$ are measurable.*

*Proof.* $(\implies)$ For $a \ge 0$, $\{f^+ > a\} = \{f > a\} \in \mathcal{M}$. For $a < 0$, $\{f^+ > a\} = E \in \mathcal{M}$. Hence $f^+$ is measurable. Similarly, $f^-$ is measurable. $(\impliedby)$ If $f^+$ and $f^-$ are measurable, their difference $f = f^+ - f^-$ is measurable. $\square$

### 7.4 Sequences of Functions: Supremum, Infimum, and Pointwise Limits

In analysis, limits of sequences can diverge to $\pm\infty$. We therefore extend our functions to the extended real number line $\overline{\mathbb{R}} = [-\infty, +\infty]$.

**Definition 7.10** (Measurability on $\overline{\mathbb{R}}$). A function $f : E \to [-\infty, +\infty]$ is measurable if $\{x : f(x) > a\} \in \mathcal{M}$ for all $a \in \mathbb{R}$. The infinite level sets are automatically measurable:
$$\{f = +\infty\} = \bigcap_{n=1}^{\infty} \{f > n\} \in \mathcal{M}, \quad \{f = -\infty\} = E \setminus \bigcup_{n=1}^{\infty} \{f > -n\} \in \mathcal{M}$$

**Theorem 7.11** (Preservation Under Countable Extremes). Let $\{f_n\}_{n=1}^{\infty}$ be a sequence of measurable functions on $E$. Then the following functions are all measurable:
$$\max_{1 \le n \le k} f_n, \quad \min_{1 \le n \le k} f_n, \quad \sup_{n \in \mathbb{N}} f_n, \quad \inf_{n \in \mathbb{N}} f_n$$

*Proof.* For any $a \in \mathbb{R}$, the supremum exceeds $a$ if and only if at least one function exceeds $a$:
$$\left\{x \in E : \sup_{n \in \mathbb{N}} f_n(x) > a\right\} = \bigcup_{n=1}^{\infty} \{x \in E : f_n(x) > a\} \in \mathcal{M}$$

Similarly, $\{\inf_n f_n < a\} = \bigcup_n \{f_n < a\} \in \mathcal{M}$. $\square$

**Theorem 7.12** (Measurability of $\limsup$, $\liminf$, and Pointwise Limits). Let $\{f_n\}_{n=1}^{\infty}$ be measurable. Then:
$$\limsup_{n \to \infty} f_n = \inf_{k \in \mathbb{N}} \left( \sup_{n \ge k} f_n \right) \quad \text{and} \quad \liminf_{n \to \infty} f_n = \sup_{k \in \mathbb{N}} \left( \inf_{n \ge k} f_n \right)$$

are both measurable. Consequently, if the pointwise limit $f(x) = \lim_{n \to \infty} f_n(x)$ exists, $f$ is measurable.

---
<!-- Page 21 -->
$$\text{MA 305: Measure \& Probability — Condensed Course Notes}$$

**Example 7.13** (Oscillation Example). Let $f_n(x) = (-1)^n x$ on $\mathbb{R}$. Each $f_n$ is continuous and measurable. Its accumulation limits are:
$$\limsup_{n \to \infty} f_n(x) = |x|, \quad \liminf_{n \to \infty} f_n(x) = -|x|$$

Both limits are continuous and measurable.

### 7.5 The Devil's Staircase (Cantor Ternary Function)

```
        φ₀(x) = x                         φ₁(x)                         φ₂(x)                         φ₃(x)
      1 ┌─────────                    1 ┌─────────                    1 ┌─────────                    1 ┌─────────
        │       /                       │     ┌───                    │     ┌───                    │    ┌────
        │      /                        │     │                       │     │                       │    │
    1/2 ┼     /                     1/2 ┼─────┘                   1/2 ┼─────┘                   1/2 ┼────┘
        │    /                          │                             │                             │
        │   /                           │                             │                             │
      0 └───┴───┴                   0 └───┴───┴                   0 └───┴───┴                   0 └───┴───┴
        0  1/3 2/3 1                    0  1/3 2/3 1                    0  1/3 2/3 1                    0  1/3 2/3 1
```

**Figure 5:** Iterations of the **Devil's Staircase** $(\varphi_0, \varphi_1, \varphi_2, \varphi_3)$. The function recursively flattens over the middle thirds removed during the construction of the Cantor set.

**Definition 7.14** (Cantor Function $\varphi$). Define $\varphi_0(x) = x$ on $[0, 1]$. For $n \ge 0$, define recursively:
$$\varphi_{n+1}(x) = \begin{cases} \frac{1}{2}\varphi_n(3x), & 0 \le x \le \frac{1}{3} \\ \frac{1}{2}, & \frac{1}{3} \le x \le \frac{2}{3} \\ \frac{1}{2} + \frac{1}{2}\varphi_n(3x - 2), & \frac{2}{3} \le x \le 1 \end{cases}$$

The uniform limit $\varphi(x) = \lim_{n \to \infty} \varphi_n(x)$ is the **Cantor Function** (Devil's Staircase).

**Proposition 7.15** (Remarkable Properties of $\varphi$).
1. $\varphi(0) = 0$ and $\varphi(1) = 1$.
2. $\varphi$ is continuous and non-decreasing on $[0, 1]$.
3. $\varphi'(x) = 0$ on the open set $[0, 1] \setminus \mathcal{C}$ of measure $1$.
4. *Although its derivative is zero almost everywhere, $\varphi$ climbs from $0$ to $1$ entirely on the null Cantor set $\mathcal{C}$! This singular behavior is a cornerstone for advanced measure theory and probability distributions.*

<!-- Page 22 -->
MA 305: Measure & Probability --- Condensed Course Notes

22

## 8 Comprehensive Topic Synthesis & Study Map

| Course Module | Core Mechanics & Results | Conceptual Significance |
| :--- | :--- | :--- |
| **1. Riemann Review** | Upper/Lower sums over domain partitions $P$; integrability $\bar{\int} = \underline{\int}$; FTC I & II. | Domain-slicing fails for discontinuous functions $(\mathbf{1}_{\mathbb{Q}})$ and collapses under pointwise limits. |
| **2. Null Sets & Cantor** | Sets coverable by intervals of total length $<\epsilon$; countable sets are null; Cantor set is null but uncountable. | Proves that topological density does not imply measure, and uncountability does not imply positive length. |
| **3. Vitali's Theorem** | Axioms (M1)–(M4); equivalence $x \sim y \Longleftrightarrow x - y \in \mathbb{Q}$; choice set $V$; sandwich $1 \le \sum a \le 3$. | Proof that no measure can exist on all subsets of $\mathbb{R}$. We must restrict to a sub-algebra $\mathcal{M} \subsetneq \mathcal{P}(\mathbb{R})$. |
| **4. Outer Measure & Carathéodory** | Infimum of open covers $m^*(E)$; criterion $m^*(A) = m^*(A \cap E) + m^*(A \cap E^c)$; rays in $\mathcal{M}$. | Transforms outer measure into a true countably additive measure $(\mathbb{R}, \mathcal{M}, m)$ on measurable sets. |
| **5. $\sigma$-Algebras & Completion** | Axioms of $\sigma$-algebra; Borel $\mathcal{B}$; pullbacks $f^{-1}(\mathcal{G})$; complete spaces; $\mathcal{M} = \text{Completion}(\mathcal{B})$. | Provides the rigorous algebraic infrastructure to model events in probability and measure spaces. |
| **6. Measurable Functions & Limits** | $f^{-1}(U) \in \mathcal{M}$; equivalent level cuts; continuous combos; closure under $\sup$, $\inf$, $\limsup$, $\lim$. | Resolves the fatal flaw of Riemann: limits of measurable functions are always measurable! |

Table 2: Grand Synthesis of MA 305 Course Foundations.

