# AGENTS

Instructions for AI agents working in this public UCSD Skills Library.

## Read First

- Read `README.md` and `CONTRIBUTING.md` before creating or editing skills.
- Follow the public repository shape in `CONTRIBUTING.md`.
- Prefer small, reviewable changes.

## Repository Shape

- Put TritonAI or UCSD AI Tools maintained skills under `tritonai/<skill-name>/`.
- Put community contributed skills under `community/<skill-name>/`.
- Every skill folder must include `SKILL.md`.
- Optional skill resources belong inside that skill folder as `references/`, `assets/`, or `scripts/`.
- Do not create a top-level `skills/` folder in this public repository.

## Skill Rules

- Create or edit one skill at a time unless the user explicitly asks for a broader migration.
- Keep each skill focused on one workflow.
- Use lowercase, hyphenated skill folder names.
- Make the folder name match the `name:` field in `SKILL.md`.
- Write a specific `description:` trigger in `SKILL.md` frontmatter.
- For community skills, include a `maintainer:` frontmatter field naming the contributor, team, or organization responsible for the skill.
- Keep long policy excerpts, examples, and reference material in `references/` instead of overloading `SKILL.md`.
- Do not add arbitrary frontmatter fields. For this public repo, `maintainer:` is the only extra field, and only for community skills.
- Do not add `agents/openai.yaml` unless this repository later adds tooling that consumes it.
- Do not add per-skill `README.md`, installation guides, quick references, changelogs, or other auxiliary docs.

## Public Boundary

This is the public library. Do not add:

- Secrets, tokens, API keys, credentials, private certificates, or real account IDs.
- Real student, patient, employee, customer, or operational data.
- Private UCSD infrastructure details, deployment procedures, or internal-only runbooks.
- Skills that assume restricted access to internal systems unless the public instructions are safe without that access.
- Instructions that tell an agent to bypass approval, security, privacy, or repository rules.

Internal or restricted skills belong in `UCSD-Skills-Library-Secure`, not here.

## Tooling Boundary

- Do not add dashboard, generated catalog, installer, publishing, or deployment tooling unless the user explicitly asks for repository tooling.
- If tooling is added later, keep it lightweight and document the commands in `README.md` and `CONTRIBUTING.md`.
- Do not add `catalog`, `tier`, `publicationStatus`, or generated-dashboard metadata to skills unless the repo tooling requires it.

## Checks

Before finishing, run the most relevant available checks. For documentation-only changes, at least read back the edited files and check for obvious formatting issues.

If this repo adds validation tooling later, document the commands in `README.md` and `CONTRIBUTING.md` before expecting agents or contributors to run them.
