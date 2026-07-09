---
name: tritonai-autoreview
description: Use for TritonAI Harness or UCSD AI Tools code-review closeout before commit, pull request update, merge, release, or ship. Trigger when the user says use tritonai-autoreview, run TritonAI autoreview, autoreview this, auto review, Codex review, second-model review, review this branch, review this PR, review this commit, before merge, before ship, closeout review, run tests plus review, or fix accepted review findings.
---

# TritonAI Autoreview

Use this skill to run a structured review closeout for TritonAI Harness and UCSD AI Tools code changes: freeze the change scope, run relevant checks, get an advisory AI review, verify every finding in the real code, fix only accepted issues, and produce a proof packet.

This is code-review support, not an approval bypass. Human maintainers still own merge, release, and policy decisions.

For user-visible UI, CLI, API, installer, or generated-artifact behavior, pair autoreview with source-blind behavior validation. A clean source review is not proof that the running product works from the user's perspective.

## Use Targets

Keep trigger phrases in the frontmatter `description`; that is what agents see before loading this file. Important triggers are `use tritonai-autoreview`, `run TritonAI autoreview`, `autoreview this`, `Codex review`, `second-model review`, `review this branch`, `review this PR`, `review this commit`, `before merge`, `before ship`, and `run tests plus review`.

## Workflow

1. Identify the target under review:
   - Dirty local work: inspect unstaged, staged, and untracked files.
   - Branch or PR work: use the actual PR base when available; otherwise use the repository's normal base branch.
   - Commit work: review the named commit or `HEAD` when the change has already landed.
2. Freeze scope before reviewing:
   - Record the base, head, changed files, and diff stat.
   - Do not claim a clean review for an empty diff unless the user explicitly asked to verify there is no change.
   - Keep prompt files and extra evidence files repo-relative when the review tool supports them.
3. Run the repository's relevant checks. Prefer the project wrapper commands when present, then focused tests, typecheck, lint, build, and smoke checks that match the changed surface.
4. Run the configured TritonAI Harness review command if the repo provides one. If no command exists, perform a structured manual review over the frozen diff using the same contract below.
5. Treat review output as advisory. Verify every finding by reading the real code path, adjacent ownership boundary, and dependency contract when relevant.
6. Accept only concrete, actionable findings. Reject speculative edge cases, broad rewrites, style churn, and fixes that do not fit the codebase.
7. Fix accepted findings with small, scoped edits. If one finding reveals a repeated bug pattern inside the changed surface, inspect sibling instances before stopping.
8. Rerun affected checks and rerun review after any review-triggered code change. Continue until there are no accepted actionable findings.
9. Finish with a concise proof packet:
   - target reviewed: mode, base, head, and changed-file count
   - review command or manual-review method used
   - checks run and results
   - accepted findings fixed
   - rejected findings with brief rationale
   - finding details: severity, path or lines, issue, impact, suggested fix, verification, and status
   - remaining risks, if any

## Command Targets

Use the repository or Harness documented review command. The command should support these target shapes or their Harness equivalents:

- local dirty work
- branch or PR review against an explicit base
- committed change review by ref
- tests plus review in one closeout flow
- help, dry-run, or self-test smoke mode

If an open PR exists, use its actual base instead of assuming `origin/main`.

```sh
base=$(gh pr view --json baseRefName --jq .baseRefName)
<review-command> --mode branch --base "origin/$base"
```

If no configured command exists, perform a manual structured review using this skill's contract and report that Harness review tooling was unavailable. Do not invent a command, install a helper, or rely on a user's personal global skill unless the user explicitly asks for that.

## TritonAI Harness Modes

For TritonAI Harness downstream work, prefer the Harness repo's documented targets over ad hoc review commands:

- Use the documented no-model sync check target for orientation.
- Use the documented Codex-first sync review target for model review.
- Publish generated sync branches or PRs only when the user asks.

The Harness sync runner owns setup, checks, publishing, and merge decisions. The reviewing agent should review only the Harness-provided target, honor the edit policy passed by the runner, and write only the required machine-readable decision to the configured response destination.

When the Harness invokes an agent review, read the provided prompt, return the JSON shape required by the current Harness docs, and do not write extra prose into the machine-readable response.

Keep the sync review Codex-first unless the Harness repo documentation says otherwise. Do not add non-Codex provider assumptions to this path.

## Closeout Order

