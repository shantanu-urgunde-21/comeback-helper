"""
Index vault notes into the atlas.

    python -m src.atlas.index                    # all notes
    python -m src.atlas.index --note "path.md"   # one note
    python -m src.atlas.index --rebuild          # discard and re-extract
"""

import argparse
from pathlib import Path
from typing import Optional

from src.config import get_settings
from src.logger import log
from src.vault.manager import ObsidianVaultManager
from src.atlas.extract import extract_note
from src.atlas.store import AtlasStore
from src.atlas import validate


def index_vault(
    store: Optional[AtlasStore] = None,
    note: Optional[Path] = None,
    rebuild: bool = False,
) -> dict:
    settings = get_settings()
    store = store or AtlasStore()

    if rebuild:
        store.clear()

    if note:
        notes = [note]
    else:
        vm = ObsidianVaultManager(settings.vault_path)
        notes = vm.get_all_notes()

    reports = []
    for n in notes:
        stmts, terms, rep = extract_note(n, store)
        store.add_terms(terms)
        store.add_statements(stmts)
        reports.append({"note": n.name, **rep})

    # Term matching improves once every note's terms are in the table, so run
    # visibility validation only after the whole pass.
    findings = validate.check(store)
    store.save()

    return {
        "notes": reports,
        "stats": store.stats(),
        "validation": validate.summarise(findings),
        "findings": findings,
    }


def _print(result: dict):
    s = result["stats"]
    v = result["validation"]
    print("\n" + "=" * 70)
    print("  ATLAS INDEX")
    print("=" * 70)
    for r in result["notes"]:
        if "error" in r:
            print(f"  {r['note']:<40} ERROR: {r['error']}")
        else:
            print(f"  {r['note']:<40} {r['statements']:>3} statements  "
                  f"{r['terms']:>3} terms  {r['dropped_unknown_context']:>2} dropped")
    print("-" * 70)
    print(f"  statements {s['statements']:<6} terms {s['terms']:<6} "
          f"contexts used {s['contexts_used']}/{s['contexts']}")
    print(f"  by status  {s['by_status']}")
    print("  busiest contexts:")
    for cid, n in s["top_contexts"]:
        print(f"      {cid:<28} {n}")
    print("-" * 70)
    print(f"  validation  {v['errors']} errors, {v['warnings']} warnings")
    for gate, n in sorted(v["by_gate"].items(), key=lambda kv: -kv[1]):
        print(f"      {gate:<26} {n}")
    print("=" * 70 + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--note")
    ap.add_argument("--rebuild", action="store_true")
    args = ap.parse_args()
    res = index_vault(note=Path(args.note) if args.note else None, rebuild=args.rebuild)
    _print(res)


if __name__ == "__main__":
    main()
