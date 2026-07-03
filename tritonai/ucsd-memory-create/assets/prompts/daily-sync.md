# Daily Memory Sync

Run inside the TritonAI memory vault.

## Objective

Collect newly available local conversation context, turn it into source-backed Markdown notes, and update the Obsidian-style graph without external side effects.

## Steps

1. Read `.memory/config.json` and `AGENTS.md`.
2. Inspect only enabled local sources. Do not connect to email, calendar, Jira, Drive, or other external systems unless the config explicitly enables that source and credentials/connectors are already available.
3. Import new or changed conversation material into `sources/conversations/` with source path, imported timestamp, and run id.
4. Extract durable items:
   - projects
   - people
   - decisions
   - open loops
   - preferences
   - reusable commands or workflows
5. Update notes using YAML frontmatter and `[[wikilinks]]`.
6. Append uncertain items to `inbox.md` instead of overfitting them into project or people notes.
7. Write a concise run report to `.memory/logs/daily-sync-YYYY-MM-DD.md`.

## Guardrails

- Do not store secrets, tokens, private keys, session cookies, or credential files.
- Do not send email, update Jira, publish files, or perform external writes.
- Preserve provenance. Every durable note created from a source should include enough context to trace back to the source.
- Prefer additive updates. Leave cleanup, merging, and deletion to the weekly cleanup job.
