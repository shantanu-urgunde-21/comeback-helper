"""
Validation gates.

Model A's gates could only check that a relation was in the enum. Model B's
structure supports gates that catch *misclassification* with no human in the
loop — in particular, a statement using a term that is not visible from its
declared context is almost certainly filed in the wrong place.
"""

from typing import Iterable

from src.atlas.schema import Statement, Status, Term
from src.atlas.store import AtlasStore


class Finding(dict):
    """A gate failure: {gate, severity, statement, detail}."""


def check(store: AtlasStore, statements: Iterable[Statement] | None = None) -> list[Finding]:
    stmts = list(statements if statements is not None else store.statements.values())
    out: list[Finding] = []

    def add(gate, severity, s, detail):
        out.append(Finding(gate=gate, severity=severity, statement=s.id, detail=detail))

    for s in stmts:
        # 1. the context must exist in the lattice
        if s.context not in store.contexts:
            add("unknown-context", "error", s, f"'{s.context}' is not in the lattice")
            continue

        # 2. a FALSE statement without a witness is useless — the counterexample
        #    is the whole content of the claim
        if s.status == Status.FALSE and not s.witness:
            add("false-without-witness", "error", s, "status FALSE requires a witness")

        # 3. term visibility. A statement may only use terms defined in its own
        #    context or an ancestor. A statement invoking a metric cannot live in
        #    TopologicalSpace. This catches misclassification for free.
        visible = store.visible_terms(s.context)
        for key in s.uses_terms:
            name, _, ctx = key.rpartition("@")
            if name.lower() not in visible:
                add("term-not-visible", "warn", s,
                    f"uses '{name}' (defined in {ctx}) which is not visible from {s.context}")

        # 4. a slogan is the ladder's join key; an empty one silently orphans it
        if len(s.slogan.split()) < 3:
            add("weak-slogan", "warn", s, f"slogan too short to join on: '{s.slogan}'")

    # 5. lattice consistency: a slogan asserted THEOREM at a context should not
    #    be FALSE at any context *below* it — more structure cannot break a
    #    result that already held with less.
    by_slogan: dict[str, list[Statement]] = {}
    for s in stmts:
        by_slogan.setdefault(s.slogan.strip().lower(), []).append(s)

    for slogan, group in by_slogan.items():
        if len(group) < 2:
            continue
        for a in group:
            if a.status != Status.THEOREM:
                continue
            for b in group:
                if b.status == Status.FALSE and a.context in store.ancestors(b.context):
                    add("contradiction", "error", b,
                        f"FALSE in {b.context} but THEOREM in ancestor {a.context} "
                        f"— one of the two is misclassified")
    return out


def summarise(findings: list[Finding]) -> dict:
    by_gate: dict[str, int] = {}
    for f in findings:
        by_gate[f["gate"]] = by_gate.get(f["gate"], 0) + 1
    return {
        "total": len(findings),
        "errors": sum(1 for f in findings if f["severity"] == "error"),
        "warnings": sum(1 for f in findings if f["severity"] == "warn"),
        "by_gate": by_gate,
    }
