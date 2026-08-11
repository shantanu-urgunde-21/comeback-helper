"""
Curated scope for the context lattice.

This module supplies the *node set* only. The ordering relation between
contexts is transcribed from independent sources (see `sources.py`) and merged
by vote in `merge.py` — never hand-authored here.

Scope: Ordinary Differential Equations, Calculus, Linear Algebra, plus the
analysis/algebra spine those three sit on.

`extends` semantics used throughout: `A extends B` means *A assumes everything
B assumes, and more*. So A sits BELOW B in the lattice (more structure, less
general). Metric space extends topological space.
"""

from typing import Optional, NamedTuple


class ContextSeed(NamedTuple):
    id: str
    name: str
    wikipedia: Optional[str]  # None → skip Wikipedia/Wikidata for this node
    course: str               # which course this context shows up in


# ---------------------------------------------------------------------------
# Roots — assumed by everything, named by no textbook chapter.
# These exist because a single book's lattice has holes at the top.
# ---------------------------------------------------------------------------

ROOTS = [
    ContextSeed("Set", "Set", "Set (mathematics)", "foundations"),
]


# ---------------------------------------------------------------------------
# Candidate contexts, scoped to ODE / Calculus / Linear Algebra
# ---------------------------------------------------------------------------

CANDIDATES = [
    # -- order & number systems ------------------------------------------
    ContextSeed("OrderedField", "Ordered field", "Ordered field", "foundations"),
    ContextSeed("RealNumbers", "Real numbers (complete ordered field)", "Real number", "foundations"),
    ContextSeed("ComplexNumbers", "Complex numbers", "Complex number", "foundations"),

    # -- algebra ----------------------------------------------------------
    ContextSeed("Group", "Group", "Group (mathematics)", "linear algebra"),
    ContextSeed("AbelianGroup", "Abelian group", "Abelian group", "linear algebra"),
    ContextSeed("Ring", "Ring", "Ring (mathematics)", "linear algebra"),
    ContextSeed("CommutativeRing", "Commutative ring", "Commutative ring", "linear algebra"),
    ContextSeed("IntegralDomain", "Integral domain", "Integral domain", "linear algebra"),
    ContextSeed("Field", "Field", "Field (mathematics)", "linear algebra"),
    ContextSeed("Module", "Module over a ring", "Module (mathematics)", "linear algebra"),
    ContextSeed("VectorSpace", "Vector space", "Vector space", "linear algebra"),
    ContextSeed("FiniteDimVectorSpace", "Finite-dimensional vector space", "Dimension (vector space)", "linear algebra"),
    ContextSeed("AlgebraOverField", "Algebra over a field", "Algebra over a field", "linear algebra"),
    ContextSeed("MatrixRing", "Matrix algebra", "Matrix ring", "linear algebra"),

    # -- inner product / norm --------------------------------------------
    ContextSeed("NormedVectorSpace", "Normed vector space", "Normed vector space", "linear algebra"),
    ContextSeed("InnerProductSpace", "Inner product space", "Inner product space", "linear algebra"),
    ContextSeed("EuclideanSpace", "Euclidean space", "Euclidean space", "calculus"),
    ContextSeed("BanachSpace", "Banach space", "Banach space", "analysis"),
    ContextSeed("HilbertSpace", "Hilbert space", "Hilbert space", "analysis"),

    # -- topology & metric ------------------------------------------------
    ContextSeed("TopologicalSpace", "Topological space", "Topological space", "analysis"),
    ContextSeed("HausdorffSpace", "Hausdorff space", "Hausdorff space", "analysis"),
    ContextSeed("MetricSpace", "Metric space", "Metric space", "analysis"),
    ContextSeed("CompleteMetricSpace", "Complete metric space", "Complete metric space", "analysis"),
    ContextSeed("CompactSpace", "Compact space", "Compact space", "analysis"),
    ContextSeed("ConnectedSpace", "Connected space", "Connected space", "analysis"),

    # -- manifolds (where ODEs live geometrically) ------------------------
    ContextSeed("TopologicalManifold", "Topological manifold", "Topological manifold", "analysis"),
    ContextSeed("SmoothManifold", "Smooth manifold", "Differentiable manifold", "analysis"),

    # -- function classes -------------------------------------------------
    ContextSeed("ContinuousFunction", "Continuous function", "Continuous function", "calculus"),
    ContextSeed("DifferentiableFunction", "Differentiable function", "Differentiable function", "calculus"),
    ContextSeed("SmoothFunction", "Smooth function", "Smoothness", "calculus"),
    ContextSeed("AnalyticFunction", "Analytic function", "Analytic function", "calculus"),
    ContextSeed("LipschitzFunction", "Lipschitz continuous function", "Lipschitz continuity", "ode"),
    ContextSeed("RiemannIntegrable", "Riemann-integrable function", "Riemann integral", "calculus"),
    ContextSeed("MeasureSpace", "Measure space", "Measure space", "analysis"),
    ContextSeed("LebesgueIntegrable", "Lebesgue-integrable function", "Lebesgue integration", "analysis"),

    # -- calculus settings ------------------------------------------------
    ContextSeed("RealFunction", "Function of one real variable", "Function of a real variable", "calculus"),
    ContextSeed("MultivariableFunction", "Function of several real variables", "Function of several real variables", "calculus"),
    ContextSeed("VectorField", "Vector field", "Vector field", "ode"),

    # -- differential equations -------------------------------------------
    ContextSeed("DifferentialEquation", "Differential equation", "Differential equation", "ode"),
    ContextSeed("ODE", "Ordinary differential equation", "Ordinary differential equation", "ode"),
    ContextSeed("PDE", "Partial differential equation", "Partial differential equation", "ode"),
    ContextSeed("FirstOrderODE", "First-order ODE", "First-order differential equation", "ode"),
    ContextSeed("SeparableODE", "Separable ODE", "Separation of variables", "ode"),
    ContextSeed("ExactODE", "Exact differential equation", "Exact differential equation", "ode"),
    ContextSeed("LinearODE", "Linear differential equation", "Linear differential equation", "ode"),
    ContextSeed("LinearODEConstCoeff", "Linear ODE with constant coefficients", "Linear differential equation", "ode"),
    ContextSeed("HomogeneousLinearODE", "Homogeneous linear ODE", "Homogeneous differential equation", "ode"),
    ContextSeed("ODESystem", "System of ODEs", "System of differential equations", "ode"),
    ContextSeed("AutonomousSystem", "Autonomous system", "Autonomous system (mathematics)", "ode"),
    ContextSeed("DynamicalSystem", "Dynamical system", "Dynamical system", "ode"),
    ContextSeed("InitialValueProblem", "Initial value problem", "Initial value problem", "ode"),
    ContextSeed("BoundaryValueProblem", "Boundary value problem", "Boundary value problem", "ode"),
    ContextSeed("SturmLiouville", "Sturm-Liouville problem", "Sturm–Liouville theory", "ode"),
]

