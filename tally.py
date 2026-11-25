# -*- coding: utf-8 -*-
"""Tally the QC flags poll.

Reads the comments on the poll discussion (its number is `poll_discussion` in flags.json),
parses each ballot line ("Spike: Req  --> note") and writes:

  RESULTS.md            the results page for the group: the decision on one screen, the
                        comparison with the current status, votes and comments underneath
  results/summary.csv   one row per test: current status, poll result and the vote counts
  results/ballots.csv   one row per voter and test, as parsed, with the note

Levels are Req (Required), Opt (Optional) and N/A (Not applicable). A line left blank is an
abstention. A voter's latest ballot comment is the one that counts.

Runs locally (token from GH_TOKEN, GITHUB_TOKEN or `gh auth token`). No third-party packages.
"""
import csv, json, os, re, subprocess, urllib.request
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = json.loads((HERE / "flags.json").read_text(encoding="utf-8"))
REPO_URL = DATA["repo"]
OWNER, REPO = REPO_URL.rstrip("/").split("/")[-2:]
POLL = DATA["poll_discussion"]
TESTS = DATA["tests"]

CODES = ["Req", "Opt", "N/A"]
LABEL = {"Req": "Required", "Opt": "Optional", "N/A": "Not applicable"}
CURRENT = {"required": "Req", "optional": "Opt", "not applicable": "N/A"}      # "to decide" has no level


# ---------------------------------------------------------------- GitHub
def token():
    for k in ("GH_TOKEN", "GITHUB_TOKEN"):
        if os.environ.get(k):
            return os.environ[k]
    return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()


