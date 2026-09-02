# Documentation & record-keeping rules

*Why this exists: the work is thorough but was spread across ~30 docs with no single current
index and a stale top-level handoff, so fresh sessions re-derived settled results. These rules
stop that. They are binding on every session, human or AI.*

## The three rules that matter most

1. **`docs/STATE.md` is the single source of truth for STATUS.** Read it first, every session.
   Update it last, every session. If any other doc disagrees about what is done or open,
   STATE.md wins; the doc it points to wins for technical detail.
2. **Never silently supersede.** When a new result replaces an old one, do BOTH in the same
   session: (a) put a one-line banner at the TOP of the old doc/section — `> ⚠️ SUPERSEDED by
   <file/section>, <date>. Reason: …` — and (b) move the item between STATE.md's ledgers.
   Never delete the old reasoning; a reader who finds it later must see why it changed.
3. **Close and open questions explicitly.** Finishing something → move it from STATE.md §3
   (OPEN) to §1 (SETTLED) with a pointer to the doc that settled it. Starting a new thread →
   add it to §3 with an owner tag: `[runnable]`, `[needs-data]`, or `[external]`.

## How to document a new result

- Write it in a **dated results doc** (`docs/RESULTS_<topic>_<YYYY-MM-DD>.md`). Dated docs are
  append-only history — don't edit yesterday's numbers, supersede them (rule 2).
- Every quantitative claim must be **traceable**: name the script and the `runs/<file>.json`
  that produced it, so anyone can re-run it. A number with no reproducible source is not a result.
- Then update STATE.md's ledgers and doc map. That update is part of the task, not optional.

## Superseding specifics

- A **withdrawn/wrong** claim: record it in the paper's revision-history section (§10) AND leave
  a banner on the internal doc that made it. Never resurrect a withdrawn claim without new evidence
  and a note saying what changed.
- A **stale handoff/plan**: banner at top pointing to the current doc; keep for history.
- When two docs cover the same subject, the newer one names the older as superseded; don't leave
  the reader to guess which is live.

## Session-end checklist (do before you stop)

- [ ] STATE.md §0 status line current; §1/§3 ledgers reflect what changed this session.
- [ ] Any superseded doc/section carries a banner.
- [ ] New numbers point to a script + runs/ JSON.
- [ ] TECHNICAL_BIBLE.md updated if a durable technical fact changed (standing instruction).
- [ ] Commit with a message that says what changed (one logical change per commit where possible).

## Norms

- Intellectual honesty over hype. When cross-checking against another model (e.g. Grok), the job
  is to be the honest counterweight — verify claims against code and data before adopting them.
- One terminal command at a time when handing commands to Hassan (novice-friendly).
