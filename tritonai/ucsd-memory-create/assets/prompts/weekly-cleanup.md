# Weekly Memory Cleanup

Run inside the TritonAI memory vault.

## Objective

Consolidate the previous week's memory notes into a cleaner Obsidian graph while preserving provenance and user-authored content.

## Steps

1. Read `.memory/config.json`, `AGENTS.md`, and the previous seven days of `.memory/logs/`.
2. Review `inbox.md`, new `sources/`, and recently changed notes.
3. Merge duplicate project, people, meeting, and conversation notes when they clearly refer to the same entity.
4. Promote stable facts from `inbox.md` into the right note. Leave uncertain items in place with a short reason.
5. Add or repair `[[wikilinks]]` between people, projects, meetings, and decisions.
6. Create or update `summaries/weekly-YYYY-Www.md` with:
   - important projects
   - decisions
   - open loops
   - stale or low-confidence memories
   - suggested follow-up prompts
7. Write a concise run report to `.memory/logs/weekly-cleanup-YYYY-Www.md`.

## Guardrails

- Do not delete user-authored notes. Move stale generated notes to an archive section or record a proposed cleanup instead.
- Do not remove provenance fields.
- Do not ingest new external systems during cleanup.
- Do not send messages, create tickets, publish content, or make external writes.
