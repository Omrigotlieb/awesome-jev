#!/usr/bin/env python3
"""Generate README.md from entries.json. Run: python3 build_readme.py"""
import json, datetime, pathlib, collections

ROOT = pathlib.Path(__file__).resolve().parent
DATA = json.load(open(ROOT / "entries.json"))
CATS = DATA["categories"]; E = DATA["entries"]; META = DATA["meta"]
A = "https://github.com/user-attachments/assets"

SHOTS = {
 "hero": f"{A}/d6f3eaf6-eeaa-40ea-870a-b37721147496",
 "bench": f"{A}/d28a5b27-d8c6-4ae5-b9e0-f26151132190",
 "docs": f"{A}/5e754e4f-e4c6-4598-b2b0-c0024cac7474",
 "madewith": f"{A}/3b4e0e34-b8d5-4ca0-84c6-12719d9840f2",
 "classifier": f"{A}/7a71f6f1-5f68-409e-9b30-97bfe5996450",
 "typewriter": f"{A}/09c06676-2e6c-4300-b138-63033952f254",
 "tetris": f"{A}/5fc57b75-0cac-4143-8409-c2a589886aee",
 "pacman": f"{A}/eaf7db8d-eb8e-4e5e-8fbf-e60103e94868",
 "chess": f"{A}/e72f7ae6-ac81-42fd-8fff-5aef635b0771",
 "rustline": f"{A}/dbca4d76-6f3b-4d4d-8658-807ea6c0e55d",
 "semantic": f"{A}/f5217f84-2888-4872-b7e5-bccc5848e711",
 "crowdcheck": f"{A}/7c809a7b-87e6-49f7-a69f-d5fe602413e8",
 "evals": f"{A}/50ec1eda-4191-405b-a81e-a9184a3b6ef3",
 "blink": f"{A}/44ad74ac-9574-44af-9238-d6b12482f48b",
 "yesno": f"{A}/9a26ec0a-5780-4875-9e33-92e8fa0b46fd",
 "hollow": f"{A}/cb78981f-59a3-4487-88e2-b16866ffa20e",
 "gameplan": f"{A}/4f064d53-099f-49c2-bf94-8e435406f3ae",
}

GALLERY = [
 ("Jev plays Pac-Man", "https://jev-pacman.ephraimduncan.com", "pacman",
  "Every junction is one typed question. The panel shows the live action probabilities (up 20% / right 27% / <b>down 53%</b>), the confidence, and an 888 ms latency for the decision that produced this frame."),
 ("Jev Chess", "https://chess-jev.loomens.com", "chess",
  "Two Jev personas play each other. The right rail is a decision trace: the chosen move, per-move probabilities, and which doctrine (Balanced / Aggressive / Defensive / Chaotic) shaped the choice."),
 ("Workflow evals", "https://evals.typesafe.ai", "evals",
  "TypeSafe's own accuracy-vs-cost frontier across four real workflows — security incidents, agent trace observability, invoice processing, customer service — comparing structured workflows against standalone prompts."),
 ("TypeSafe Typewriter", "https://typesafe-demo.val.run", "typewriter",
  "Sixteen typed judgments about your text, re-asked on every keystroke through one API call. The canonical demo of why a System One model is not a chat model."),
 ("Jev Classifier", "https://jevclassifier.vercel.app", "classifier",
  "Paste JSON, define the run, classify. Shows the shape most production Jev code takes: one request carrying many questions, every answer a probability."),
 ("SemanticSpace", "https://semanticspace.dev", "semantic",
  "Places phrases in 2D by asking Jev how strongly each relates to two chosen axis concepts, then using the scores as coordinates. Scores as geometry."),
 ("Crowdcheck", "https://crowdcheck-ai.vercel.app", "crowdcheck",
  "Tests a post against 10,000 simulated readers with their own jobs, tastes and memories, each reacting through typed decisions rather than generated text."),
 ("blink.review", "https://blink.review", "blink",
  "Code review that runs every time an agent edits a file — Jev checks the diff in place of an LLM reviewer, fast enough to sit inside the edit loop."),
 ("Hollow Creek", "https://hollow-creek-sigma.vercel.app", "hollow",
  "A village where every NPC decides for themselves how to react to you, and remembers. Typed decisions as game AI, no dialogue tree."),
 ("Tetris", "https://jev-omega.vercel.app", "tetris",
  "Play it yourself, or hand the board to the TypeSafe `Choice` primitive and let it pick every move."),
 ("Rustline — Duel Jev", "https://jev-arcade.vercel.app/duel", "rustline",
  "A 3D arena shooter where the opponent is a Jev decision loop running at four difficulty presets."),
 ("Game Plan", "https://game-plan.adriaansendennis.workers.dev/play", "gameplan",
  "Word-association puzzle where Jev judges whether your link between two concepts actually holds."),
 ("Yes / No", "https://yesno.coderai.dev", "yesno",
  "The smallest possible product built on a System One model: one `Boolean` question, two possibilities."),
 ("Made with Jev", "https://madewithjev.com", "madewith",
  "The largest community directory of Jev builds (295 builds / 91 guides at time of capture) — a primary source for this list."),
]

