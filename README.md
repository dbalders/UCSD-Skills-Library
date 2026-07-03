# UCSD Skills Library

Public, reusable agent skills for UC San Diego and TritonAI workflows.

An agent skill is a folder of instructions, references, scripts, and assets that an AI coding agent can load when a task matches the skill's trigger description.

This repository is intentionally lightweight. It is a skills library, not a dashboard, installer, generated catalog, or internal platform runbook.

## Layout

```text
UCSD-Skills-Library/
  README.md
  AGENTS.md
  CONTRIBUTING.md
  LICENSE

  tritonai/
    README.md
    skill-name/
      SKILL.md
      references/
      assets/
      scripts/

  community/
    README.md
    skill-name/
      SKILL.md
      references/
      assets/
      scripts/
```

- `tritonai/` is for skills maintained by the TritonAI or UCSD AI Tools team.
- `community/` is for skills contributed by the community and reviewed before merge.
- Each skill lives in its own folder.
- Each skill must have a `SKILL.md` entrypoint.

## Installing a Skill

Copy the individual skill folder into the skills directory used by your agent. Do not copy the `tritonai/` or `community/` wrapper folder.

Common locations:

| Use case | Put skill folders here |
|---|---|
| Global dotagents skills | `~/.agents/skills/` |
| Citizen-Developer repo-local skills | `<Citizen-Developer repo>/.agents/skills/` |
| Managed TritonAI Harness install | `~/.agents/ucsd/skills/` |

For global dotagents-compatible setups:

```sh
mkdir -p ~/.agents/skills
cp -R tritonai/example-skill ~/.agents/skills/
```

For the Citizen-Developer workspace:

```sh
cd "/path/to/Citizen-Developer"
mkdir -p .agents/skills
cp -R "/path/to/UCSD-Skills-Library/tritonai/example-skill" .agents/skills/
```

For the managed TritonAI Harness install:

```sh
mkdir -p ~/.agents/ucsd/skills
cp -R tritonai/example-skill ~/.agents/ucsd/skills/
```

After copying, the installed skill should look like this:

```text
~/.agents/skills/example-skill/
  SKILL.md
  references/
  assets/
  scripts/
```

## Skill Format

Every `SKILL.md` starts with YAML frontmatter:

```yaml
---
name: example-skill
description: Use when an agent should do a specific workflow. Trigger on concrete user intents, keywords, file types, or slash commands.
---
```

The frontmatter `description` should explain when the skill should be used. Keep it concrete so agents do not load the skill for unrelated work.

Community skills must also include a `maintainer:` field naming the contributor, team, or organization responsible for the skill.

## Public Boundary

This public repository should only contain skills that are safe to publish openly.

Do not add:

- Secrets, tokens, API keys, private certificates, or credentials.
- Private UCSD infrastructure details or deployment procedures.
- Real student, patient, employee, customer, or operational data.
- Internal-only runbooks, escalation paths, or restricted service assumptions.
- Skills that send email, write to production systems, or use authentication without clear user confirmation and review.

Internal or restricted skills belong in the private `UCSD-Skills-Library-Secure` repository instead.

## Contributing

Contributions are welcome through pull requests. See `CONTRIBUTING.md` for the expected skill layout, review rules, and public/private boundary.

## License

This repository is available under the MIT License. See `LICENSE`.
