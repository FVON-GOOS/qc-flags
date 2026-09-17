# -*- coding: utf-8 -*-
"""Builds the QC flags status page from flags.json (status, thresholds, discussion per test)."""
import json, pathlib, html as H
from urllib.parse import quote

OUT = pathlib.Path(__file__).parent
DATA = json.loads((OUT / "flags.json").read_text(encoding="utf-8"))
REPO = DATA["repo"]
BIN = {"compulsory": "agreed", "optional": "optional", "not applied": "notapplied", "to decide": "review"}

def chip(v):
    return f'<span class="fl f{v}">{v}</span>' if v is not None else ""

def row(t):
    thr = "<br>".join(f"{H.escape(text)} {chip(flag)}".strip() for text, flag in t["thresholds"])
    d = t.get("discussion_number")
    issue = f'<a class="issue" href="{REPO}/discussions/{d}" target="_blank" rel="noopener">Discussion #{d}</a>' if d else ""
    return (f'<tr><td>{H.escape(t["test"])}{issue}</td>'
            f'<td><span class="bin {BIN[t["status"]]}">{H.escape(t["status"])}</span></td>'
            f'<td>{H.escape(t["params"])}</td><td>{thr}</td><td>{H.escape(t["discussion"])}</td></tr>')

rows = []
for g in DATA["groups"]:
    rows.append(f'<tr class="grp"><td colspan="5">{H.escape(g["name"])}</td></tr>')
    rows += [row(t) for t in g["tests"]]
table = ('<table class="matrix">\n<thead><tr><th>Test</th><th>Status</th><th>Parameters</th><th>Thresholds</th><th>Discussion</th></tr></thead>\n'
         '<tbody>\n' + "\n".join(rows) + '\n</tbody>\n</table>')

new_issue = f"{REPO}/discussions/{DATA.get('proposals_discussion', '')}"

EXTRA = """
/* flags matrix */
table.matrix{font-size:14.5px} table.matrix td:first-child{font-weight:600;white-space:nowrap}
table.matrix td .fl{margin:0 3px;vertical-align:baseline}
table.matrix tr.grp td{font-family:"Barlow Condensed",sans-serif;font-size:14px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-2);background:var(--shallows);padding:6px 9px}
table.matrix td:nth-child(4){min-width:26ch} table.matrix td:last-child{max-width:40ch}
a.issue{display:block;font-family:"Barlow Condensed",sans-serif;font-size:13px;font-weight:600;letter-spacing:.04em;margin-top:2px}
.bin{display:inline-block;font-family:"Barlow Condensed",sans-serif;font-size:13px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;padding:1px 7px;border-radius:2px;border:1px solid var(--rule);white-space:nowrap}
.bin.agreed{border-color:#2F8F4E;color:#2F8F4E}.bin.optional{border-color:#3C7DC4;color:#3C7DC4}.bin.notapplied{border-color:#7B8B94;color:#7B8B94}.bin.review{border-color:#E0952B;color:#B8741A}
@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]) .bin.review{color:#E9A94A} :root:not([data-theme="light"]) .bin.agreed{color:#4DB56E} :root:not([data-theme="light"]) .bin.optional{color:#5E9BE0} }
:root[data-theme="dark"] .bin.review{color:#E9A94A} :root[data-theme="dark"] .bin.agreed{color:#4DB56E} :root[data-theme="dark"] .bin.optional{color:#5E9BE0}
.three{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:26px;margin-top:8px}
.three h3{font-family:"Barlow Condensed",sans-serif;font-size:20px;font-weight:600;margin:0 0 4px}
.three p{margin:6px 0;font-size:15.5px} .three .fl{margin:0 1px}
.feedback{border-left:3px solid var(--accent);padding:4px 16px;margin:14px 0 18px;max-width:100ch}
.feedback p{margin:8px 0}
"""

CSS = (OUT / "page.css").read_text(encoding="utf-8") + EXTRA
BODY = (OUT / "flags-body.html").read_text(encoding="utf-8").replace("{{TABLE}}", table).replace("{{NEW_ISSUE}}", new_issue)
page = ('<title>FVON QC Flags Status</title>\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700'
        '&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400'
        '&family=IBM+Plex+Mono:wght@400;500&display=swap">\n'
        f'<style>\n{CSS}\n</style>\n{BODY}')
(OUT / "fvon-qc-flags.html").write_text(page, encoding="utf-8")
print("wrote", len(page), "bytes;", sum(len(g["tests"]) for g in DATA["groups"]), "tests")
