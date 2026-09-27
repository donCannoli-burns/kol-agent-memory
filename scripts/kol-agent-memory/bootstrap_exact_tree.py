#!/usr/bin/env python3
"""Create and refresh the exact ~/.kolmafia KoLmaf-AI memory tree.

This helper exists because current KoLmafia intentionally limits Git synchronization
and normal ASH file writes to a restricted set of directories. It performs only
local filesystem work beneath the selected KoLmafia root and never reads secrets or
chat contents.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

PROJECT = "kol-agent-memory"

REQUESTED_FILES = [
    "data/kolmaf-ai.html5.html5",
    "sessions/kolmaf-ai.html5",
    "settings/kolmaf-ai.html5",
    "scripts/kolmaf-ai.html5",
    "relay/kolmaf-ai.html5",
    "data/kolmaf-ai.html5",
    "ccs/kolmaf-ai.html5",
    "chats/kolmaf-ai.html5",
    ".config/kolmaf-ai.html",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def default_root() -> Path:
    return Path.home() / ".kolmafia"


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def file_uri(path: Path) -> str:
    return path.resolve().as_uri()


def detect_player(root: Path, explicit: str | None) -> str:
    if explicit:
        return explicit
    sessions = root / "sessions"
    if sessions.is_dir():
        names = sorted(sessions.glob("active_session.*"), key=lambda p: p.stat().st_mtime, reverse=True)
        if names:
            return names[0].name.split("active_session.", 1)[1]
    return "unknown"


def templates_dir(root: Path) -> Path:
    installed = root / "data" / PROJECT / "templates"
    if installed.is_dir():
        return installed
    # Supports self-test / source-checkout execution.
    return Path(__file__).resolve().parents[2] / "data" / PROJECT / "templates"


def html_page(template: str, *, title: str, kicker: str, body: str, master: Path, path: Path) -> str:
    return (template
        .replace("{{TITLE}}", html.escape(title))
        .replace("{{KICKER}}", html.escape(kicker))
        .replace("{{BODY}}", body)
        .replace("{{MASTER_URI}}", file_uri(master))
        .replace("{{PATH}}", html.escape(str(path))))


def plane_body(name: str, description: str, bullets: Iterable[str]) -> str:
    lis = "".join(f"<li>{html.escape(x)}</li>" for x in bullets)
    return f"<h2>{html.escape(name)}</h2><p>{html.escape(description)}</p><ul>{lis}</ul>"


def desired_paths(root: Path) -> dict[str, Path]:
    mem = root / "kolmaf-ai" / "memory"
    return {
        "master": mem / "llm-wiki.html5",
        "chroma": mem / "chroma.html5",
        "langgraph": mem / "langgraph.html5",
        "qtable": mem / "qtable.html5",
        "clock": mem / "sys" / "nano-sec-state-clock.html",
        "env": mem / "env" / "index.html5",
        "session": mem / "env" / "session" / "index.html5",
        "player": mem / "env" / "session" / "player" / "index.html5",
        "tmp": mem / "env" / "session" / "player" / "tmp" / "index.html5",
        "state": mem / "state" / "index.html5",
        "local": mem / "local" / "index.html5",
        "manifest": mem / "manifest.json",
        "runtime": mem / "state" / "runtime.json",
    }


def build_runtime(root: Path, player: str) -> dict:
    dirs = ["data", "sessions", "settings", "scripts", "relay", "ccs", "chats", ".config"]
    return {
        "generated_at": now_iso(),
        "kolmafia_root": str(root),
        "player": player,
        "directories": {d: {"exists": (root / d).exists(), "path": str(root / d)} for d in dirs},
        "authority_note": "Memory/index surfaces inform; they do not authorize execution.",
        "privacy_note": "No settings contents, chat contents, or session contents were ingested by this sync.",
    }


def render_exact(root: Path, player: str) -> None:
    tdir = templates_dir(root)
    master_t = read_text(tdir / "master.html5")
    plane_t = read_text(tdir / "plane.html5")
    clock_t = read_text(tdir / "nano-sec-state-clock.html")
    p = desired_paths(root)
    master = p["master"]

    for path in p.values():
        if path.suffix:
            path.parent.mkdir(parents=True, exist_ok=True)
    (root / "kolmaf-ai" / "memory" / "env" / "session" / "player" / "tmp").mkdir(parents=True, exist_ok=True)
    (root / "kolmaf-ai" / "memory" / "local").mkdir(parents=True, exist_ok=True)

    runtime = build_runtime(root, player)
    atomic_write(p["runtime"], json.dumps(runtime, indent=2, sort_keys=True) + "\n")

    plane_specs = {
        "chroma": ("Chroma / Vector Memory", "ROUTING · VECTOR", "Semantic retrieval/vector index surface.", [
            "Use similarity to retrieve candidate memory, not to assert truth.",
            "Preserve source pointers and freshness alongside embeddings.",
            "Rebuildable index data should stay separate from durable local notes.",
        ]),
        "langgraph": ("LangGraph / State Graph Memory", "ROUTING · GRAPH", "Explicit state/transition/checkpoint topology for resumable agent work.", [
            "Transitions should emit explicit evidence/events.",
            "Checkpoint state should be resumable and drift-detectable.",
            "Graph position is context, not permission to execute an external action.",
        ]),
        "qtable": ("Q-Table Routing Memory", "ROUTING · Q", "Learned routing preference surface for choosing retrieval/action-planning lanes.", [
            "Q-values are routing hints, never direct game-action authority.",
            "Keep state/action vocabularies explicit and bounded.",
            "Reward updates should be auditable and reversible/rebuildable where possible.",
        ]),
        "env": ("Environment Memory", "SYSTEM · ENV", "Local runtime/environment index.", [
            f"KoLmafia root: {root}", f"Detected player: {player}", "This index stores metadata only, not secrets." ]),
        "session": ("Session Memory", "STATE · SESSION", "Session-scoped navigation and generated state.", [
            "Session evidence can be refreshed or discarded.",
            "Raw session contents are not ingested by the bootstrap.",
            "Use explicit evidence/provenance when an agent resumes." ]),
        "player": ("Player Memory", "STATE · PLAYER", "Player-scoped index beneath the session plane.", [
            f"Detected player: {player}",
            "Keep account-specific secrets outside generated memory.",
            "Re-observe current game state before mutations." ]),
        "tmp": ("Temporary Memory", "STATE · TMP", "Scratch area for disposable generated artifacts.", [
            "Safe to replace on sync when marked generated.",
            "Do not store durable operator notes here.",
            "Do not use scratch data as long-term authority." ]),
        "state": ("Runtime State", "STATE · CURRENT", "Generated current-state metadata.", [
            "Source: state/runtime.json",
            "Projection is refreshable and may become stale.",
            "No hidden tick accumulator or assumed missed effects." ]),
        "local": ("Local Durable Memory", "LOCAL · DURABLE", "Human/agent notes intended to survive sessions.", [
            "Generated sync does not overwrite README.md or additional hand-authored files.",
            "Store decisions with provenance and dates.",
            "Prefer compact durable facts over raw transcript dumps." ]),
    }
    for key, (title, kicker, desc, bullets) in plane_specs.items():
        body = plane_body(title, desc, bullets)
        atomic_write(p[key], html_page(plane_t, title=title, kicker=kicker, body=body, master=master, path=p[key]))

    local_readme = root / "kolmaf-ai" / "memory" / "local" / "README.md"
    if not local_readme.exists():
        atomic_write(local_readme, "# Local KoLmaf-AI Memory\n\nHand-authored durable notes live here. Generated sync will not overwrite this file.\n")

    clock = clock_t.replace("{{MASTER_URI}}", file_uri(master))
    atomic_write(p["clock"], clock)

    requested = [root / x for x in REQUESTED_FILES]
    rows = []
    for path in requested:
        rows.append(f"<tr><td><a href=\"{file_uri(path)}\">{html.escape(path.name)}</a></td><td><code>{html.escape(str(path))}</code></td><td>{html.escape(path.parent.name or '.')} plane</td></tr>")
    rows.extend([
        f"<tr><td><a href=\"{file_uri(p['chroma'])}\">chroma.html5</a></td><td><code>{html.escape(str(p['chroma']))}</code></td><td>vector retrieval index</td></tr>",
        f"<tr><td><a href=\"{file_uri(p['langgraph'])}\">langgraph.html5</a></td><td><code>{html.escape(str(p['langgraph']))}</code></td><td>graph/state topology</td></tr>",
        f"<tr><td><a href=\"{file_uri(p['qtable'])}\">qtable.html5</a></td><td><code>{html.escape(str(p['qtable']))}</code></td><td>learned routing</td></tr>",
    ])

    master_html = master_t
    replacements = {
        "{{CONFIG_URI}}": file_uri(root / ".config" / "kolmaf-ai.html"),
        "{{SCRIPTS_URI}}": file_uri(root / "scripts" / "kolmaf-ai.html5"),
        "{{RELAY_URI}}": file_uri(root / "relay" / "kolmaf-ai.html5"),
        "{{CCS_URI}}": file_uri(root / "ccs" / "kolmaf-ai.html5"),
        "{{STATE_URI}}": file_uri(p["state"]),
        "{{SESSIONS_URI}}": file_uri(root / "sessions" / "kolmaf-ai.html5"),
        "{{CLOCK_URI}}": file_uri(p["clock"]),
        "{{LOCAL_URI}}": file_uri(p["local"]),
        "{{CHROMA_URI}}": file_uri(p["chroma"]),
        "{{LANGGRAPH_URI}}": file_uri(p["langgraph"]),
        "{{QTABLE_URI}}": file_uri(p["qtable"]),
        "{{ROWS}}": "".join(rows),
        "{{RUNTIME_PRE}}": html.escape(json.dumps(runtime, indent=2, sort_keys=True)),
        "{{MANIFEST_URI}}": file_uri(p["manifest"]),
    }
    for k, v in replacements.items():
        master_html = master_html.replace(k, v)
    atomic_write(master, master_html)

    index_specs = {
        "data/kolmaf-ai.html5": ("KoLmaf-AI Data Memory", "SYSTEM · DATA", "Machine-readable/generated agent data plane."),
        "data/kolmaf-ai.html5.html5": ("KoLmaf-AI Agent Data Alias", "AGENT · DATA", "Intentional duplicate-extension agent entry alias."),
        "sessions/kolmaf-ai.html5": ("KoLmaf-AI Session Index", "STATE · SESSIONS", "Session location index. This bootstrap does not ingest session contents."),
        "settings/kolmaf-ai.html5": ("KoLmaf-AI Settings Index", "SYSTEM · SETTINGS", "Settings location index only. Preference/credential contents are not ingested."),
        "scripts/kolmaf-ai.html5": ("KoLmaf-AI Scripts Index", "SYSTEM · SCRIPTS", "Scripts/control-plane location index."),
        "relay/kolmaf-ai.html5": ("KoLmaf-AI Relay Index", "SYSTEM · RELAY", "Relay/UI location index."),
        "ccs/kolmaf-ai.html5": ("KoLmaf-AI CCS Index", "SYSTEM · CCS", "CCS location index only; this HTML file is not a combat strategy."),
        "chats/kolmaf-ai.html5": ("KoLmaf-AI Chats Index", "PRIVATE · CHATS", "Chat location index only. Chat contents are not ingested by default."),
        ".config/kolmaf-ai.html": ("KoLmaf-AI Config Index", "SYSTEM · CONFIG", "Local configuration location index."),
    }
    for rel, (title, kicker, desc) in index_specs.items():
        path = root / rel
        body = plane_body(title, desc, [
            f"Directory: {path.parent}",
            "Cross-indexed to the LLM Memory Wiki.",
            "This page stores navigation/metadata, not execution authority.",
        ])
        atomic_write(path, html_page(plane_t, title=title, kicker=kicker, body=body, master=master, path=path))

    player_dir = root / "kolmaf-ai" / "memory" / "env" / "session" / "player" / player
    player_dir.mkdir(parents=True, exist_ok=True)
    player_index = player_dir / "index.html5"
    atomic_write(player_index, html_page(plane_t, title=f"Player · {player}", kicker="STATE · PLAYER INSTANCE", body=plane_body(player, "Player-specific memory location.", ["No credentials stored here by bootstrap.", "Generated metadata may be replaced on sync."]), master=master, path=player_index))

    manifest = {
        "schema": "kol-agent-memory/1",
        "generated_at": now_iso(),
        "root": str(root),
        "player": player,
        "master": str(master),
        "requested_files": [str(root / x) for x in REQUESTED_FILES],
        "memory_planes": {k: str(v) for k, v in p.items()},
        "rules": {
            "index_is_not_authority": True,
            "ingest_settings_contents": False,
            "ingest_chat_contents": False,
            "ingest_session_contents": False,
            "generated_state_replaceable": True,
            "local_memory_preserved": True,
        },
    }
    atomic_write(p["manifest"], json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def status(root: Path) -> int:
    p = desired_paths(root)
    checks = [("master", p["master"])] + [(rel, root / rel) for rel in REQUESTED_FILES]
    ok = True
    for label, path in checks:
        exists = path.is_file()
        ok = ok and exists
        print(f"{'OK  ' if exists else 'MISS'} {label}: {path}")
    return 0 if ok else 1


def self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="kol-agent-memory-test-") as td:
        root = Path(td) / ".kolmafia"
        render_exact(root, "testplayer")
        rc = status(root)
        master = desired_paths(root)["master"]
        text = master.read_text(encoding="utf-8")
        assert "LLM Memory Wiki" in text
        assert "testplayer" in text
        assert "{{" not in text
        for rel in REQUESTED_FILES:
            t = (root / rel).read_text(encoding="utf-8")
            assert "LLM Memory Wiki" in t or "llm-wiki.html5" in t
        print("SELF-TEST PASS")
        return rc


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["install", "sync", "status", "self-test"])
    ap.add_argument("--root", type=Path, default=default_root())
    ap.add_argument("--player")
    args = ap.parse_args()

    if args.command == "self-test":
        return self_test()

    root = args.root.expanduser().resolve()
    if args.command == "status":
        return status(root)

    root.mkdir(parents=True, exist_ok=True)
    player = detect_player(root, args.player)
    render_exact(root, player)
    print(f"{args.command.upper()} complete: {desired_paths(root)['master']}")
    return status(root)


if __name__ == "__main__":
    raise SystemExit(main())
