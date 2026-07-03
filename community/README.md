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

Only `SKILL.md` is required. Community skills should be focused and source-backed when they encode policy or technical guidance.

Community skills must include a `maintainer:` field in `SKILL.md` frontmatter:

```yaml
---
name: example-skill
description: Use when this skill should be loaded.
maintainer: Contributor Name
---
```