def fetch_comments():
    q = """query { repository(owner:"%s", name:"%s") { discussion(number:%d) {
             comments(first:100) { nodes { author { login } updatedAt url body isMinimized } } } } }""" % (OWNER, REPO, POLL)
    req = urllib.request.Request("https://api.github.com/graphql", data=json.dumps({"query": q}).encode(),
                                 headers={"Authorization": f"bearer {token()}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        data = json.load(r)
    if "errors" in data:
        raise SystemExit(f"GraphQL error: {data['errors']}")
    return data["data"]["repository"]["discussion"]["comments"]["nodes"]


# ---------------------------------------------------------------- parsing
LEVEL_RE = re.compile(r"^\s*(req(?:uired)?|compulsory|mandatory|opt(?:ional)?|n/a|na\b|not(?:\s+(?:applicable|applied|needed|relevant))?)"
                      r"(?![A-Za-z])", re.I)


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def parse_value(rest):
    """'Req --> note' -> ('Req', 'note'); no recognised level -> ('', rest)."""
    rest = rest.strip()
    m = LEVEL_RE.match(rest)
    if not m:
        return "", rest
    word = m.group(1).lower()
    level = "Req" if word[:3] in ("req", "com", "man") else "Opt" if word[:3] == "opt" else "N/A"
    return level, re.sub(r"^[\s,:;>\-]+", "", rest[m.end():]).strip()


def parse_ballot(body):
    """{test name: (level, note)} for the lines of a comment that name a test and carry a vote."""
    by_norm = {norm(t["test"]): t["test"] for t in TESTS}
    votes = {}
    for raw in body.splitlines():
        line = raw.strip().lstrip("-*| ").replace("`", "")
        if ":" not in line:
            continue
        k, rest = line.split(":", 1)
        test = by_norm.get(norm(k))
        if test:
            level, note = parse_value(rest)
            if level:
                votes[test] = (level, note)
    return votes


# ---------------------------------------------------------------- results page
def md(text):
    return text.replace("|", "\\|").replace("\n", " ")


def votes_text(c):
    return " · ".join(f"{LABEL[k]} {c[k]}" for k in CODES if c.get(k)) or "no votes"


def result_of(c):
    """'Req' | 'Opt' | 'N/A' | 'tied' | 'none'"""
    if not c:
        return "none"
    top = max(c.values())
    lead = [k for k in CODES if c.get(k, 0) == top]
    return lead[0] if len(lead) == 1 else "tied"


def results_page(rows, voters, last):
    cols = CODES + [k for k in ("tied", "none") if any(r["result"] == k for r in rows)]
    label = dict(LABEL, tied="Undecided (tied)", none="No votes yet")
    names = lambda k: "<br>".join(r["test"] for r in rows if r["result"] == k) or "–"
    count = lambda k: sum(r["result"] == k for r in rows)
    poll_url = f"{REPO_URL}/discussions/{POLL}"

    head = f"{len(rows)} tests · {len(voters)} voter{'s' if len(voters) != 1 else ''}"
    L = ["# QC flags: poll results", "", head + (f" · last ballot {last}" if last else ""), ""]
    if not voters:
        L += [f"No ballots yet. Vote in the [poll]({poll_url}).", ""]
    L += ["## The decision", "",
          "| " + " | ".join(f"{label[k]} ({count(k)})" for k in cols) + " |",
          "|" + "---|" * len(cols),
          "| " + " | ".join(names(k) for k in cols) + " |", "",
          "**Required:** every FVON network applies the test. **Optional:** a network may apply it. "
          "**Not applicable:** FVON does not apply the test.", "",
          "## Compared with the current status", "",
          "| Test | Current status | Poll result | Change |", "|---|---|---|---|"]
    for r in rows:
        cur, res = r["current"], r["result"]
        poll = LABEL.get(res, label[res].lower() if res in ("tied", "none") else res)
        if res in ("tied", "none"):
            change = ""
        elif CURRENT.get(cur) == res:
            change = "same"
        elif cur == "to decide":
            change = "**new decision**"
        else:
            change = "**changed**"
        L.append(f"| {r['test']} | {cur} | {poll} | {change} |")
    L += ["", "## Detail", "", "<details>", "<summary>Votes behind each result</summary>", "",
          "| Test | Votes | " + " | ".join(LABEL[k] for k in CODES) + " |", "|---|---|---|---|---|"]
    for r in rows:
        who = [", ".join(v for v, lv, n in r["cast"] if lv == k) or "–" for k in CODES]
        L.append(f"| {r['test']} | {votes_text(r['counts'])} | " + " | ".join(who) + " |")
    L += ["", "</details>", "", "<details>", "<summary>Voter comments</summary>", "",
          "| Test | Voter | Comment |", "|---|---|---|"]
    for r in rows:
        for v, lv, n in r["cast"]:
            if n:
                L.append(f"| {r['test']} | {v} | {md(n)} |")
    L += ["", "</details>", ""]
    if voters:
        L += [f"Voters: {', '.join(voters)}. Not every voter voted on every test.", ""]
    L += [f"Generated by [`tally.py`](tally.py) from the ballots in the [poll]({poll_url}); do not edit by hand. "
          "Every ballot line is in [`results/ballots.csv`](results/ballots.csv).", ""]
    return "\n".join(L)


# ---------------------------------------------------------------- main
def main():
    latest = {}                                   # voter -> (date, url, votes); a later ballot replaces an earlier one
    for c in fetch_comments():
        if c.get("isMinimized"):
            continue
        votes = parse_ballot(c["body"])
        if not votes:
            continue                              # a discussion comment, not a ballot
        who = (c.get("author") or {}).get("login") or "ghost"
        if who not in latest or c["updatedAt"] >= latest[who][0]:
            latest[who] = (c["updatedAt"], c["url"], votes)
    voters = list(latest)
    last = max((v[0][:10] for v in latest.values()), default="")

    rows, ballots = [], []
    for t in TESTS:
        cast = [(who, *latest[who][2][t["test"]]) for who in voters if t["test"] in latest[who][2]]
        counts = Counter(lv for _, lv, _ in cast)
        rows.append({"test": t["test"], "current": t["status"], "counts": counts, "cast": cast,
                     "result": result_of(counts)})
        for who, lv, note in cast:
            ballots.append({"Test": t["test"], "Voter": who, "Date": latest[who][0][:10], "Vote": lv,
                            "Note": note, "Link": latest[who][1]})
    summary = [{"Test": r["test"], "Current status": r["current"],
                "Poll result": LABEL.get(r["result"], {"tied": "tied", "none": ""}.get(r["result"], "")),
                "Required": r["counts"].get("Req", 0), "Optional": r["counts"].get("Opt", 0),
                "Not applicable": r["counts"].get("N/A", 0)} for r in rows]

    out = HERE / "results"
    out.mkdir(exist_ok=True)

    def write(name, data, fields):
        with open(out / name, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader(); w.writerows(data)
    write("summary.csv", summary, ["Test", "Current status", "Poll result", "Required", "Optional", "Not applicable"])
    write("ballots.csv", ballots, ["Test", "Voter", "Date", "Vote", "Note", "Link"])
    (HERE / "RESULTS.md").write_text(results_page(rows, voters, last), encoding="utf-8", newline="\n")
    print(f"{len(rows)} tests, {len(voters)} ballots -> RESULTS.md, results/")


if __name__ == "__main__":
    main()
