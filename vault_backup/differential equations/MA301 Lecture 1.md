---
course: "differential equations"
source_file: "MA301 Lecture 1.pdf"
tags: ["math", "coursework", "differential-equations"]
---

# MA301 Lecture 1

<!-- Page 1 -->

# Lecture - 1
## Application of ODEs

### An atomic waste disposal problem:

Reference: M. Braun, *Differential Equations and applications*

![Diagram of a drum dropped into water towards a bottom surface 300 ft below]

**bottom surface** (300 ft)

---

### Mathematical Modelling:

**Newton's second law of motion:** $F = ma$

$$m \frac{d^2 y}{d t^2} = \text{Total force}$$
$$= W - B - D \quad \text{--- (2)}$$

$$\begin{cases} 
W := \text{weight of the body} & D := \text{Drag force} \\
B := \text{buoyancy force}
\end{cases}$$

As a drum descends through water, it is acted upon the three forces.

$$m \frac{d^2 y}{d t^2} = \text{Total force}$$
$$= W - B - D$$

---
<!-- Page 2 -->

$$\text{Velocity } V(t) = \frac{d y}{d t}, \quad D = cV, \quad W = mg$$

From (2),
$$m \frac{d V}{d t} = W - B - cV . \quad \text{--- (3)}$$

Substitute $m = \frac{W}{g}$ in (3), we have
$$\frac{d V}{d t} + \left(\frac{cg}{W}\right)V = \frac{g}{W} (W - B) . \text{ This gives rise to}$$

the first order differential equation:

$$\text{(4)} \quad \begin{cases} \frac{d V}{d t} + \left(\frac{cg}{W}\right)V = \frac{g}{W}(W - B), \\ V(0) = 0 \quad (\text{at the time of release of drum velocity is zero}) \end{cases}$$

$$\mathbf{\text{Solution:}} \quad V(t) = \frac{W - B}{c} \left(1 - e^{-\frac{cg}{W}t}\right) .$$

If $V(t) \approx 40 \text{ ft/s}$, then the drum breaks.

We calculated the velocity in terms of time, but not in terms of distance, so we are unable to predict the velocity when it hits the floor.

---
<!-- Page 3 -->

### Modified approach: 
We modify the approach as follows to write the velocity in terms of distance. Now, $y$ is the distance and $v(y)$ is the velocity at the distance $y$.

The two functions $V(t)$ & $v(y)$ are related through
$$\boxed{V(t) = v(y(t))}$$

$$\frac{dV}{dt} + \left(\frac{cg}{W}\right)V = \frac{g}{W}(W-B), \quad \text{--- (4)}$$

Therefore, $\frac{dV}{dt} = \frac{dv}{dy} \frac{dy}{dt} = v \frac{dv}{dy} . \quad \text{--- (5)}$
(Using chain rule)

Using (5) in (4) and solving, we obtain

$$\boxed{\frac{gy}{W} = -\frac{v}{c} - \left(\frac{W-B}{c^2}\right) \log \left(\frac{W - B - cv}{W - B}\right)} \quad \text{--- (6)}$$

Equation (6) represents distance $y$ as a function of velocity $v$.

It is difficult to write $v$ as a function of $y$. But numerically, it can be shown that $v(300) \approx 45$ and the drum breaks!!

<!-- Page 1 -->
A few more applications are :

<u>Radioactive decay</u> : A radioactive substance decomposes at a rate proportional to the amount present. Let $y(t)$ be the amount present at time $t$. Then,

$$\frac{dy}{dt} = -ky,$$

where $k$ is a physical constant whose value is found by experiments. ($-k$ is called the decay constant).  
(Linear ODE, first order)

<u>The motion of an oscillating pendulum</u> :

Consider an oscillating pendulum of length $L$. Let $\theta$ be the angle it makes with the vertical direction.

$$\frac{d^2\theta}{dt^2} + \frac{g}{L}\sin\theta = 0 \text{ .}$$  
(ODE, second order, nonlinear)

<!-- Page 2 -->
<u>A falling object</u> :

A body of mass $m$ falls under the force of gravity. The drag force due to the air resistance is $c \cdot v^2$, where $v$ is the velocity and $c$ is a constant. Then,

$$\boxed{m\frac{dv}{dt} = mg - cv^2}$$

(An ODE of first order) ($\text{Linear or nonlinear?}$)

<!-- Page 3 -->
For more detailed explanation of above model, refer to M. Braun book.

<u>Remark</u> :  
$\text{AEC}$ ($\text{Atomic Energy Commission}$) forbid the dumping of low level atomic waste at sea.

<!-- Page 1 -->
Bungee-Jumping Model: To find the velocity of a jumper as a function of time during the free-fall part of the jump.

The mathematical model for this problem can be obtained as follows:

From Newton's second law of motion gives
$$m \frac{dv}{dt} = F \quad -(1)$$

where '$v$' is velocity of the jumper.

If the net force is positive, the object will accelerate. If it is negative, the object will decelerate.

If the net force is zero, then the object velocity will remain at a constant level.

$$\text{Total force } F = F_D + F_U$$
$$\underbrace{\hspace{2.2cm}}_{\text{downward pull of gravity}}$$
$$\underbrace{\hspace{2.5cm}}_{\text{upward force of air resistance}}$$

<!-- Page 2 -->
$$\underbrace{\begin{matrix} \text{Upward force} \\ \text{due to air} \\ \text{resistance} \end{matrix}}_{\text{}} \longrightarrow F_U$$

$$\underbrace{\begin{matrix} \text{Downward} \\ \text{force due} \\ \text{to gravity} \end{matrix}}_{\text{}} \longrightarrow F_D$$

