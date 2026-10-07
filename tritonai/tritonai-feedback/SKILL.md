---
name: tritonai-feedback
description: Gather diagnostics for TritonAI feedback, bug reports, support requests, improvement ideas, or agent-experience notes, then prepare a GitHub issue for users with a GitHub account or an email for users without one. Trigger on /tritonai, /feedback, /feed-back, /feed back, TritonAI feedback, email TritonAI, report this to TritonAI, or send this to tritonai@ucsd.edu.
---

# TritonAI Feedback

Turn the user's feedback into an actionable report backed by diagnostics the agent can gather. Prefer a GitHub issue when the user has a GitHub account. Use email to `tritonai@ucsd.edu` only when the user has no GitHub account, unless they explicitly request email.

In Harness Codex threads, a leading `/feedback` is currently intercepted by native provider feedback before this skill receives it. Use `/tritonai` or `$tritonai-feedback` to invoke this workflow there. Do not submit native provider feedback as a substitute for a TritonAI report.

## Gather the Report

Use the current message and relevant conversation as the initial report. Inspect available tools, workspace metadata, app diagnostics, and logs before asking the user for information the agent can discover. Ask concise questions for missing essentials: what happened, expected behavior, reproduction steps, approximate time, frequency, and impact. For an improvement idea, capture the workflow pain point and desired outcome.

Gather what is relevant and available:

- TritonAI app version/build, release channel, and agent/tool version.
- OS/version, architecture, and relevant browser or device details.
- Provider/model and relevant non-secret settings.
- Workspace/repository, branch, commit, and working-tree status when relevant.
- Timestamp with timezone, exact error text, commands, stack traces, and tool failures.
- Relevant app/server, provider, terminal, and crash logs for the affected session and time window; screenshots or recordings when they help explain the problem.
- Troubleshooting already attempted, observed results, and any safe reproduction the user authorized.

Discover the running app's diagnostic/log location from its tools or configuration; do not assume a development checkout represents the installed app. Collect read-only evidence without changing settings, installing dependencies, restarting services, or rerunning destructive operations. Keep collection scoped to the reported problem. Do not sweep unrelated sessions, the home directory, credential stores, environment dumps, or complete conversation databases.

Record sources and the covered time window. Distinguish observed facts, user reports, and hypotheses. Mark unavailable diagnostics and collection errors explicitly; do not invent missing details or keep asking indefinitely. For a simple suggestion, avoid collecting unrelated technical logs.

## Prepare Safe Diagnostics

Create a report and sanitized diagnostic files in a temporary directory outside the repository. Keep originals unchanged. Review text, attachments, screenshots, filenames, and metadata for secrets and unrelated private content before including them. Remove credentials, authorization headers, cookies, tokens, passwords, private keys, and connection strings. Replace identifying usernames and private paths with consistent placeholders when unnecessary to reproduce the issue. Exclude student, patient, employee, customer, and unrelated operational data.

Include concise relevant excerpts in the report and all collected, relevant, sanitized logs as attachments where supported. List every included file, its source/time window, and redactions, omissions, or truncation. If a payload limit requires splitting or reducing logs, disclose it and preserve the sanitized files for the user. Never silently discard diagnostics or upload them to a separate file-sharing service.

For a file handoff, use a runtime-supported downloadable attachment or a user-approved destination and verify that the user can retrieve the files. A path on a remote agent's filesystem alone is not a completed handoff. If file delivery is unavailable, provide the usable sanitized content directly where it fits and identify anything still inaccessible. Preserve files while delivery or handoff is incomplete. After verified delivery or confirmed handoff, remove only task-created temporary copies that are no longer needed; retain copies the user requests and never delete original logs.

## Choose the Delivery Route

- Check the available GitHub integration or CLI's authenticated login without printing credentials. Authentication establishes tool access, not that the login belongs to the user; a shared or service account must not be treated as the user's account. Establish whether the user has a GitHub account and which posting identity they authorize from the request or known account context; ask if either is unclear.
- An absent CLI, expired login, missing repository permission, or failed API request does **not** mean the user has no account. Offer the supported sign-in flow or a prepared GitHub issue draft; do not switch to email automatically.
- If the user has no GitHub account, prepare the email fallback. Do not require them to create an account.

### GitHub Issue

