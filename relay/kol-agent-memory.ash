string PROJECT_ID = "donCannoli-burns-kol-agent-memory";

string esc(string value) {
    string out = replace_string(value, "&", "&amp;");
    out = replace_string(out, "<", "&lt;");
    out = replace_string(out, ">", "&gt;");
    out = replace_string(out, "\"", "&quot;");
    return out;
}

void emit_header() {
    write("<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>");
    write("<title>KoL Agent Memory</title><style>:root{color-scheme:dark;--bg:#061011;--panel:#0b1b1d;--panel2:#0e2224;--line:#1c3a3e;--text:#d9f0ec;--muted:#71928f;--cyan:#53e5d5;--mint:#95ffd7;--amber:#ffba62}*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at 85% 0,#12383a55,transparent 34%),var(--bg);color:var(--text);font:14px/1.5 ui-monospace,monospace}.wrap{max-width:1180px;margin:auto;padding:22px}.hero,.card{border:1px solid var(--line);background:rgba(11,27,29,.95);border-radius:14px;padding:18px;margin:12px 0}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:10px}.k{color:var(--cyan);font-size:11px;letter-spacing:.14em}.muted{color:var(--muted)}a{color:var(--cyan)}button{background:#102628;color:var(--text);border:1px solid #315e60;border-radius:9px;padding:9px 12px;cursor:pointer}code,pre{background:#041012;border:1px solid var(--line);border-radius:7px;padding:2px 5px;overflow:auto}.ok{color:var(--mint)}.warn{color:var(--amber)}form{display:inline}</style></head><body><main class='wrap'>");
}

void action_button(string action, string label) {
    write("<form method='get'><input type='hidden' name='action' value='" + esc(action) + "'><button type='submit'>" + esc(label) + "</button></form> ");
}

void main() {
    string action = form_field("action");
    string notice = "";
    if (action == "refresh") {
        boolean ok = cli_execute("call kol-agent-memory.ash refresh relay-ui");
        notice = ok ? "Supported memory plane refreshed." : "Refresh reported a failure; inspect gCLI.";
    } else if (action == "setup") {
        boolean ok = cli_execute("call kol-agent-memory.ash setup");
        notice = ok ? "KoLmafia-side setup completed." : "Setup reported a failure; inspect gCLI.";
    } else if (action == "update") {
        boolean ok = cli_execute("call kol-agent-memory.ash update");
        notice = ok ? "Project update command completed." : "Update reported a failure; inspect gCLI.";
    }

    emit_header();
    write("<section class='hero'><div class='k'>LOCAL MEMORY BUS · KOLMAF-AI</div><h1>KoL Agent Memory</h1><p class='muted'>Human + agent control surface for the cross-indexed system/state/local memory tree. Index surfaces inform; they do not authorize execution.</p></section>");
    if (notice != "") write("<div class='card'><b>" + esc(notice) + "</b></div>");

    write("<div class='card'>");
    action_button("refresh", "Refresh state indexes");
    action_button("setup", "Run KoLmafia setup");
    action_button("update", "Git update project");
    write("</div>");

    write("<section class='grid'>");
    string git_badge = git_exists(PROJECT_ID) ? "<b class='ok'>YES</b>" : "<b class='warn'>NO</b>";
    write("<article class='card'><div class='k'>INSTALL</div><h2>KoLmafia plane</h2><p>Git installed: " + git_badge + "</p><p>Version: " + esc(get_version()) + " / r" + get_revision() + "</p><p>Player: " + esc(my_name()) + "</p></article>");
    write("<article class='card'><div class='k'>MASTER</div><h2>LLM wiki</h2><p><code>~/.kolmafia/kolmaf-ai/memory/llm-wiki.html5</code></p><p class='muted'>Created by the exact-tree bootstrap.</p></article>");
    write("<article class='card'><div class='k'>AGENT</div><h2>Fallback index</h2><p><a href='/kolmaf-ai.html5'>data/kolmaf-ai.html5</a></p><p><a href='/kolmaf-ai.html5.html5'>data/kolmaf-ai.html5.html5</a></p></article>");
    write("</section>");

    write("<section class='card'><div class='k'>ONE-TIME EXACT TREE</div><h2>Protected-path bootstrap</h2><p>Current KoLmafia intentionally does not let normal ASH file writers create arbitrary root/settings/chat/config files. Run this once from your local shell:</p><pre>python3 ~/.kolmafia/scripts/kol-agent-memory/bootstrap_exact_tree.py install</pre><p>Refresh later with:</p><pre>python3 ~/.kolmafia/scripts/kol-agent-memory/bootstrap_exact_tree.py sync</pre></section>");

    write("<section class='card'><div class='k'>PLANES</div><div class='grid'><div><b>Chroma/vector</b><p class='muted'>Similarity/retrieval index.</p></div><div><b>LangGraph</b><p class='muted'>State/transition topology and resumable execution memory.</p></div><div><b>Q-table</b><p class='muted'>Learned routing hints, never action authority.</p></div><div><b>Nano-state clock</b><p class='muted'>Derived time/state reference, no fake tick accumulator.</p></div></div></section>");
    write("</main></body></html>");
}
