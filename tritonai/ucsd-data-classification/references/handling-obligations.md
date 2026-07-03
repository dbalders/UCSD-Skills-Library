# Handling Obligations by Protection / Availability Level

Source: **BFB-IS-3** (2019-10-25), Sections 8–18. Each requirement is scoped to a
classification **threshold** — it applies at that level *and above*. IS-3 states *what*
scales by level; the *how* lives in the implementing Standards (see
[sources.md](sources.md)).

## Quick threshold map

| Trigger | Required controls (IS-3 §) |
|---|---|
| **P2 or higher** | Access controls preventing unauthorized access (§9.1.1) · secure media disposal (§8.3.2) · secure/tracked media transfer (§8.3.3) · attack/compromise monitoring (§12.2) · in-house code built to the Secure Software Development Standard (§14.1) · cloud/Supplier services risk-assessed (§6.1.1) · Supplier maintenance controls (§11.2.4) |
| **P3 or higher** | Encrypt **in transit** (§10.1) · encrypt on portable media/devices (§10.1, §8.3.1) · Risk Assessment required (§6.1.1) · asset inventory record (§8.1.1) · network access monitored for unauthorized access (§9.1.2) · segregation of duties for access grants + change records (§9.1.1) · segmented networks, unused ports/services disabled, secure service versions, managed admin access (§13.1) · source-code/config access restricted to authorized members (§14.2) · incident reported to CISO + privacy officer (§16.1.2) · admin-log access need-to-know + periodic privileged-account review (§12.4.3) · secure-config baselines + authenticated vulnerability scans (§12.6) · not taken/transmitted off-site without authorization; protected on- and off-site (§11.2.5) · secure transfer between Locations/Suppliers (§13.2) · background checks for access (§7.1) |
| **P4** | Encrypt **at rest on any media** (§10.1) · network access via secure control points, most-restrictive rules, log unauthorized attempts (§9.1.2, §13.1) · penetration testing ≥ every 3 years / after major change (§14.1) · exceptions **require** compensating controls (§2.2) |
| **A3 or higher** | Backed up and recoverable (§12.3) · monitoring for attack/compromise when IT Resource is A3+ (§12.2) |
| **A4** | Environmental/power protection (§11.2.2) · included in emergency & disaster-recovery planning (§17.1) · authenticated vulnerability scans (§12.6) |

## Detail by topic

### Asset management & media (§8)
- Inventory record for P3+ assets, incl. Proprietor, Protection & Availability Levels, location, retention (§8.1.1).
- Encrypt P3+ on portable media; store portable media securely (§8.3.1).
- Securely dispose of media holding P2+ per the Disposal Standard (§8.3.2).
- Track and use secure transfer methods for P2+ media (§8.3.3).

### Access control (§9)
- Need-to-Know and Least-Privilege for all Institutional Information (§9.1.1).
- P2+: controls to prevent unauthorized access.
- P3+: Proprietor sets access rights/role restrictions; **segregate requestor / approver / grantor** roles (or compensating controls); keep change + approval records.
- Unique user account per person (§9.2.1); approval process + required training before access (§9.2.2).
- P4 network access routed through secure access-control points; P3+ network access monitored (§9.1.2).

### Encryption (§10)
- P3+: encrypt **in transit** over a network.
- P3+: encrypt on portable media / portable computing devices.
- **P4: encrypt at rest on *any* electronic media.**
- Use a CISO-approved method; follow the Encryption Key & Certificate Management Standard.

### Operations, logging, backup (§12)
- Separate prod / test / dev; test/dev containing Institutional Information needs the **same controls as prod** for its level (§12.1.4).
- Monitor for attack/compromise when P2+ info, or P3+/A3+ IT Resources, are present (§12.2).
- A3+: backed up and recoverable; backups inherit the data's Protection Level; test restores (§12.3).
- Comply with the Event Logging Standard (§12.4.1); **protect logs at the Protection Level of the data they contain** (§12.4.2); P3+ admin-log access is need-to-know with periodic privileged-account review (§12.4.3).
- Only supported/patched software; secure-config baselines and authenticated vuln scans for P3+/A4 (§12.6).

### Communications security (§13)
- P3+ IT Resources on **segmented networks** restricted to P3+ peers; protected ingress/egress; managed admin access; unused ports/protocols/services off; secure service versions (§13.1).
- P4 access-control network devices: most-restrictive rules, authorized connections only, log unauthorized attempts (§13.1).
- P3+ transfers between Locations / to Suppliers use CISO- and Proprietor-approved controls (§13.2).

### Secure development (§14)
- Identify security requirements in planning, per the Secure Software Configuration Standard, Risk Assessment, levels, and Minimum Security Standard (§14.1).
- **In-house code handling P2+ must follow the Secure Software Development Standard** (§14.1).
- P4: penetration testing ≥ every 3 years and after major change (§14.1).
- P3+ source code/config access restricted to authorized members; **version control required** for production source/config; remove or document any non-formal access methods before production (§14.2).

### Suppliers (§15)
- Agreements carry security terms (UC Appendix – Data Security and Privacy or CISO-approved equivalent).
- PCI suppliers sign PCI terms; HIPAA Business Associates sign a **BAA**.
- Suppliers must not share/harvest/pass-through UC credentials, create backdoors, or disable controls without approval.

### Incident, continuity, compliance (§16–18)
- Report suspected incidents promptly; P3+ incidents → CISO → Location privacy officer (§16.1.2).
- A4 resources included in emergency/DR planning (§17.1).
- Meet legal/contractual/grant obligations for security, privacy, IP, and encryption (§18.1).

## Exceptions (§2.2)
Exceptions to Sections 7–18 go to the CISO via the Location process. **Compensating
controls are required** when the exception involves an obligation by law/regulation/
agreement, P3+ Institutional Information, or P4 IT Resources.
