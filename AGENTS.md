# Agents.md

## 1) Agent Protocol
- Files: repo or `~/Desktop/Coding/agenticPrograms/agent-scripts`

## 2) Work Style
- Goal: min tokens, max signal.
- Voice: direct, terse, no filler.
- Prefer noun phrases over full prose.
- Prefer known abbrevs when clear: `ctx`, `req`, `impl`, `tests`, `wip`, `deps`.
- Avoid polite/formal padding (`please`, long intros, apologies unless needed).
- Output format: short bullets, flat lists, actionable items first.

## 3) Read-When Hints (Context Discovery)
- Before coding, run:`list-docs.py` script
- Parse listing results.
- If task intent matches `read_when` hints, open that markdown before editing code.
- If no hint match, skip doc body and continue.

## 4) Safety Guardrails (Trash Rule)
- Never use `rm -rf` for routine deletes.
- Use `trash` command instead (recoverable delete).
- For bulk/critical deletes:
  - preview targets first
  - confirm path scope
  - then `trash <targets>`

## 5) Conventional Commits + Small Files
- File size target: keep source files under `500` LOC.
- If file exceeds `500` LOC:
  - refactor by concern/module split
  - reformat for readability
  - keep behavior unchanged unless requested
- Commit message format (Conventional Commits):
  - `type(scope): summary`
  - Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `build`, `ci`, `perf`.
  - Examples:
    - `feat(parser): add read_when matcher`
    - `refactor(docs): split toc renderer`
