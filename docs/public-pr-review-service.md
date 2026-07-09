# Public PR and Issue Review Service

This repo includes a local GitHub webhook receiver that reviews public-skill PRs
and issues through the Codex app server. It posts a new GitHub comment for each
newly reviewed PR head SHA and each newly reviewed issue update.

The service is intentionally separate from GitHub Actions and CodeRabbit:

- GitHub Actions runs lightweight preflight checks.
- CodeRabbit gives broad AI review and inline comments when the GitHub App is enabled.
- This service gives a local Codex review focused on public-skill policy,
  whether a change belongs here or in `UCSD-Skills-Library-Secure`, and whether
  a new issue is safe/actionable enough for public maintainer triage.

## Architecture

```text
GitHub pull_request / issues webhook
  -> Cloudflare Tunnel hostname, or any HTTPS tunnel
  -> http://127.0.0.1:8787/github/webhook
  -> local Codex review worker
  -> Codex app-server JSONL client
  -> new PR or issue comment for each reviewed head SHA/update
```

The webhook handler verifies GitHub's `X-Hub-Signature-256`, returns `202 Accepted`
quickly, and performs the Codex review in a background worker.

## What It Reviews

For `pull_request` actions `opened`, `reopened`, `synchronize`, `ready_for_review`,
and `edited`, the service:

- Fetches the PR into an isolated git worktree under `.public-pr-reviewer/`.
- Runs trusted local checks for changed files, diff stat, whitespace, contributor
  placement, public-skill format, and high-confidence leak patterns.
- Asks Codex to review merge readiness against `README.md`, `CONTRIBUTING.md`,
  `AGENTS.md`, `.github/CODEOWNERS`, `.github/PULL_REQUEST_TEMPLATE.md`, and the
  PR diff.
- Posts a new comment marked with `<!-- ucsd-public-skills-codex-pr-review -->`.
- Records reviewed head SHAs in `.public-pr-reviewer/state.json` so the same commit
  is not reviewed twice unless `--force` is used.

For `issues` actions `opened`, `reopened`, and `edited`, the service:

- Ignores pull requests delivered through the Issues API.
- Reviews the issue body against public repository fit, public-boundary safety,
  missing reporter information, and likely next maintainer action.
- Posts a new comment marked with `<!-- ucsd-public-skills-codex-issue-review -->`.
- Records reviewed issue `updated_at` values in `.public-pr-reviewer/state.json`
  so the same issue update is not reviewed twice unless `--force` is used.

## Local Setup

Create a GitHub token that can read pull requests/contents and write PR comments.
For a fine-grained token, grant this repository:

- Contents: Read
- Pull requests: Read
- Issues: Read and Write
- Metadata: Read

Set secrets:

```sh
export PR_REVIEW_GITHUB_TOKEN="github_pat_..."
export PR_REVIEW_WEBHOOK_SECRET="$(openssl rand -hex 32)"
```

`GITHUB_TOKEN` or `GH_TOKEN` also work when `PR_REVIEW_GITHUB_TOKEN` is not set.

Run the webhook receiver:

```sh
python3 scripts/public_pr_review_service.py
```

Health check:

```sh
curl http://127.0.0.1:8787/healthz
```

Manual review without a webhook:

```sh
python3 scripts/public_pr_review_service.py --review-pr 12
```

Manual issue review:

```sh
python3 scripts/public_pr_review_service.py --review-issue 34
```

Dry-run manual review:

```sh
python3 scripts/public_pr_review_service.py --review-pr 12 --dry-run --force
```

## GitHub Webhook

In GitHub repository settings:

- Payload URL: `https://<your-tunnel-host>/github/webhook`
- Content type: `application/json`
- Secret: the value of `PR_REVIEW_WEBHOOK_SECRET`
- Events: choose **Pull requests** and **Issues**
- Active: enabled

Use the GitHub webhook redelivery button to replay a delivery after changing the
service.

## Codex App Server

The service talks to Codex through the app-server protocol. It does not call
`codex exec`, and it does not use `codex --remote`, because this Codex version
only supports `--remote` for interactive TUI/session commands.

The reviewer starts a short-lived stdio app-server process for each review:

```sh
export CODEX_REMOTE="stdio://"
```

Defaults:

```sh
CODEX_PATH=/Applications/Codex.app/Contents/Resources/codex
CODEX_REMOTE=stdio://
CODEX_MODEL=gpt-5.5
CODEX_REASONING_EFFORT=high
CODEX_TIMEOUT_SECONDS=3600
```

`unix://`, `ws://`, and `wss://` app-server endpoints are not supported by this
reviewer. The tested automation path is `codex app-server --stdio`.

## Notes

- Draft PRs are reviewed by default. Add `--skip-drafts` to ignore drafts.
- Use `--allow-unsigned` only for local webhook testing.
- The service posts a new comment for each newly reviewed head SHA. It does not
  update or replace older comments.
- The service posts a new issue-review comment for each newly reviewed issue
  update. It does not update labels, assignees, milestones, or issue state.
- Only authors on the private AI team allowlist may contribute to `tritonai/`.
  Other contributors should use `community/<skill-name>/` with `maintainer:`.
- The private allowlist is not committed to git. The local reviewer can read
  `.public-pr-reviewer/ai-team-allowlist.txt` to avoid blocking allowlisted
  authors on `tritonai/` changes, but public reviewer comments keep neutral
  wording and do not reveal membership. If the allowlist is missing or the
  author is not listed, `tritonai/` changes are reported as requiring maintainer
  verification.
- Local state and worktrees live under `.public-pr-reviewer/`, which is ignored by git.
- Token/secret-like environment variables are scrubbed before running Codex.
- The reviewer does not execute changed repository scripts.
