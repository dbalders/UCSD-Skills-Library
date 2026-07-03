# Contributing to UCSD Skills Library

Thanks for helping improve the UCSD Skills Library. This repository is intentionally simple: it contains reusable agent skills, not a generated catalog, dashboard, installer, or internal deployment tooling.

## Repository Shape

Use this layout for skills:

```text
tritonai/
  skill-name/
    SKILL.md
    references/
    assets/
    scripts/

community/
  skill-name/
    SKILL.md
    references/
    assets/
    scripts/
```

Only `SKILL.md` is required. Add `references/`, `assets/`, or `scripts/` only when the skill genuinely needs them.

## Before You Add a Skill

- Check existing skills first and extend one when that is cleaner than adding a near-duplicate.
- Keep the skill focused on one job.
- Use lowercase, hyphenated folder names.
- Make the folder name match the `name:` field in `SKILL.md`.
- Community skills must include a `maintainer:` field in `SKILL.md` frontmatter naming the contributor, team, or organization responsible for the skill.
- Do not include internal UCSD credentials, private service details, customer data, secrets, or non-public operational runbooks.

## Agent Instructions

If you point an AI agent at this repository to create or edit a skill, give it these rules:

1. Read this file before editing.
2. Create or update one skill at a time.
3. Put TritonAI or UCSD AI Tools maintained skills under `tritonai/<skill-name>/`.
4. Put community contributed skills under `community/<skill-name>/` and include a `maintainer:` frontmatter field.
5. Do not create a top-level `skills/` folder in this public repo.
6. Do not add dashboard, catalog, installer, or deployment tooling unless the task explicitly asks for repository tooling.
7. Do not add per-skill `README.md`, installation guides, quick references, changelogs, or other auxiliary docs. Put agent-needed detail in `SKILL.md` or `references/`.
8. Keep long references in `references/`; keep `SKILL.md` focused on when to use the skill and how to run the workflow.
9. Use placeholders in examples. Do not invent realistic UCSD people, emails, IDs, tokens, hosts, or private service names.
10. Run the local checks documented below, or clearly say why they could not be run.

## Skill Frontmatter

Every `SKILL.md` must start with YAML frontmatter:

```yaml
---
name: example-skill
description: Use when an agent should do a specific workflow. Trigger on concrete user intents, keywords, file types, or slash commands.
---
```

The `description` is used by agents to decide when to load the skill. Include the concrete trigger contexts there, not in a separate "when to use" section that only appears after the skill is already loaded. Be specific and avoid broad wording that overlaps unrelated skills.

Community skills must also include a maintainer:

```yaml
---
name: example-skill
description: Use when an agent should do a specific workflow. Trigger on concrete user intents, keywords, file types, or slash commands.
maintainer: Contributor Name
---
```

Use a real person, team, or organization name for `maintainer:`. Do not put private phone numbers, personal addresses, tokens, or credentials in frontmatter.

Do not add arbitrary frontmatter fields. For this public repo, `maintainer:` is the only extra frontmatter field allowed, and only for community skills. Do not add `allowed-tools`, `catalog`, `tier`, `publicationStatus`, `agents/openai.yaml`, or generated-dashboard metadata unless this repository later adds tooling that requires it.

## Skill Content Rules

A good public skill should:

- State exactly when to use it.
- Prefer official or authoritative sources.
- Cite sources for policy, compliance, brand, accessibility, security, or technical-standard claims.
- Make approval gates explicit before sending messages, changing production systems, publishing content, or contacting external services.
- Keep commands copyable and scoped to the user's workspace.
- Avoid broad agent behavior changes unrelated to the skill's job.

Do not include instructions that tell an agent to ignore system, developer, repository, security, privacy, or approval requirements.

## Review Expectations

All contributions should be reviewed before merge. Review should check:

- The skill is safe to publish publicly.
- Instructions are clear, scoped, and actionable.
- Any policy, compliance, or technical claims cite authoritative sources.
- Scripts are minimal, readable, and do not hide network calls or shell behavior.
- The skill does not ask agents to bypass approvals, leak secrets, or mutate external systems without explicit user confirmation.

Skills that include scripts, external network calls, authentication flows, or security/compliance guidance need extra review.

## Local Checks

At minimum, inspect changed files before opening a pull request:

```sh
find tritonai community -name SKILL.md -print
git diff --check
```

If validation tooling is added later, document the real commands here and in `README.md`. The tooling should enforce the same public skill rules described in this file.

## Private or Internal Skills

Some skills do not belong in this public repository. Use the private secure library for skills that include internal platform details, deployment procedures, private infrastructure assumptions, restricted data workflows, or operational handoffs.
