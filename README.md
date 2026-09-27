# kol-agent-memory

KoLmafia-local memory/index plane for humans and coding agents.

This project installs a small ASH + relay control surface through KoLmafia Git and then uses a bundled local Python bootstrap to create the exact cross-indexed memory tree requested under `~/.kolmafia/`.

## What it creates

The exact-tree bootstrap creates and cross-links:

```text
~/.kolmafia/
├── kolmaf-ai/
│   └── memory/
│       ├── llm-wiki.html5                  # master index
│       ├── chroma.html5                    # vector-memory plane index
│       ├── langgraph.html5                 # graph/state-machine plane index
│       ├── qtable.html5                    # learned-routing/Q plane index
│       ├── sys/
│       │   └── nano-sec-state-clock.html   # derived-state clock reference
│       ├── env/
│       │   ├── index.html5
│       │   └── session/
│       │       ├── index.html5
│       │       └── player/
│       │           ├── index.html5
│       │           └── tmp/
│       │               └── index.html5
│       ├── state/
│       │   ├── runtime.json
│       │   └── index.html5
│       ├── local/
│       │   ├── README.md
│       │   └── index.html5
│       └── manifest.json
├── data/
│   ├── kolmaf-ai.html5
│   └── kolmaf-ai.html5.html5
├── sessions/kolmaf-ai.html5
├── settings/kolmaf-ai.html5
├── scripts/kolmaf-ai.html5
├── relay/kolmaf-ai.html5
├── ccs/kolmaf-ai.html5
├── chats/kolmaf-ai.html5
└── .config/kolmaf-ai.html
```

The duplicate `data/kolmaf-ai.html5.html5` name is preserved intentionally because it was part of the requested interface. It is treated as an agent-entry alias to the normal `data/kolmaf-ai.html5` plane.

## KoLmafia install

In gCLI:

```text
git checkout https://github.com/donCannoli-burns/kol-agent-memory
call kol-agent-memory.ash setup
```

KoLmafia Git only synchronizes its supported project folders. Current KoLmafia also intentionally prevents normal ASH file writes directly into `settings/` and does not expose arbitrary root-directory creation through `buffer_to_file()`. Therefore the ASH setup installs/refreshes the KoLmafia-supported plane and prints the exact one-time command for the protected-path bootstrap:

```bash
python3 ~/.kolmafia/scripts/kol-agent-memory/bootstrap_exact_tree.py install
```

After that, refresh both planes with:

```text
call kol-agent-memory.ash refresh
```

and, when desired:

```bash
python3 ~/.kolmafia/scripts/kol-agent-memory/bootstrap_exact_tree.py sync
```

## Relay UI

Open the relay browser and choose `kol-agent-memory-relay` from the relay-script selector.

The relay UI is deliberately local and conservative. It can:

- show install/bootstrap state;
- refresh KoLmafia-supported state/index files;
- run this repository's own `git update`;
- show the exact bootstrap/sync commands;
- expose links to the installed agent index and memory wiki.

It does **not** send chat, kmail, trade, combat, or arbitrary game commands.

## v1 verified checkpoint

Verified live on KoLmafia **r29301** on 2026-09-27.

The complete install/bootstrap path succeeded:

```text
git checkout https://github.com/donCannoli-burns/kol-agent-memory
call kol-agent-memory.ash setup
```

Then from the local shell:

```bash
python3 ~/.kolmafia/scripts/kol-agent-memory/bootstrap_exact_tree.py install
```

Then back in gCLI:

```text
call kol-agent-memory.ash refresh exact-tree-ready
```

Final verification commands:

```bash
python3 ~/.kolmafia/scripts/kol-agent-memory/bootstrap_exact_tree.py status
```

and:

```text
call kol-agent-memory.ash status
```

The exact-tree status confirmed all requested index locations as present, including:

```text
~/.kolmafia/kolmaf-ai/memory/llm-wiki.html5
~/.kolmafia/data/kolmaf-ai.html5.html5
~/.kolmafia/sessions/kolmaf-ai.html5
~/.kolmafia/settings/kolmaf-ai.html5
~/.kolmafia/scripts/kolmaf-ai.html5
~/.kolmafia/relay/kolmaf-ai.html5
~/.kolmafia/data/kolmaf-ai.html5
~/.kolmafia/ccs/kolmaf-ai.html5
~/.kolmafia/chats/kolmaf-ai.html5
~/.kolmafia/.config/kolmaf-ai.html
```

The KoLmafia-side status also confirmed:

- Git install detected;
- player context resolved;
- refresh marker recorded as `exact-tree-ready`;
- master wiki and agent index paths resolved;
- relay entrypoint available as `kol-agent-memory-relay`.

### Compatibility fixes verified during first live install

Two first-install issues were found and corrected before the verified checkpoint:

1. The relay script originally shared the basename `kol-agent-memory.ash` with the controller script, causing KoLmafia to report “too many matches.” The relay entrypoint is now uniquely named `kol-agent-memory-relay.ash`.
2. `path` is a reserved ASH identifier. The controller now uses `file_path` instead.

These fixes are included in current `main`.

## Memory model

The master `llm-wiki.html5` is the cross-index. It treats memory as four related but distinct planes:

- **SYSTEM** — implementation contracts, runtime surfaces, paths, ownership, provenance.
- **STATE** — derived/current runtime facts and snapshots; replaceable and refreshable.
- **LOCAL** — operator/agent notes intended to survive sessions.
- **ROUTING** — vector (`chroma`), graph (`langgraph`), and Q-table indexes used to find or route memory; these are indexes over memory, not authority over game state.

The design follows a strict rule: observation/index surfaces may inform an action but do not authorize it.

## Commands

```text
call kol-agent-memory.ash status
call kol-agent-memory.ash setup
call kol-agent-memory.ash refresh [reason]
call kol-agent-memory.ash update
call kol-agent-memory.ash bootstrap-command
call kol-agent-memory.ash sync-command
call kol-agent-memory.ash help
```

Python exact-tree tool:

```text
bootstrap_exact_tree.py install [--root ~/.kolmafia] [--player NAME]
bootstrap_exact_tree.py sync    [--root ~/.kolmafia] [--player NAME]
bootstrap_exact_tree.py status  [--root ~/.kolmafia]
```

No file contents from `settings/` or `chats/` are ingested automatically. Those files are represented as indexed locations only. Session contents are also not scraped by the Python bootstrap; the ASH side writes only its own generated session index page.

## Update

```text
call kol-agent-memory.ash update
```

or the normal KoLmafia Git command:

```text
git update donCannoli-burns-kol-agent-memory
```

Then rerun the Python `sync` command if you want the protected-path pages regenerated with the newest templates.

## Design sources

The implementation is adapted from the supplied local HTML5 memory/wiki, derived-state, vector, graph, Q-table, and nano-state-clock artifacts. Those references are not vendored wholesale; this repository uses them as architectural/design inputs and keeps the shipped KoLmafia package small.

## License

MIT. See `LICENSE`.
