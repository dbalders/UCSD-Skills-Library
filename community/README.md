# Community Skills

This folder is for skills contributed by the community.

Community skills should be safe to publish in the public UCSD Skills Library and reviewed before merge.

Each skill should live in its own folder:

```text
community/
  example-skill/
    SKILL.md
    references/
    assets/
    scripts/
```

Only `SKILL.md` is required. Add `references/`, `assets/`, or `scripts/` only when the skill genuinely needs them.

Do not add per-skill `README.md`, installation guides, quick references, changelogs, or other auxiliary docs. Community skills should be focused and source-backed when they encode policy or technical guidance.

Community skills must include a `maintainer:` field in `SKILL.md` frontmatter:

```yaml
---
name: example-skill
description: Use when this skill should be loaded.
maintainer: Contributor Name
---
```
