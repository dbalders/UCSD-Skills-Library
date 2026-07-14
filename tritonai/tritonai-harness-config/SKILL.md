---
name: tritonai-harness-config
description: Investigate and explain the live TritonAI Harness environment using sanitized runtime and source evidence. Use for Harness config files, CODEX_HOME or TRITONAI_HOME, permissions or sandbox modes, models and providers, skills, logs, installation paths, or comparisons with personal Codex or Codex Desktop. Also use for explicit T3 Code or t3code configuration/runtime questions, Harness-versus-T3 Code comparisons, or questions about a t3code identifier in a Harness diagnostic; not unrelated source-code mentions.
---

# TritonAI Harness Configuration

Investigate the environment running now. Do not answer from remembered versions, paths, models, or defaults.

## Principles

- Treat the running Harness and matching `TritonAI-Harness` source as the TritonAI product sources of truth. Treat `pingdotgg/t3code` as parent/upstream unless the user explicitly asks about upstream T3 Code.
- Read applicable `AGENTS.md`, the current repository `README.md`, and relevant docs. Use `rg` to find current implementation and configuration paths.
- Prefer evidence in this order: active session/runtime; Harness settings or diagnostics; matching launcher and process code; resolved on-disk configuration; current docs; defaults and tests.
- Prove that a checkout matches the installed artifact before using it as runtime evidence. Otherwise label it as comparison evidence.
- Separate **active now**, **configured default**, **available option**, and **inferred**. Keep investigation read-only unless the user requests a change.

## Protect Sensitive Data

- Inspect only named variables and requested settings. Never dump the full environment or unrelated process state.
- Never print credentials, tokens, cookies, authorization headers, auth files, or secret stores. Do not open files such as `auth.json`.
- Extract only relevant non-secret config keys or a small redacted log window. For “same config” questions, compare resolved paths before contents.
- Sanitize command lines and remote URLs before quoting them.

## Workflow

### 1. Identify the target

Determine whether the question concerns a current Harness session, installed app, development checkout, personal Codex or Codex Desktop, or upstream T3 Code. For a checkout, record its root, branch, and commit. If live runtime evidence is unavailable, say so rather than substituting repository defaults.

### 2. Resolve the relevant homes

Inspect named values individually when relevant:

```sh
printenv CODEX_HOME
printenv TRITONAI_HOME
```

An unset shell value does not prove what a running app received. Trace the Harness launcher, provider settings, process construction, or diagnostics to resolve defaults and overrides.

Keep these concepts separate:

- `TRITONAI_HOME`: Harness-owned state root, when used by the current implementation
- `CODEX_HOME`: home passed to the selected Codex runtime or provider
- personal Codex home: relevant only when runtime evidence selects it
- repository-local `.agents/`: project instructions or skills, not proof of the active Codex home

Never infer that `~/.codex/config.toml` is merged or effective when `CODEX_HOME` resolves elsewhere. Prove cross-home behavior from current runtime code, arguments, overlays, or filesystem links.

### 3. Trace the effective setting

Search narrowly and exclude generated or dependency trees, for example:

```sh
rg -n --hidden \
  --glob '!**/.git/**' --glob '!**/node_modules/**' \
  --glob '!**/dist/**' --glob '!**/build/**' \
  'CODEX_HOME|TRITONAI_HOME|config\.toml' .
```

Add only terms needed for the active question, such as one permission-mode or log-path identifier. Do not run a broad union of unrelated terms.

For an effective Codex config question:

1. Identify the selected provider or session.
2. Resolve the `CODEX_HOME` passed to its process.
3. Locate the config under that home.
4. Check arguments, overlays, symlinks, and runtime overrides.
5. Inspect only requested non-secret keys.

If the user says the proposed file is wrong, retrace from the active process instead of defending a default-derived path.

### 4. Follow the relevant branch

- **Permissions:** Derive the current mode from session metadata, approval behavior, and Harness runtime state. Use config or source only to explain future launches. For full access versus supervised, state whether a change affects this session or a later one.
- **Models and providers:** Distinguish active selection, configured providers, and the available model catalog. Do not hardcode names, endpoints, availability, or policy. Report authentication only as present, absent, or unknown.
- **Logs and skills:** Derive paths from resolved roots and current path-building code or diagnostics. Separate Harness logs from provider logs and managed skills from Codex-home or repository-local skills. Use bounded listings and prove any overlay behavior.
- **Installation and Codex comparisons:** Inspect the running executable, version metadata, and matching docs or source. Do not assume development, packaged, or operating-system layouts match. Use the installer repository only for installer-owned layout. Compare Harness and Codex using their actual launchers, homes, settings, providers, skills, permissions, logs, and update ownership; consult current official OpenAI documentation when needed.
- **T3 Code:** Treat a `t3code` identifier as possibly inherited until Harness evidence shows otherwise. Do not infer shared configuration from names alone. For “Does t3code use the same config?”, identify the specific processes and compare their resolved homes, launcher arguments, and config paths. Inspect upstream source only when explicitly requested or necessary for comparison.

## Answer Contract

Lead with the answer, then give:

- active runtime evidence
- relevant sanitized locations
- the owning boundary: Harness, personal Codex, upstream T3 Code, or installer
- anything not proven
- a change path only when requested, including whether it affects the current or a future session

Before finishing, confirm that the answer uses live evidence, distinguishes Harness from personal Codex and upstream T3 Code, exposes no sensitive data, and names the effective config or says why it could not be proven.