Reference: *Applied Numerical Methods with MATLAB for Engineers and Scientists*, Steven C. Chapra

The force due to gravity is $F_D = mg$, where $g$ is the acceleration due to gravity.

<!-- Page 3 -->
Air resistance can be formulated in a variety of ways.
$$F_U = -C_d \, v^2,$$

where $C_d$ is the proportionality constant called the drag coefficient.

Thus, the greater the fall velocity, the greater the upward force due to air resistance.

The parameter $C_d$ accounts for properties of the falling object, such as shape or surface roughness, that affect the air resistance. For the present case, $C_d$ might be a function of type of clothing or the orientation used by the jumper during free fall.

The net force is the difference between the downward and upward force. Therefore,
$$\frac{dv}{dt} = g - \frac{C_d}{m} v^2. \quad - 1(a)$$

The above equation represents the bungee jumper model.

Eqn $1(a)$ is a **first order differential equation**.

<!-- Page 1 -->
If the jumper is initially at rest, that is at $t=0$, $v=0$, then Calculus and ordinary differential equation course can be used to obtain an analytical or exact solution for $v$ as a function of time $t$.

$$v(t) = \sqrt{\frac{gm}{c_d}} \tanh \left(\sqrt{\frac{gc_d}{m}} t \right).$$

<!-- Page 2 -->
Mixing problem with two compartments

Tank A
Tank B
$2\text{ Ltr/min}$
$0\text{ kg/Ltr}$
$x(0) = 5\text{ kg}$
$\text{Vol} = 50\text{ Ltr}$
$3\text{ ltr/min}$
$y(0) = 1\text{ kg}$
$\text{Vol} = 40\text{ ltr}$
$1\text{ ltr/min}$
$2\text{ ltr / min}$
$\frac{y(t)}{40}\text{ kg / Ltr}$

Figure (1)

Discription of the Mixing Problem

Tank A is connected to Tank B by two separate pipes (see the figure).
The pure water is entering at a rate of $2\text{ ltr / min}$.

Initially at $t=0$,
Tank A is filled with $50\text{ ltr}$ with $5\text{ kgs}$ of salt dissolved in it.
Tank B is filled with $40\text{ ltr}$ with $1\text{ kg}$ of salt dissolved in it.

The solution flows from Tank A to Tank B at a rate of $3\text{ Ltr/min}$ and from Tank B to Tank A (via separate pipe) at a rate of $1\text{ Ltr/min}$.

<!-- Page 3 -->
A completely mixed solution is draining from Tank B at a rate of $2\text{ Ltr/min}$.

Let $x(t)$ be the amount of salt in Tank A at time $t$.

Let $y(t)$ be the amount of salt in Tank B at time $t$.

By using the formula,
rate of change of salt in each tank
$= \text{rate in} - \text{rate out}$,

we have
$$\begin{aligned}
\frac{dx}{dt} &= \text{rate of change in Tank A } (\text{in Kg/min}) \\
&= \text{rate in} - \text{rate out} \\
&= \left[2 \cdot 0 + 1 \cdot \frac{y(t)}{40}\right] - \left[3 \cdot \frac{x(t)}{50}\right]
\end{aligned}$$

<!-- Page 1 -->
$$\begin{array}{cc}
\text{Ltr} & \text{Kg} \\
50 & x(t) \text{ in } 1\text{ min } \frac{3x(t)}{50}\text{ kg salt going} \\
& \text{from } A\text{ to } B \\
3 & ?
\end{array}$$

$$\begin{array}{cc}
\text{Ltr} & \text{Kg} \\
40 & y(t) \text{ in } 1\text{ min } \frac{1\cdot y(t)}{40}\text{ kg salt going} \\
1 & ? \hspace{3cm} \text{from } B\text{ to } A.
\end{array}$$

$$\begin{array}{cc}
\text{Ltr} & \text{Kg} \\
1 & 0 \hspace{0.5cm} \text{in } 1\text{ min } 2.0\times 0\text{ kg salt} \\
2 & ? \hspace{0.5cm} \text{entering into tank } A.
\end{array}$$

$$^{lly}\text{ we have}$$

$$\begin{aligned}
\frac{dy}{dt} &= \text{rate of change of salt in Tank } B \\
&\hspace{3.2cm}(\text{in kg/min}) \\
&= \text{rate in } - \text{rate out} \\
&= \left[\frac{3x(t)}{50}\right] - \left[\frac{y(t)}{40} + \frac{2y(t)}{40}\right]
\end{aligned}$$
$$\underbrace{\hspace{2.2cm}}_{\text{from } A\text{ to } B} \hspace{0.6cm} \underbrace{\hspace{2.5cm}}_{\substack{\text{from} \\ B\text{ to } A} \quad \text{drained} \atop \text{from } B}$$

<!-- Page 2 -->
$$\text{Thus, } \begin{aligned}
\frac{dx}{dt} &= -\frac{3x(t)}{50} + \frac{y(t)}{40} \\
\frac{dy}{dt} &= \frac{3x(t)}{50} - \frac{3y(t)}{40}
\end{aligned}$$

$$\begin{bmatrix}
\frac{dx}{dt} \\
\frac{dy}{dt}
\end{bmatrix} = \begin{bmatrix}
-\frac{3}{50} & \frac{1}{40} \\
\frac{3}{50} & -\frac{3}{40}
\end{bmatrix}\begin{bmatrix}
x(t) \\
y(t)
\end{bmatrix}$$

$$\text{The above example shows that a single}$$
$$\text{differential equation is not enough to}$$
$$\text{describe certain physical problems.}$$

