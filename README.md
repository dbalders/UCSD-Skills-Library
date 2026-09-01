# TritonAI Commons

TritonAI Commons is the public library of reusable agent skills for UC San Diego, TritonAI, and community workflows. The repository URL remains `https://github.com/dbalders/UCSD-Skills-Library` for compatibility with existing Harness installs and links.

Created and maintained by David Balderston for UC San Diego.

An agent skill is a folder of instructions, references, scripts, and assets that an AI coding agent can load when a task matches the skill's trigger description.

This repository is intentionally lightweight. Harness provides the publishing experience; this repository remains the reviewable source of truth rather than becoming a dashboard, installer, generated catalog, or internal platform runbook.

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
      LICENSE
      references/
      assets/
      scripts/

  community/
    README.md
    skill-name/
      SKILL.md
      LICENSE
      references/
      assets/
      scripts/
```

- `tritonai/` is for skills maintained by the TritonAI or UCSD AI Tools team. Only authors on the private AI team allowlist may contribute skills there.
- `community/` is for skills contributed by everyone else and reviewed before merge.
- Each skill lives in its own folder.
- Each skill must have a `SKILL.md` entrypoint and a `LICENSE` matching the
  repository MIT license.

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
  LICENSE
  references/
  assets/
  scripts/
```

## Publishing from TritonAI Harness

Create, install, and use a skill locally in Harness first. When it is ready to share, find it under **Settings → Skills → Your Skills** and select **Share with UCSD**.

Harness reads that existing local skill folder, validates its public copy, and submits it under `community/<skill-name>/`. Supporting text files are included. If the skill has no maintainer or matching license, the submitted copy names the signed-in GitHub user and includes the repository MIT license without changing local files. A conflicting local license must be resolved before submission.

Harness uses the connected GitHub integration to handle a fork, contribution branch, commits, and ready-for-review pull request. It never merges automatically, never overwrites an existing Commons skill, and does not expose or ask for a raw GitHub token. Campus approval is a later maintainer decision, not a contributor-selected submission scope.

The same submission is callable from Harness chat: ask to submit a named local skill to UCSD, then approve the public write. If GitHub is not connected, Harness explains the fork and public pull-request flow and directs you through **Settings → Plugins → GitHub** to sign in or create an account before retrying.

## Skill Format

Every `SKILL.md` starts with YAML frontmatter:

```yaml
---
name: example-skill
description: Use when an agent should do a specific workflow. Trigger on concrete user intents, keywords, file types, or slash commands.
---
```

The frontmatter `description` should explain when the skill should be used. Keep it concrete so agents do not load the skill for unrelated work.

Keep frontmatter minimal. Community skills must include a `maintainer:` field naming the contributor, team, or organization responsible for the skill. Standard agent-supported metadata such as `allowed-tools` may be retained; generated catalog or storefront metadata is not accepted.

## Public Boundary

This public repository should only contain skills that are safe to publish openly.

Do not add:

- Secrets, tokens, API keys, private certificates, or credentials.
- Private UCSD infrastructure details or deployment procedures.
- Real student, patient, employee, customer, or operational data.
- Internal-only runbooks, escalation paths, or restricted service assumptions.
- Skills that send email, write to production systems, or use authentication without clear user confirmation and review.

Internal or restricted skills belong in the private `UCSD-Skills-Library-Secure` repository instead.

## PR Review Automation

Pull requests are reviewed through three complementary layers:

- GitHub Actions runs lightweight preflight checks for contributor placement,
  public-skill format, obvious leak patterns, and whitespace.
  To avoid exposing private membership, public checks report maintainer
  verification for `tritonai/` changes without failing just because the private
  allowlist is unavailable.
- CodeRabbit is configured by `.coderabbit.yaml` for AI review on each PR update,
  with emphasis on public-vs-secure repository fit.
- The local Codex webhook reviewer in `docs/public-pr-review-service.md` runs
  through the Codex app server and posts public-skills review comments for each
  newly reviewed PR head SHA and issue update.

## Contributing

Contributions are welcome through Harness sharing or ordinary pull requests. See `CONTRIBUTING.md` for the expected skill layout, review rules, and public/private boundary.

## License

This repository is available under the MIT License. See `LICENSE`. Each
individual skill folder also includes the license so it remains available when
that skill is copied or distributed on its own. Community contributors remain
credited through skill maintainer metadata and Git history.
