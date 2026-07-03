---
name: ucsd-memory
description: Use and maintain an existing local TritonAI memory vault. Trigger on $memory, remember this, forget this, search memory, what do we know about, summarize this into memory, memory status, or requests to add, update, remove, query, or cite Obsidian-style TritonAI memory notes.
---

# UCSD Memory

<!-- Methodology provenance: local-first agent memory pattern from TritonAI/Codex usage, plus David Allen GTD capture/review discipline for capture, clarification, and review. -->

Use this skill for day-to-day memory operations after `ucsd-memory-create` has created the vault.

## Locate the Vault

1. Prefer the configured memory root from `.memory/config.json` if the user gives a path.
2. Otherwise check:
   - `~/.agents/ucsd/data/memory`
   - `%USERPROFILE%\.agents\ucsd\data\memory`
3. If no vault exists, use or recommend `ucsd-memory-create` instead of inventing a new structure.
4. Read the vault `AGENTS.md` before editing memory files.

## Operate on Markdown Directly

No wrapper command is required. Inspect and edit the vault's Markdown files directly using the rules below, after reading `AGENTS.md` and `.memory/config.json`.

## Operations

### Remember

Use when the user says to remember, save, capture, add to memory, or keep something for later.

1. Identify the right scope: person, project, meeting, conversation, preference, workflow, or inbox.
2. Preserve provenance: source, timestamp, who requested it, and confidence.
3. Write durable facts to the most specific note. Use `inbox.md` for uncertain or unsorted memory.
4. Use YAML frontmatter when creating a new note:

```yaml
---
title: Example
type: project
created: 2026-06-18
updated: 2026-06-18
sources:
  - kind: conversation
    path: current-thread
confidence: medium
---
```

5. Add `[[wikilinks]]` to related people, projects, meetings, and source notes.
6. Keep the user-facing response short and mention the file changed.

### Search or Answer

Use when the user asks what memory knows, asks about prior work, or asks for a memory-backed answer.

1. Search filenames, headings, wikilinks, and content.
2. Prefer specific source-backed notes over broad summaries.
3. Separate confirmed memory from inference.
4. Cite the memory note paths or names used.
5. If memory is stale or ambiguous, say so and offer the narrow next lookup.

### Forget or Remove

Use when the user asks to forget, delete, remove, redact, or correct a memory.

1. Confirm the target if the request could match multiple notes.
2. Prefer surgical edits or redaction over deleting whole notes.
3. Preserve a minimal audit line in `.memory/logs/` unless the user asks for privacy deletion.
4. For privacy deletion, remove the sensitive content and do not preserve the sensitive text in logs.
5. Never remove scheduler config or source files unrelated to the requested memory.

### Summarize into Memory

Use when the user asks to save a conversation, summarize a thread, or make the current work durable.

1. Extract durable facts, decisions, preferences, open loops, and commands.
2. Put raw or near-raw context under `sources/conversations/` only when appropriate.
3. Update project/person/summary notes with concise source-backed bullets.
4. Add unresolved items to `inbox.md` with a `Done means:` or `Follow-up:` line when helpful.

### Status

Use when the user asks whether memory is working.

Check:

- vault exists
- `AGENTS.md` exists
- `.memory/config.json` exists
- recent `.memory/logs/` entries
- daily and weekly schedule metadata if present
- enabled sources

Report missing pieces and point setup gaps to `ucsd-memory-create`.

## Guardrails

- Do not ingest email, calendar, Jira, Drive, or other external systems unless explicitly enabled in the vault config and requested by the user.
- Do not send email, update Jira, publish files, or make external writes while answering memory requests.
- Do not store API keys, tokens, passwords, private keys, session cookies, or unrelated secrets.
- Do not rewrite large areas of the graph for a small memory request.
- Do not claim memory is current unless you checked the relevant notes or logs in this turn.

## Sources & Currency

- This skill encodes a local operational workflow, not UCSD policy.
- Pair with `ucsd-memory-create` for vault initialization and scheduled background jobs.