ALL_CONTEXTS = ROOTS + CANDIDATES


# ---------------------------------------------------------------------------
# Anchor test — pairs I am certain of, used to detect direction inversion.
#
# The dominant failure mode when transcribing a lattice is confusing
# pedagogical order with axiom inclusion (many analysis courses teach metric
# spaces before topological spaces, but MetricSpace extends TopologicalSpace,
# not the reverse). These pairs catch that immediately.
#
# Format: (child, parent) meaning "child extends parent".
# ---------------------------------------------------------------------------

ANCHORS = [
    ("MetricSpace", "TopologicalSpace"),
    ("MetricSpace", "HausdorffSpace"),
    ("HausdorffSpace", "TopologicalSpace"),
    ("CompleteMetricSpace", "MetricSpace"),
    ("CompactSpace", "TopologicalSpace"),
    ("ConnectedSpace", "TopologicalSpace"),
    ("NormedVectorSpace", "VectorSpace"),
    ("NormedVectorSpace", "MetricSpace"),
    ("InnerProductSpace", "NormedVectorSpace"),
    ("BanachSpace", "NormedVectorSpace"),
    ("BanachSpace", "CompleteMetricSpace"),
    ("HilbertSpace", "InnerProductSpace"),
    ("HilbertSpace", "BanachSpace"),
    ("EuclideanSpace", "InnerProductSpace"),
    ("RealNumbers", "OrderedField"),
    ("OrderedField", "Field"),
    ("ComplexNumbers", "Field"),
    ("ContinuousFunction", "TopologicalSpace"),
    ("AbelianGroup", "Group"),
    ("Ring", "AbelianGroup"),
    ("CommutativeRing", "Ring"),
    ("IntegralDomain", "CommutativeRing"),
    ("Field", "IntegralDomain"),
    ("Module", "AbelianGroup"),
    ("VectorSpace", "Module"),
    ("FiniteDimVectorSpace", "VectorSpace"),
    ("AlgebraOverField", "VectorSpace"),
    ("SmoothManifold", "TopologicalManifold"),
    ("TopologicalManifold", "TopologicalSpace"),
    ("SmoothFunction", "DifferentiableFunction"),
    ("DifferentiableFunction", "ContinuousFunction"),
    ("AnalyticFunction", "SmoothFunction"),
    ("LipschitzFunction", "ContinuousFunction"),
    ("ODE", "DifferentialEquation"),
    ("PDE", "DifferentialEquation"),
    ("FirstOrderODE", "ODE"),
    ("LinearODE", "ODE"),
    ("SeparableODE", "FirstOrderODE"),
    ("ExactODE", "FirstOrderODE"),
    ("LinearODEConstCoeff", "LinearODE"),
    ("HomogeneousLinearODE", "LinearODE"),
    ("AutonomousSystem", "ODESystem"),
]


