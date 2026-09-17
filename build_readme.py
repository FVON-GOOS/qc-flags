# -*- coding: utf-8 -*-
"""Builds README.md for FVON-GOOS/qc-flags from flags.json (needs the discussion numbers filled in)."""
import json, pathlib, sys

SRC = pathlib.Path(__file__).parent / "flags.json"
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).parent / "README.md"
data = json.loads(SRC.read_text(encoding="utf-8"))
REPO = data["repo"]

def thr(t):
    return "<br>".join(text + (f" → **{flag}**" if flag is not None else "") for text, flag in t["thresholds"])

lines = []
lines.append("# FVON QC flags: where we are\n")
lines.append("One row per test: its status, the parameters it flags, the thresholds and the flag each condition produces, and what the group still has to decide. "
             "The full page with the three flag standards is in [`docs/index.html`](docs/index.html) "
             f"(rendered at {data.get('pages_url', '')}).\n" if data.get("pages_url") else
             "One row per test: its status, the parameters it flags, the thresholds and the flag each condition produces, and what the group still has to decide.\n")
lines.append("**How to give feedback.** Every test has a [Discussion](../../discussions). Reply there with the status you want (compulsory, optional, not applied), "
             "the thresholds you would apply and why. One reply per person is enough; edit it if you change your mind. This summary is updated from the threads before each subcommittee meeting. "
             f"To suggest a test that is not listed, use the [proposals thread]({REPO}/discussions/{data.get('proposals_discussion', '')}).\n")
lines.append("## Flag scale\n")
lines.append("FVON uses the IOC Manuals and Guides 54 scale: 0 no QC, 1 good, 2 probably good, 3 suspect, 4 bad, 5 corrected, 9 missing. One flag per variable; a derived variable inherits the worst flag of its inputs. "
             "QARTOD uses 1 pass, 2 not evaluated, 3 suspect, 4 fail, 9 missing. SeaDataNet (L20) uses 0 to 9 with 3 meaning probably bad, plus 6 below detection, 7 in excess, 8 interpolated and letter codes for uncertain values.\n")
lines.append("## Test by test\n")
lines.append("| Test | Status | Parameters | Thresholds | Discussion |")
lines.append("|---|---|---|---|---|")
for g in data["groups"]:
    lines.append(f"| **{g['name']}** | | | | |")
    for t in g["tests"]:
        d = t.get("discussion_number")
        link = f"[{t['test']}]({REPO}/discussions/{d})" if d else t["test"]
        std = "; ".join(f"{k}: {v}" for k, v in t.get("standards", {}).items())
        if std: link += f"<br><sub>{std}</sub>"
        lines.append(f"| {link} | {t['status']} | {t['params']} | {thr(t)} | {t['discussion']} |")
lines.append("")
lines.append("## Files\n")
lines.append("- `flags.json`: the data behind the table (status, parameters, thresholds, discussion per test). Change it and run `build_flags.py` and `build_readme.py`.")
lines.append("- `docs/index.html`: the full page, including the description of the FVON, QARTOD and SeaDataNet standards.")
lines.append("- `build_flags.py`, `build_readme.py`, `flags-body.html`, `page.css`: the generators.\n")
lines.append("Maintained by the FVON Data Management Subcommittee.")
OUT.write_text("\n".join(lines), encoding="utf-8")
print("wrote", OUT, len("\n".join(lines)), "bytes")
