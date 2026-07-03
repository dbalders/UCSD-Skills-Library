---
name: ucsd-data-classification
description: Use when building or reviewing a UC San Diego application, automation, script, database, API, or data pipeline that stores, transmits, logs, or displays data — to classify that data under UC's IS-3 Protection Levels (P1–P4) and apply the handling controls each level requires. Trigger when defining data models or database schemas, choosing where to store data, writing logging, building forms or endpoints that collect personal/financial/health/student data, or whenever fields like SSN, credit card, PHI, FERPA student records, passwords, API keys, or other PII appear. Also /ucsd-data-classification, "classify this data", "what protection level", "can I store this", "is this allowed at UCSD".
---

# UCSD Data Classification & Handling

Help classify UC San Diego data under UC policy **BFB-IS-3** and apply the handling
controls each Protection Level requires, so applications and automations protect
regulated data correctly.

This skill reflects UC **systemwide** policy (IS-3), which sets the minimum floor.
UCSD campus-specific guidance (e.g. which services are approved for each level) is
**not yet incorporated** — see *UCSD-specific guidance* below. UCSD may add
requirements that are more restrictive than IS-3, never less.

## How to use this skill

When data appears in a design, schema, or code path, work through these steps:

1. **Identify** the data elements in play — what is stored, transmitted, logged, or displayed.
2. **Classify** each element's Protection Level (P1–P4), and the system's Availability Level — *Step 1*.
3. **Apply** the controls required at the highest level any data touches — *Step 2*. A system, database, log, or backup inherits the Protection Level of the most sensitive data it holds.
4. **Check** the design against the *Guardrails*. Call out any violation explicitly, with the data element and the rule.
5. **Escalate** instead of guessing when data is regulated or classification is ambiguous — *When to escalate*.

## Step 1 — Classify the data (Protection Level)

Assign the **highest** applicable level. Most common code-relevant elements below;
the full pre-classified list and legal definitions are in
[references/protection-levels.md](references/protection-levels.md).

| Level | Common elements |
|---|---|
| **P4 – High** | SSN; credit/debit card data (PCI); PHI / medical / health-insurance info (HIPAA/CMIA); driver's license, passport, visa, or national-ID numbers; biometric data; genetic data; bank/financial account & official accounting records; GLBA financial-aid / student-loan info; **passwords, PINs, API keys, auth secrets, private keys**; export-controlled data (ITAR/EAR); large or comprehensive PII sets |
| **P3 – Moderate** | Student education records (FERPA); UC personnel/HR records; PII in large sets; attorney-client privileged; IT security plans & vulnerability data; building-access & security-camera records |
| **P2 – Low** | Internal business records not meant to be public; de-identified data; UC directory data; exam content |
| **P1 – Minimal** | Public website content; course catalogs; press releases; published research |

Key classification rules:

- **Inheritance:** a copy pulled from a source system (e.g. a student or HR system)
  inherits that source's Protection Level. A store, log, cache, or backup takes the
  level of the **most sensitive** record it contains.
- **Aggregation:** combining several low-risk fields can raise the level (a profile
  assembled from many P2 fields can become P3/P4).
- **Availability Level (A1–A4)** is separate: the impact if the system is *unavailable*.
  Classify it too — it drives backup/DR requirements in Step 2.

## Step 2 — Apply handling requirements by level

Use the level from Step 1. Each row is required **at that level and above**. Section
numbers cite IS-3; the detailed "how" lives in the implementing Standards (see
[references/handling-obligations.md](references/handling-obligations.md)).

| Decision | Requirement |
|---|---|
| **Storage at rest** | P4: encrypt on **any** media (§10.1). P3: encrypt on portable media/devices. → never write P4 to an unencrypted DB, disk, object store, file, cache, or cookie. |
| **In transit** | P3+: must be encrypted in transit (§10.1). → TLS/HTTPS only; no plaintext HTTP, no unencrypted internal hops. |
| **Logging** | Logs inherit the data's Protection Level (§12.4.2); P3+ admin logs are need-to-know (§12.4.3). → never log SSN, PII, PHI, card numbers, or secrets; redact first. |
| **Access control** | P2+: controls to prevent unauthorized access (§9.1.1). P3+: least-privilege, monitored access, segregation of request/approve/grant duties (§9.1.1–9.1.2). → no public/anonymous access to P2+. |
| **Source & secrets** | P3+ source-code access restricted (§14.2); secrets are P4. → no credentials/keys in source, config, or repos; remove debug/undisclosed access paths before prod. |
| **Dev / test** | Test/dev holding P2+ data needs the **same** controls as prod (§12.1.4). → don't copy real P3/P4 into dev, demos, or fixtures; use synthetic or de-identified data. |
| **Backups** | A3+: backed up and recoverable; backups inherit the data's Protection Level (§12.3). |
| **Suppliers / cloud** | P2+ in cloud/SaaS needs a Risk Assessment (§6.1.1); PCI vendors need PCI terms, PHI vendors need a signed BAA (§15). |
| **Secure development** | In-house code handling P2+ must follow the UC Secure Software Development Standard (§14.1); P4 systems require penetration testing (§14.1). |

## Guardrails — never do these

- Never store **P4** (SSN, card, PHI, secrets, etc.) unencrypted — DB, file, object store, cache, cookie, `localStorage`, or temp file.
- Never put PII / PHI / SSN / card numbers in a **URL, query string, or path**.
- Never write P3/P4 data or secrets to **logs, error messages, stack traces, or analytics**.
- Never transmit P3+ over **plaintext HTTP** or any unencrypted channel.
- Never commit **credentials, keys, tokens, or P4 data** to source control.
- Never expose **P2+** data without authentication and authorization (no public endpoints or buckets).
- Never copy **real P3/P4** data into dev/test, demos, or fixtures — use synthetic/de-identified data.
- Never leave **undisclosed/backdoor access** (debug routes, default creds) in production.
- Never send **P3/P4** to a third-party service without a Risk Assessment and contract terms (BAA for PHI, PCI terms for cards).

## When to escalate

Stop and route to a human — the **Unit Information Security Lead**, the
**Institutional Information Proprietor**, or the campus **Information Security Office** —
rather than guess, when:

- Data is **P4** or otherwise regulated (HIPAA, PCI, FERPA, ITAR/EAR, GLBA). These carry legal obligations beyond code.
- Classification is **ambiguous**, or low-risk fields **combine** into something more sensitive.
- The design needs an **exception** to a control — IS-3 requires CISO approval and compensating controls for P3+/P4 (§2.2).
- **Export-controlled** (EAR/ITAR) data is involved — requires the Export Control Office.
- You must choose a **storage location or service** for P3/P4 and cannot confirm it is approved (see below).

## UCSD-specific guidance (to be added)

IS-3 sets the systemwide floor. The campus-specific layer — especially the list of
**approved services / storage for each Protection Level** (where P3/P4 may live, the
campus secure enclave, what is disallowed) and campus contacts — is not yet captured
here. Until it is, when a storage location or service must be chosen for P3/P4 data,
treat it as an **escalation point** and confirm approval with the UCSD Information
Security Office.

## Sources & currency

- **UC BFB-IS-3, Electronic Information Security** (issued 2019-10-25) — controls and Protection/Availability Level definitions.
- **UC Protection Level Classification Guide** (rev. 2022-07-18) — pre-classified data elements.
- Detailed requirements live in the IS-3 implementing **Standards** (Encryption, Event Logging, Account & Authentication, Secure Software Development, Minimum Security, etc.).

Full links, document versions, and the standards list are in
[references/sources.md](references/sources.md). Verify currency against the source
pages; UC reviews standards at least every three years.
