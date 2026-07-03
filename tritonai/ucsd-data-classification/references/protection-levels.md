# UC Protection Levels — Pre-Classified Data Elements

Source: **UC Protection Level Classification Guide** (IT Security Committee item SC-0003,
rev. 2022-07-18) and **BFB-IS-3** §8.2.1. These are pre-classified to save Proprietors
time. If a data type is not listed, consult the *UC Institutional Information and IT
Resource Classification Standard*.

> **Note:** Over-classification adds needless cost and compliance burden;
> under-classification risks inadequate protection and breaches. Assign the **highest**
> level that applies to any element involved.

## Contents

- Level definitions and availability levels
- Protection Level 4 (P4)
- Protection Level 3 (P3)
- Protection Level 2 (P2)
- Protection Level 1 (P1)
- Special case
- Key terms and acronyms

## Level definitions (IS-3 §8.2.1)

| Level | Impact of disclosure or compromise |
|---|---|
| **P4 – High** | Unauthorized disclosure or modification could result in significant fines, penalties, regulatory action, or civil/criminal violations. Statutory, regulatory, contractual obligations are major drivers. *(Statutory.)* |
| **P3 – Moderate** | Could result in small-to-moderate fines, penalties, or civil action; moderate damage or privacy impact; moderate financial loss. Includes lower-risk items that, combined, raise risk. *(Proprietary.)* |
| **P2 – Low** | Not specifically protected by statute/regulation/contract but generally not for public use; unauthorized use could cause minor damage or small financial loss. *(Internal.)* |
| **P1 – Minimal** | Public information, or information intended to be readily obtainable by the public; integrity (preventing unauthorized modification) is the primary concern. *(Public.)* |

### Availability Levels (IS-3 §8.2.1)

| Level | Impact of loss of availability |
|---|---|
| **A4 – High** | Major impairment to Location operation / essential services, and/or significant financial loss. |
| **A3 – Moderate** | Moderate financial loss and/or reduced service. |
| **A2 – Low** | Minor losses or inefficiencies. |
| **A1 – Minimal** | Minimal impact or minor financial loss. |

## Protection Level 4 (P4)

| Institutional Information type | Justification |
|---|---|
| Building access systems | Life and safety |
| Code-signing certificates or keys | Operational integrity |
| Covered Defense Information (CDI), incl. Controlled Technical Information (CTI), DFARS 252.204-7012 | Government contract |
| Controlled Unclassified Information (CUI) | Government contract |
| Credit card cardholder information | Payment Card Industry (PCI) |
| Disability or other medical information collected from students to provide services | Privacy, regulation, statute |
| EAR / ITAR / 10 CFR Part 810 (transfer of unclassified nuclear tech). *EAR can be P4 or P3 — contact the Export Control Office.* | Regulation |
| Customer Information re student loans, federal financial aid, and other GLBA financial services | Privacy, GLBA |
| Financial, accounting, and payroll information (official accounting records) | Integrity |
| Human-subject research data with individual identifiers (esp. identifiers listed in law) | Privacy, regulation |
| Individually identifiable genetic information (human-subject identifiable) | Privacy, regulation |
| Information with contractual requirements for P4-level protection | Contract |
| Passwords, PINs, passphrases, or other authentication secrets that access P2–P4 info or manage IT Resources | Operational integrity |
| PII / PI in large sets or comprehensive sets about a person (e.g. work accident with medical records; GDPR Art. 9 special categories) | Privacy, regulation, statute |
| Private encryption keys | Operational integrity |
| Protected Health Information (PHI), health information, medical & patient records | HIPAA, CMIA, IPA |
| Research info classified P4 by an IRB, or required to be in a high-security environment | Academic integrity |
| Sensitive Identifiable Human Subject Research data, or research under a Certificate of Confidentiality / the Common Rule | Privacy, regulation |
| **Social Security Numbers** (subset of PII) | Regulation, statute |

## Protection Level 3 (P3)

| Institutional Information type | Justification |
|---|---|
| Animal research protocols | Academic integrity, safety |
| Attorney-client privileged information | Legal protection, statute |
| Building entry records from automated key-card systems | Protective information |
| Certain types of federal data | FISMA |
| Export-Controlled Research (EAR and ITAR). *EAR can be P3 or P4 — contact the Export Control Office.* | Regulation |
| IT security information, exception requests, system security plans | Protective information |
| PII / Personal Data (GDPR Art. 4(1)) in large sets | Regulation, statute |
| Research info classified P3 by an IRB | Academic integrity |
| Security-camera recordings, body-worn video, cameras recording cash/payment-card areas | Protective information, contract |
| Student education records | FERPA |
| Student special-services records (services/accommodations with an expectation of privacy) | Privacy, FERPA |
| UC personnel records | Privacy |

## Protection Level 2 (P2)

| Institutional Information type | Justification |
|---|---|
| Building plans and physical-plant information | Operational integrity, protective info |
| Calendar information without P3/P4 content | Operational integrity |
| De-identified patient information (negligible re-identification risk) | Academic integrity |
| Exams (questions and answers) | Academic integrity |
| Meeting notes without P3/P4 content | Operational integrity |
| Patent applications & work papers not under a secrecy order or contractual restriction | Academic / operational integrity |
| Research using publicly available data | Operational integrity |
| Routine business records and emails without P3/P4 content | Operational integrity |
| UC directory (faculty, staff, students without a FERPA block) | Operational integrity |
| Unpublished research, drafts, IP not classified P3/P4 | Academic integrity |

## Protection Level 1 (P1)

Course catalogs · hours of operation · parking regulations · press releases · public
event calendars · public-facing websites intended for unrestricted access · published
research — all *Intended for public use*.

## Special case

Records under a legal **Notice of Duty to Preserve** may require a higher Protection
Level — consult Location Counsel.

## Key terms & acronyms

- **PII (Personally Identifiable Information):** sensitive info that uniquely identifies,
  contacts, or locates a person. Examples: government ID numbers — **SSN, driver's
  license, passport, national ID, visa** — plus **genetic data, biometric information,
  medical/health-insurance information**, and other elements named in California civil
  code. (CA codes 1798.29 / 1798.82 / 1798.84 govern PI; UC uses the "PII" convention.)
- **PHI / Health / Medical Information:** individually identifiable health info governed
  by **HIPAA** and **CMIA** — past/present/future physical or mental health, treatment,
  care provision, or payment/insurance for care.
- **PCI:** credit, debit, or other payment-card data, governed by the PCI Data Security
  Standard.
- **FERPA:** student education records maintained by UC or someone acting for it.
- **GLBA:** "Customer Information" re financial services (16 CFR 314.2 / 313.3); see the
  UC GLBA Compliance Plan.
- **CUI / CDI:** information requiring safeguarding/dissemination controls per law,
  regulation, or contract (FAR/DFARS); see NIST SP 800-171.
- **EAR / ITAR:** export-controlled research (national security, foreign policy,
  anti-terrorism, non-proliferation). Must be stored in the U.S. with access limited to
  authorized U.S. persons. Examples: chemical/biological agents, satellite data, certain
  software/technical data, military electronics, nuclear-physics info.
- **GDPR:** EU privacy law; Article 9 "special categories" are treated as P4.
- **FISMA:** federal security-program requirements; data stored on U.S. soil.
- **CoC / Common Rule:** protections for identifiable, sensitive human-subject research.
