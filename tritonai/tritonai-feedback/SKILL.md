---
name: tritonai-feedback
description: Use when a user wants to send feedback, bug reports, support requests, improvement ideas, or agent-experience notes to the TritonAI team. Trigger on explicit requests such as /tritonai, /feedback, /feed-back, /feed back, TritonAI feedback, email TritonAI, report this to TritonAI, or send this to tritonai@ucsd.edu.
---

# TritonAI Feedback

Use this skill to turn coding-agent feedback into a concise email to `tritonai@ucsd.edu`.

## Workflow

1. Treat the user's current message as the initial feedback.
2. If the feedback is not clear enough to act on, ask only for the missing essentials:
   - what happened
   - what they expected
   - which coding agent or tool was involved
   - any relevant error text, command, file path, repo, model, or timestamp
3. Draft a short email with a specific subject and actionable body.
4. Show the exact subject and body to the user before sending.
5. Send only after the user confirms, because this is an external action.
6. If no email-sending tool is available, provide a ready-to-send draft or a `mailto:` link instead of pretending it was sent.

## Email Rules

- Always send to `tritonai@ucsd.edu`.
- Do not include API keys, tokens, passwords, private keys, or unrelated sensitive content.
- Redact secrets from logs before including them.
- Keep the email direct and useful. Prefer facts over long explanation.
- If the user is reporting a bug, include reproduction steps and observed behavior when available.
- If the user is suggesting an improvement, include the workflow pain point and desired outcome.
- If the issue depends on environment, include the agent name, repo/path, OS, model/provider, and approximate time when known.

## Email Shape

```text
To: tritonai@ucsd.edu
Subject: TritonAI feedback: <short issue or request>

Hi TritonAI team,

<one-paragraph summary>

Context:
- Agent/tool:
- Repo or workspace:
- What happened:
- Expected result:
- Relevant command/error:

Thanks,
<sender name if known>
```

Omit empty context fields. For quick feedback, a three-sentence email is better than a padded report.
