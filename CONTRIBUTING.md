# Contributing

This list is generated. **Do not edit `README.md`** — your change will be overwritten on the next build.

## Adding or changing an entry

1. Edit [`entries.json`](entries.json).
2. Run `python3 build_readme.py`.
3. Commit both files.

An entry looks like this:

```json
{
 "name": "jev-guard",
 "url": "https://github.com/leepokai/jev-guard",
 "desc": "Agent security: prompt-injection and dangerous-action guard for Claude Code, Codex, Pi, and ACP agents, with Jev deciding what to block",
 "category": "verification-guardrails",
 "repo": "leepokai/jev-guard",
 "lists": 5,
 "sources": ["yibie_awesome-jev", "cobanov_awesome-jev"],
 "link_status": "ok",
 "evidence": "strong",
 "primitives": ["boolean", "choice"],
 "extra_links": []
}
```

Leave `link_status`, `evidence` and `primitives` as `"unchecked"` / `[]` if you don't know them — `audit.py` fills them in.

## Inclusion criteria

- The source is public and citable.
- It **uses Jev** — or a documented Jev port, reproduction, or derivative — for a concrete typed decision. A generic classifier, router, or LLM-as-judge with no Jev involvement does not qualify.
- One sentence covering scenario, method, and value. No essays in the list.
- One entry, one category. When several fit, pick the one closest to the direct application domain.

Not included: pure opinion with no artifact, launch commentary with nothing running behind it, private or inaccessible sources, and anything too vague to classify.

## Removals are contributions

If an entry is dead, mis-attributed, duplicated, or does not actually use Jev, **open a PR that deletes it**. A removal PR is as welcome as an addition and will be merged on the same evidence standard.

## The pipeline

Four scripts, run in this order. A [GitHub Action](.github/workflows/audit.yml) runs all of them twice a day and commits only when the output changed, so in normal use you never run them by hand.

```bash
GITHUB_TOKEN=... python3 discover.py   # search GitHub for Jev projects not yet listed
python3 audit.py                       # re-check every link and Jev reference
python3 normalize.py                   # merge duplicate URLs, disambiguate clashing names
python3 build_readme.py                # regenerate README.md
```

- **`discover.py`** needs a GitHub token because it uses the search API. Everything it finds lands in the `unreviewed` category, never in a curated one.
- **`audit.py`** needs no token at all — it reads `raw.githubusercontent.com` directly. A repository is only marked dead when GitHub answers cleanly that nothing is there; a network failure leaves the previous status alone, so a flaky run cannot bury a live project.
- **`normalize.py`** is safe to re-run; it is idempotent.
- **`build_readme.py`** is the only thing that writes `README.md`.

## Promoting an unreviewed entry

Entries in **Recently Discovered (unreviewed)** are search hits, not curated entries. To promote one:

1. Check the repository actually calls the Jev API.
2. Write a real one-sentence description, replacing the auto-generated one.
3. Change its `category` to the right one and drop the `discovered` field.

If it does not belong, delete the entry. That is the more common outcome and it is a good contribution.

## AI-assisted submissions

AI-assisted work is fine. Bulk AI-generated submissions are not.

Jev shipped alongside a large wave of same-day repositories that share one scaffold, land in one or two commits, and ship more prose than code. Those can be legitimate — but if you are submitting several at once, say so in the PR, and say what each one actually does differently. Submissions that cannot answer "does the code call the API, and is there a runnable check" will be asked that question.

## Screenshots

Screenshots in the gallery are captured live from the running project, not taken from the project's own marketing. If you want a project featured with a screenshot, link something that runs.
