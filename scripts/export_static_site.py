import json
import shutil
from pathlib import Path

def export_static_site():
    repo_root = Path(__file__).parent.parent.resolve()
    dist_dir = repo_root / "dist_static"
    dist_dir.mkdir(parents=True, exist_ok=True)

    # 1. Copy logo, css & app JS
    static_src = repo_root / "static"
    img_dist = dist_dir / "img"
    if img_dist.exists():
        shutil.rmtree(img_dist)
    shutil.copytree(static_src / "img", img_dist)
    shutil.copy2(static_src / "style.css", dist_dir / "style.css")
    shutil.copy2(static_src / "app.js", dist_dir / "app.js")

    # index.html and app.js are shared with the live server (src/server.py
    # serves the same files under /static/). The only thing that changes for
    # GitHub Pages is: (a) the <meta name="build-mode"> flag app.js reads to
    # decide whether to call /api/... or read data/*.json, and (b) absolute
    # /static/... asset paths, which only resolve under the live server's
    # root and 404 on a GitHub Pages project site. See CLAUDE.md / README for
    # why there is deliberately no separate hand-maintained copy of these.
    html = (static_src / "index.html").read_text(encoding="utf-8")
    if '<meta name="build-mode" content="live">' not in html:
        raise RuntimeError(
            "static/index.html's build-mode meta tag has changed shape — "
            "update the replace in export_static_site.py or app.js will "
            "wire up live-only tabs (Ingest/Query) on GitHub Pages."
        )
    html = html.replace(
        '<meta name="build-mode" content="live">',
        '<meta name="build-mode" content="static">',
    )
    html = html.replace('"/static/', '"./')
    (dist_dir / "index.html").write_text(html, encoding="utf-8")

    # Create empty .nojekyll for GitHub Pages
    (dist_dir / ".nojekyll").write_text("", encoding="utf-8")

    # 2. Locate graph.json
    graph_src = repo_root / ".storage" / "graph.json"
    if not graph_src.exists():
        raise FileNotFoundError("No .storage/graph.json found!")
    
    graph_data = json.loads(graph_src.read_text(encoding="utf-8"))

    # 3. Locate Obsidian Vault
    try:
        import src
        from shared.config import get_settings
        vault_path = get_settings().vault_path
        if not vault_path.exists():
            vault_path = repo_root / ".storage" / "vault"
    except Exception:
        vault_path = Path("D:/obsidian/comeback-helper")
        if not vault_path.exists():
            vault_path = repo_root / ".storage" / "vault"

    notes_dist = dist_dir / "notes"
    if notes_dist.exists():
        shutil.rmtree(notes_dist)
    notes_dist.mkdir(parents=True, exist_ok=True)

    vault_index = {"vault": {}}

    if vault_path.exists():
        print(f"Copying notes from vault at: {vault_path}")
        for note_file in vault_path.rglob("*.md"):
            try:
                rel_path = note_file.relative_to(vault_path)
            except ValueError:
                rel_path = Path(note_file.name)
            
            course_name = rel_path.parts[0] if len(rel_path.parts) > 1 else "General"
            if course_name not in vault_index["vault"]:
                vault_index["vault"][course_name] = []
            
            target_file = notes_dist / rel_path
            target_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(note_file, target_file)
            
            rel_web_path = f"notes/{rel_path.as_posix()}"
            vault_index["vault"][course_name].append({
                "title": note_file.stem,
                "path": rel_web_path,
                "size": note_file.stat().st_size
            })
    else:
        print(f"Warning: Vault path {vault_path} does not exist.")

    # 4. Map node provenance paths to relative web paths
    for node in graph_data.get("nodes", []):
        if "provenance" in node and isinstance(node["provenance"], list):
            for prov in node["provenance"]:
                if "doc_path" in prov and prov["doc_path"]:
                    orig_p = Path(prov["doc_path"])
                    try:
                        rel = orig_p.relative_to(vault_path)
                        prov["doc_path"] = f"notes/{rel.as_posix()}"
                    except ValueError:
                        matches = list(notes_dist.rglob(f"{orig_p.stem}.md"))
                        if matches:
                            rel = matches[0].relative_to(notes_dist)
                            prov["doc_path"] = f"notes/{rel.as_posix()}"
                        else:
                            prov["doc_path"] = ""

    data_dir = dist_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    (data_dir / "graph.json").write_text(json.dumps(graph_data, indent=2), encoding="utf-8")
    (data_dir / "vault.json").write_text(json.dumps(vault_index, indent=2), encoding="utf-8")

    print("Static site (index.html, app.js, style.css, img/, data/) generated in dist_static/")
    print(f"  Total graph nodes: {len(graph_data.get('nodes', []))}")
    print(f"  Total graph edges: {len(graph_data.get('edges', []))}")
    total_notes = sum(len(v) for v in vault_index["vault"].values())
    print(f"  Total notes copied: {total_notes}")

if __name__ == "__main__":
    export_static_site()