def anchor(t):
    a = t.lower()
    for ch in "&/,.:()": a = a.replace(ch, "")
    return "-".join(a.split())

def flags(e):
    f = []
    if e["link_status"] == "dead": f.append("🔗")
    elif e["evidence"] in ("none", "mentions") and e["repo"]: f.append("❔")
    if e["lists"] >= 7: f.append("⭐")
    return (" " + "".join(f)) if f else ""

def line(e):
    s = f"- [{e['name']}]({e['url']}) — {e['desc']}"
    for label, url in e.get("extra_links", []):
        s += f" ([{label}]({url}))"
    return s + flags(e)

def main():
    by = collections.defaultdict(list)
    for e in E: by[e["category"]].append(e)
    for k in by: by[k].sort(key=lambda e: (-e["lists"], e["name"].lower()))

    audit_badge = META["audited"].replace("-", "--")
    n = len(E)
    ok = sum(1 for e in E if e["link_status"] == "ok")
    dead = [e for e in E if e["link_status"] == "dead"]
    noev = [e for e in E if e["repo"] and e["evidence"] in ("none", "mentions")]
    o: list[str] = []
    w = o.append

    w("# awesome-jev")
    w("")
    w("<!-- Generated by build_readme.py from entries.json. Edit the data, then rebuild. -->")
    w("")
    w(f"[![entries](https://img.shields.io/badge/entries-{n}-111111?style=flat-square)](#full-list) "
      f"[![links checked](https://img.shields.io/badge/links%20checked-{ok}%20live%20%2F%20{len(dead)}%20dead-2ea043?style=flat-square)](#link-audit) "
      f"[![screenshots](https://img.shields.io/badge/screenshots-{len(GALLERY)}-8957e5?style=flat-square)](#what-people-actually-built) "
      f"[![last audit](https://img.shields.io/badge/last%20audit-{audit_badge}-0969da?style=flat-square)](#how-this-list-is-verified)")
    w("")
    w("A curated list of everything public that is built on **[Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev)**, "
      "TypeSafe AI's System One model for typed decisions.")
    w("")
    w("Jev is not a chat model. You hand it unstructured state plus a **typed question**, and it hands back a "
      "**typed answer with a calibrated probability** — a choice, a score, or a boolean. No tokens to parse, no schema to repair. "
      "That makes it a decision layer you can put inside ordinary code: routing, classification, rubric scoring, verification, agent guardrails.")
    w("")
    w(f'<img src="{SHOTS["hero"]}" alt="typesafe.ai — The first (public) System One model" width="100%">')
    w("")
    w("<table><tr>")
    w(f'<td width="50%"><img src="{SHOTS["bench"]}" alt="Cost and speed comparison on typesafe.ai" width="100%"><br>'
      "<sub>TypeSafe's own cost/speed comparison against chat models.</sub></td>")
    w(f'<td width="50%"><img src="{SHOTS["docs"]}" alt="Jev quick start documentation" width="100%"><br>'
      "<sub>The three primitives: <code>Choice</code>, <code>Score</code>, <code>Noul</code>.</sub></td>")
    w("</tr></table>")
    w("")
    w("---")
    w("")

    # --- why this one ---
    w("## Why another awesome-jev")
    w("")
    w("Jev launched into a wave of list-building: at the time of writing there are at least "
      f"{META['source_lists']} public *awesome-jev* style lists, and they overlap heavily without agreeing. "
      "They are also unaudited — entries are added once and never re-checked.")
    w("")
    w("This list is the union of all of them, plus verification work none of them do:")
    w("")
    w("| | Typical awesome-jev list | This list |")
    w("| --- | --- | --- |")
    w(f"| Entries | 72–668 | **{n}** (deduplicated union) |")
    w(f"| Links checked | no | **yes** — {ok} live, {len(dead)} dead at last audit |")
    w("| Jev usage verified | no | **yes** — every repo's README fetched and checked for a real Jev reference |")
    w("| Cross-list agreement shown | no | **yes** — how many independent lists carry each entry |")
    w(f"| Screenshots | none | **{len(GALLERY)}**, captured live |")
    w("| Machine-readable data | rarely | [`entries.json`](entries.json) |")
    w("")
    w("Everything here is built on the work of the lists in [Other Jev Lists](#other-jev-lists). "
      "This is a merge and an audit of their collective work, not a replacement for it.")
    w("")

    # --- gallery ---
    w("## What people actually built")
    w("")
    w("Screenshots below were captured live from the running projects. "
      "They are here because a one-line description does not tell you what a typed decision *looks like* — the probability panels do.")
    w("")
    for i in range(0, len(GALLERY), 2):
        pair = GALLERY[i:i + 2]
        w("<table><tr>")
        for title, url, key, cap in pair:
            w(f'<td width="50%" valign="top"><a href="{url}"><img src="{SHOTS[key]}" alt="{title}" width="100%"></a><br>'
              f"<b>{title}</b><br><sub>{cap}</sub></td>")
        if len(pair) == 1: w('<td width="50%"></td>')
        w("</tr></table>")
        w("")

    # --- legend / method ---
    w("## How this list is verified")
    w("")
    w(f"Last audit: **{META['audited']}**. For every GitHub entry the audit fetches the repository's README directly and records:")
    w("")
    w("- **Link status** — does the repository still resolve, or has it been deleted or made private.")
    w("- **Jev evidence** — does the README name Jev / TypeSafe, reference `api.typesafe.ai`, or show a System One call. "
      "A repo can use Jev deep in its code and say nothing in its README, so a missing marker means *unevidenced*, not *false*.")
    w("- **Cross-list agreement** — how many of the independent source lists carry the entry. "
      "One list carrying something is a lead; seven carrying it is a signal.")
    w("")
    w("Markers used below:")
    w("")
    w("| Marker | Meaning |")
    w("| --- | --- |")
    w("| ⭐ | Carried by 7 or more independent lists |")
    w("| ❔ | Repository is live, but its README shows no Jev reference — treat as unverified |")
    w("| 🔗 | Link was dead at the last audit |")
    w("")
    w("> [!WARNING]")
    w("> **A listing is not an endorsement.** This audit checks that a link resolves and that a project says it uses Jev. "
      "It does not review code quality, security, licensing, or whether the project runs at all.")
    w(">")
    w("> Jev shipped with a large same-day wave of small repositories, many sharing one scaffold and one or two commits. "
      "Such projects can be entirely legitimate — they are simply **unproven**. Before adopting anything here, check that the code "
      "actually calls the API, that some runnable check exists, that published numbers trace to a source, and that a license is present.")
    w("")

    # --- coverage ---
    w("## Coverage")
    w("")
    for k, t in CATS:
        c = len(by.get(k, []))
        if c: w(f"- [{t}](#{anchor(t)}) — {c}")
    w("")
    w("## Full list")
    w("")
    for k, t in CATS:
        items = by.get(k, [])
        if not items: continue
        w(f"### {t}")
        w("")
        for e in items: w(line(e))
        w("")

    # --- audit appendix ---
    w("## Link audit")
    w("")
    w(f"{len(dead)} entries carried by the source lists no longer resolve. They are kept here, marked 🔗, "
      "so the same dead links do not get re-added by the next list that copies from these:")
    w("")
    for e in sorted(dead, key=lambda x: x["name"].lower()):
        w(f"- ~~[{e['name']}]({e['url']})~~ — carried by {e['lists']} list(s)")
    w("")
    w(f"A further **{len(noev)}** repositories are live but show no Jev reference in their README (marked ❔). "
      "Several are substantial projects that call Jev from code without documenting it, so this is a flag for review, not a removal list.")
    w("")

    # --- sources ---
    w("## Sources")
    w("")
    w("Entries were merged from these public lists, each fetched and parsed in full:")
    w("")
    for s in META["source_list_urls"]: w(f"- {s}")
    w("")
    w("## Contributing")
    w("")
    w("Edit [`entries.json`](entries.json) and run `python3 build_readme.py`. Never edit `README.md` by hand — it is generated.")
    w("")
    w("One entry, one category, one sentence. **Removals are as welcome as additions** — if an entry is dead, "
      "mis-attributed, or does not actually use Jev, open a PR that deletes it. See [CONTRIBUTING.md](CONTRIBUTING.md).")
    w("")
    w("## License")
    w("")
    w("[CC0-1.0](LICENSE) for the list content. Linked projects carry their own licenses.")
    w("")
    (ROOT / "README.md").write_text("\n".join(o))
    print(f"README.md written: {len(o)} lines, {n} entries, {len(GALLERY)} screenshots")

if __name__ == "__main__":
    main()