Create issues in [`dbalders/TritonAI-Harness`](https://github.com/dbalders/TritonAI-Harness/issues). Use this explicit destination even when the current workspace belongs to another repository; do not route to the skills library or the upstream project's tracker.

1. Explain the named GitHub destination, then perform the relevant read-only checks authorized by the feedback request: read issue guidance/template, confirm issues are enabled, check visibility, and search for an existing issue using sanitized, non-sensitive terms. Do not include private logs or identifying workspace details in search queries. If a matching issue exists, show its link and propose adding the new evidence there instead of creating a duplicate; obtain confirmation for that comment too.
2. Prepare a specific title and a body using the report shape below, adapted to the issue template. Public issues require diagnostics suitable for public disclosure. If essential details cannot be shared safely, prepare a sanitized issue and identify withheld evidence for the user; do not publish private details or silently reroute to email.
3. Show the exact repository, authenticated posting login, title, body, visibility, and sanitized attachment manifest/content to the user. Create the issue only after they confirm this report, destination, and posting identity. `/feedback` alone starts collection and drafting; it does not authorize publication. Reconfirm if the posting identity changes.
4. Use the available GitHub tool or CLI with the user's authenticated account. Pass multiline bodies as structured tool arguments or a body file. Attach sanitized files only if the tool supports it; otherwise include the sanitized logs in collapsible body sections when they fit. Retain files that cannot be included locally, state which were not uploaded, and provide an attachment handoff for the user. Resolve payload limitations in the draft before confirmation.
5. Read back the resulting issue and return its URL. If creation times out or the result is uncertain, check for the created issue before retrying to avoid duplicates. Report failures accurately.

### Email Fallback

Prepare an email to `tritonai@ucsd.edu` with subject `TritonAI feedback: <short issue or request>`. Use the same diagnostic report as the body, with all collected, relevant, sanitized logs attached where supported. If attachments are unavailable, include the sanitized logs in the body when they fit; otherwise provide the complete sanitized files and a ready-to-send draft, identifying the manual attachment step.

Default to the user's UCSD Microsoft 365/Outlook mailbox. Use this delivery order:

1. **Office plugin first.** Discover the available Microsoft 365 mail tools and connected account. Prefer the Harness Office plugin. Its current `microsoft365.mail.draft.create` tool creates an **unsent** Outlook draft with file attachments and can return a `webLink`; it does not send mail. After the user confirms draft creation, include the reviewed report and sanitized logs, retain the draft ID/link, and open that draft in Outlook on the web to complete delivery. If a future plugin exposes an actual send tool, use it only when its capability is enabled and the user has confirmed sending the report. See the [Office plugin's documented capabilities](https://github.com/dbalders/TritonAI-Plugins/tree/main/plugins/microsoft-365).
2. **Outlook on the web.** If the plugin is unavailable, disconnected, or fails, open [Outlook on the web](https://outlook.office.com/mail/) using the runtime's preferred browser tools. Verify the active UCSD/work account. Reuse the existing approved draft when one was created. Otherwise, obtain approval of the sender, recipient, reviewed report, and attachments before composing or entering them in the mailbox: Outlook can autosave them as an external draft. Then compose and attach through supported UI controls. Resolve sign-in through the normal user flow. Never assume opening a page or a `mailto:` link has populated the message or attached the logs. Draft approval does not authorize sending.
3. **Desktop Outlook.** If the web route is unavailable, use an installed Outlook app signed in to the same mailbox. Reuse the approved draft. Before creating a new draft or entering report content, obtain approval of its sender, recipient, reviewed report, and attachments; this writes to the mailbox even before sending. Verify the actual sender, recipient, body, and attachments in the UI. Draft approval does not authorize sending.
4. **Manual handoff.** If neither Outlook surface can be operated, provide the complete draft and sanitized files with concise send instructions. State that the report has not been sent. Do not switch to Gmail or another personal mailbox unless the user explicitly requests that sender.

Show the exact sender account, recipient, subject, body, and sanitized attachment manifest/content and obtain approval before creating an external draft through any route. Draft creation and sending are separate actions; never claim an unsent draft was delivered. Obtain confirmation for sending the concrete report. Carry each granted authorization across transport fallback without asking again solely because the tool changed; draft approval alone remains insufficient to send. If the sender or report changes, show the change and obtain approval for the changed draft or send action.

Before sending through any route, verify that all intended attachments are present or disclose missing files. If draft creation or sending has an uncertain result, check Drafts/Sent Items for the same recipient, subject, and recent timestamp before retrying or switching routes. Prefer reusing one draft to creating duplicates. Verify sending through a tool receipt or the matching Sent Items message, and report the actual sender and transport used; do not claim recipient receipt without evidence.

## Report Shape

```text
Summary: <problem or request and impact>

Steps to reproduce:
1. <step, if known>

Expected: <desired behavior>
Observed: <actual behavior and exact error>
Frequency and time: <frequency; timestamp with timezone>

Environment:
- App version/build/channel:
- Agent/tool and version:
- OS/architecture:
- Provider/model:
- Relevant workspace/branch/commit:

Troubleshooting: <attempts and results>
Evidence: <sanitized log excerpts and useful screenshots>
Diagnostics: <file manifest, sources, time window, redactions/omissions>
Missing information: <unavailable diagnostics or unanswered essentials>
```

Omit irrelevant fields. Keep the summary concise while preserving the diagnostic evidence needed to act on the report.