# ---------------------------------------------------------------------------
# Two relations, not one.
#
# `extends` is axiom strengthening within one signature: Field extends
# IntegralDomain extends CommutativeRing extends Ring — same kind of object,
# progressively more axioms. A genuine partial order.
#
# `over` is parameterisation: a vector space is over a field, a module over a
# ring, a normed space over R or C. A normed vector space is NOT a special kind
# of real number; it is a vector space whose *scalars* are real numbers.
#
# Collapsing the second into the first routed 39 of 54 contexts through Field
# and inflated every depth below it. It also made the spectral-theorem ladder
# inexpressible: "normal matrix over R" vs "over C" differ only in this slot.
# ---------------------------------------------------------------------------

# Contexts that can appear as a scalar / base structure another object is built over.
SCALAR_STRUCTURES = {
    "Field", "CommutativeRing", "Ring", "OrderedField",
    "RealNumbers", "ComplexNumbers",
}

# Contexts that live *in* the ring signature. Edges among these are genuine
# axiom strengthening even when the target is a scalar structure.
ALGEBRAIC_CHAIN = {
    "Group", "AbelianGroup", "Ring", "CommutativeRing", "IntegralDomain",
    "Field", "OrderedField", "RealNumbers", "ComplexNumbers",
}

# Known parameterisations that extraction either missed or mistyped.
OVER_SEED = [
    ("VectorSpace", "Field"),
    ("Module", "Ring"),
    ("AlgebraOverField", "Field"),
    ("MatrixRing", "Field"),
    ("NormedVectorSpace", "RealNumbers"),
    ("InnerProductSpace", "RealNumbers"),
    ("EuclideanSpace", "RealNumbers"),
]


def is_over(child: str, parent: str) -> bool:
    """True if this pair is parameterisation rather than axiom strengthening."""
    return parent in SCALAR_STRUCTURES and child not in ALGEBRAIC_CHAIN


def context_by_id() -> dict[str, ContextSeed]:
    return {c.id: c for c in ALL_CONTEXTS}


def wikipedia_title_map() -> dict[str, str]:
    """Wikipedia article title → context id, for resolving extracted links."""
    out: dict[str, str] = {}
    for c in ALL_CONTEXTS:
        if c.wikipedia:
            out[c.wikipedia] = c.id
    return out
