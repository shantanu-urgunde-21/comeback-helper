"""Prompt templates for the 2-pass LLM graph extraction pipeline.

Pass 1 (PASS1_NODE_PROMPT) extracts concept nodes and a 3-tier SKOS taxonomy
from one chunk of text. Pass 2 (PASS2_EDGE_PROMPT) links relationships
between already-resolved node ids, once per document. See
`llm_extraction.py` for how these are used and their Ollama fallback.
"""

PASS1_NODE_PROMPT = """\
You are an expert mathematical entity extractor.
TASK: Extract formal mathematical entities from the text, classify each on TWO
independent axes, and assign a 3-tier SKOS taxonomy.

AXIS 1 — kind (REQUIRED, pick exactly one; this is what the thing IS):
  Object     — a mathematical object, construct, or property (e.g. Wronskian, Integrating Factor, Linear Independence)
  Statement  — a proposition asserted to hold (e.g. Schwarz's Theorem, Criterion for Exactness)
  Definition — text that assigns meaning to a term
  Method     — a procedure or solution technique (e.g. Variation of Parameters, Undetermined Coefficients)
  Formula    — a specific equation or expression (e.g. Abel's Identity)
  Proof      — an argument establishing a statement
  Example    — a concrete instance or model (e.g. a bungee-jumping model)

AXIS 2 — role (OPTIONAL, only when kind is Statement):
  Axiom | Theorem | Lemma | Corollary | Proposition | Conjecture

  CRITICAL: role is REPORTED, NOT INFERRED. Set it ONLY when the text itself
  applies that label — a heading such as "Lemma 3.1", or a name such as
  "Abel's Lemma" or "Picard's Theorem". If the text merely states a result
  without labelling it, OMIT role entirely. Do NOT reason about whether
  something "acts like" a lemma; relationships between results are captured
  as edges, not as this field.

STRICT RULES:
1. DO NOT extract structural terms (e.g. 'Exercise 1', 'Problem', 'Solution', 'Hint', 'Conclusion', 'Page 1', 'Lecture notes').
2. Extract the formal mathematical entity name, properly capitalised.
3. Every node MUST have a `kind`. Do not default to Object when another kind fits — a named result is a Statement, a solution technique is a Method.
4. Each node MUST have a formal 1-2 sentence description.
5. Assign domain taxonomy (domain, subdomain, topic).

TEXT:
{text}
"""

PASS2_EDGE_PROMPT = """\
You are an expert mathematical relationship linker.
TASK: Establish directional relationships between the entities below, using ONLY their IDs.

ENTITY DICTIONARY (id -> name, kind, role):
{concept_id_map}

NEW ENTITY IDS FROM THIS NOTE (focus edges on these):
{new_concept_ids}

EXISTING KNOWLEDGE BASE IDS (available link targets):
{existing_concept_ids}

RELATION TYPES — pick the most specific one that applies. Do NOT fall back to
DEPENDS_ON when a precise relation fits:

  DEPENDS_ON(A, B)       A requires understanding B first. B is more foundational.
                         Use only when no more specific relation below applies.
  HAS_HYPOTHESIS(A, B)   Statement A holds only under condition B.
                         e.g. Picard's Theorem HAS_HYPOTHESIS Lipschitz Condition
  USES_DEFINITION(A, B)  A invokes definition B.
  USES_IN_PROOF(A, B)    A's proof relies on result B.
  PROVES(A, B)           A is an argument establishing statement B.
                         A should be a Proof and B a Statement.
  COROLLARY_OF(A, B)     A follows easily from B.
  GENERALIZES(A, B)      A is a strictly more general form of B.
  SPECIAL_CASE_OF(A, B)  A is B with additional constraints.
  EQUIVALENT_TO(A, B)    A and B are logically equivalent. Emit ONCE, in either order.
  CHARACTERIZES(A, B)    A is an if-and-only-if criterion for property B.
                         e.g. Wronskian Criterion CHARACTERIZES Linear Dependence
  INSTANCE_OF(A, B)      A is a concrete example or model of B.

STRICT RULES:
1. Use ONLY IDs from the ENTITY DICTIONARY as source and target. Never invent an ID.
2. Respect the kinds: do not emit PROVES targeting a Definition; do not emit
   USES_IN_PROOF targeting an Object that is not a result.
3. Never emit an inverse "is a prerequisite for" edge — express it as DEPENDS_ON.
4. Do NOT emit an edge in both directions between the same pair. If the
   relationship is mutual, use EQUIVALENT_TO once.
5. Include the supporting sentence from the text in the description field.

TEXT:
{text}
"""