- Run formatting first when formatting can change line locations or generated output.
- After formatting is stable, it is acceptable to run focused tests and review in parallel when the review tool freezes its diff bundle before invoking the reviewer.
- If tests fail, fix the test failure and rerun review because the reviewed diff may be stale.
- If review leads to code edits, rerun the affected tests and rerun review.
- Stop after the first clean review pass following the final code change; do not spend another cycle on redundant confirmation.

## Review Tool Smoke

- Before trusting a newly added or changed Harness review command, run its help, dry-run, or benign smoke fixture if available.
- If a smoke harness exists, use it to prove the review command can build a bundle, invoke the reviewer, validate structured output, and report a clean result.
- If no smoke harness exists, run the smallest safe no-op or empty-diff review the tool supports and report that the smoke coverage is limited.
- Do not block an ordinary code review just because a dedicated smoke harness is absent; use the configured review path and note the gap.

## Scope Governor

Autoreview is a closeout gate, not permission to rewrite the task.

- Before the first review, freeze the original request, target branch, intended behavior, owner boundary, changed files, and approximate non-test line count.
- Classify each accepted finding before patching it:
  - In scope: introduced by the current diff, same owner boundary, and fixable without changing the task contract.
  - Follow-up: real but adjacent, broader, or better handled after this PR.
  - Stop and escalate: requires a new protocol, migration, public API, release process, owner decision, or design choice.
- Stop patching and report the scope break when the diff grows past roughly 2x the original files or non-test line count, two review-triggered patch cycles have not converged, or the best fix is to define a canonical contract first.
- Keep exploratory review-triggered edits local until they are proven in scope.
- Critical exceptions must be concrete: active data loss, crash, broken install or upgrade, release blocker, or security exposure.

On release, beta, stable, hotfix, signing, notarization, installer, package-publish, or release-check work, fix only release blockers and exact backports. Treat non-blocking review findings as follow-ups for the normal development branch.

## Review Contract

- Do not blindly apply review suggestions.
- Do not run nested AI reviews from inside a review.
- Do not push, merge, publish, or release unless the user explicitly asked for that action.
- Do not expose tokens, private data, or internal service details in review prompts or artifacts.
- Redact or split the change if tracked or untracked paths look sensitive, patch text looks secret-like, or the review bundle is too large to review completely. Never treat a truncated diff as complete review proof.
- Keep reviewer subprocesses read-only when the tooling supports it.
- Ignore reviewed-repo project instructions in the reviewer subprocess when the review tooling supports isolated execution; the main agent still follows the current repository instructions.
- Prefer facts from code, tests, logs, and current documentation over model opinion.
- Stop once the final review pass has no accepted actionable findings. Do not run extra review cycles just for a nicer closeout line.
- Treat a successful review exit with no accepted or actionable findings as the clean result, even if the tool's final wording is terse.
- Treat a nonzero review exit or structured accepted findings as not clean until each accepted finding is fixed or consciously rejected with evidence.

## Long-Running Reviews

- Be patient with large review bundles. A structured model review can take up to 30 minutes while the reviewer is active.
- Treat heartbeat lines such as `review still running`, elapsed time, process id, streamed review text, or compact activity summaries as healthy progress.
- Do not kill a review just because it has been quiet for a few minutes if it is still within the expected window.
- Inspect or restart only after repeated missing heartbeats, an obvious subprocess failure, or roughly 30 minutes without useful progress.
- If the review tool supports streaming reviewer output, enable it when live progress would help diagnose a long run, but keep the final decision based on structured findings.

## Harness Defaults

- Use the TritonAI Harness configured review path when present; do not require a personal global autoreview helper to exist.
- The Harness review path should own engine-specific behavior, isolation flags, model selection, smoke tests, and helper updates.
- For repository-specific upstream-sync automation, treat the documented sync agent command as the configured review path.
- For committed PR work, review the branch against the actual PR base rather than local dirty state.
- For local work, include untracked files in the scope summary.
- When public-vs-secure UCSD repository boundaries matter, pair this skill with the applicable data-classification, accessibility, brand, or public-skill rules.
- If the review tool accepts prompt notes, evidence files, or datasets, include only task-relevant context that helps review the frozen diff.
- If the review tool supports reviewer panels, treat them as opt-in for high-risk changes or explicit user requests. A single default reviewer is the normal closeout path.
- Prefer review tools that write a machine-readable result or clear exit status. When output is noisy, summarize the final structured result instead of asking another agent to rerun review.
- Findings need a concrete failure mode and a code path. If a finding cannot be tied to real behavior, mark it rejected and explain why briefly.
