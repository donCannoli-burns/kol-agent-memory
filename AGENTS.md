# Agent guide — kol-agent-memory

Start at `~/.kolmafia/kolmaf-ai/memory/llm-wiki.html5` after bootstrap, or `~/.kolmafia/data/kolmaf-ai.html5` before bootstrap.

## Authority rules

1. Memory/index files are evidence and navigation, not execution authority.
2. Do not treat Q, vector similarity, graph proximity, or a stale snapshot as permission to mutate KoL/game state.
3. Do not scrape credentials, raw settings, or chat contents into memory by default.
4. Prefer refreshable derived state over duplicated counters.
5. Preserve source/provenance paths in generated state.
6. Temporary/session memory may be replaced; local/operator memory should not be overwritten by sync unless explicitly marked generated.

## Maintainer workflow

- Edit templates under `data/kol-agent-memory/templates/`.
- Keep `scripts/kol-agent-memory.ash` compatible with current KoLmafia ASH.
- Keep exact-tree filesystem work in `scripts/kol-agent-memory/bootstrap_exact_tree.py`; do not use ASH path-traversal workarounds.
- Run `python3 scripts/kol-agent-memory/bootstrap_exact_tree.py self-test` in a checkout before shipping.
- Verify all generated HTML contains a backlink to the master wiki.
