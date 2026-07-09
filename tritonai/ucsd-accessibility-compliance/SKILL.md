---
name: ucsd-accessibility-compliance
description: Use for UC San Diego digital accessibility work across websites, web apps, Campus CMS or Simple Sites pages, LMS content, forms, documents, PDFs, presentations, email campaigns, social posts, images, graphics, audio, and video. Helps implement, audit, or remediate content against official UCSD accessibility guidance, UCSD Digital Accessibility Standards, WCAG 2.1 AA expectations, ADA Title II and UC policy context, keyboard and screen-reader usability, semantic HTML, forms, contrast, alt text, captions, transcripts, accessible documents, and practical manual review steps. Trigger on /ucsd-accessibility, accessibility review, a11y, WCAG, ADA Title II, Siteimprove, screen reader, keyboard access, alt text, captions, transcripts, PDF remediation, or "is this accessible at UCSD".
---

# UCSD Accessibility Compliance

Use this skill to make UC San Diego digital content more accessible and easier to review. Treat it as implementation and audit support, not official certification. Full accessibility still requires judgment, manual testing, assistive-technology checks, and sometimes review by UCSD accessibility staff or the responsible compliance owner.

## Source Of Truth

Use the live UCSD sources before giving policy-sensitive advice, reviewing published content, or relying on date-based requirements. Read `references/official-sources.md` to choose the right page.

Prefer these source classes:

- UCSD Digital Accessibility Standards for scope, policy frame, responsibilities, exceptions, and enforcement timing.
- UCSD checklists for artifact-specific work: websites, writing, images, audio/video, documents, PDF remediation, presentations, social media, and email campaigns.
- UCSD Tools for Siteimprove, Accessible Brand Color Combinations, Campus CMS, Simple Sites, NVDA, and VoiceOver pointers.
- WCAG 2.1 AA for technical success criteria when UCSD pages defer to the standard.

If the UCSD page conflicts with this skill, the live UCSD page wins.

## Workflow

1. Identify the artifact type: website, app, LMS page, form, document, PDF, presentation, email, social post, image, chart, audio, video, or mixed content.
2. Inspect the actual artifact before advising. For code, find layout, routing, component, theme, form, media, and document-generation paths. For files, inspect structure, metadata, reading order, tags, and exported output where practical.
3. Fetch the relevant UCSD source page when the work is public-facing, login-protected, internally accessible, high-risk, policy-sensitive, covered by UCSD policy, or checklist-specific.
4. Apply UCSD and WCAG 2.1 AA basics: perceivable content, keyboard operation, understandable labels and instructions, robust semantics, and equal access to core tasks.
5. Separate automated findings from manual review. Automated tools can catch many syntax and contrast issues; they cannot prove screen-reader flow, reading order, caption quality, plain-language clarity, or workflow recovery.
6. Fix blockers with small, reversible changes that preserve the visible intent. Prefer semantic HTML and native controls before adding ARIA.
7. Run the most relevant checks before finishing: build/lint/typecheck, axe or equivalent scan, keyboard pass, responsive and 200 percent zoom review, contrast check, screen-reader spot check, and file-level accessibility checks for documents or presentations.
8. Report what was checked, what changed, what still needs manual verification, and whether official UCSD review is still needed.

## UCSD Defaults

- Target WCAG 2.1 AA for UCSD digital content unless a current UCSD source says otherwise.
- Treat accessibility as applying beyond public websites: portals, login-protected resources, LMS content, mobile apps, forms, surveys, documents, maps, media, social posts, and HTML email can all be in scope.
- For Campus CMS, Simple Sites, and centrally supported UCSD templates, preserve built-in accessibility defaults. Do not override text sizing, colors, layout, or focus behavior without a concrete reason.
- Use UCSD Accessible Brand Color Combinations when choosing UCSD-branded text/background colors. Pair with `ucsd-branding` for campus web branding work.
- Use Siteimprove when the site is registered or when the user has access. Do not treat Siteimprove as the only check.
- Do not silently decide that an exception applies. Name the possible exception, cite the UCSD source, and recommend confirmation with the responsible owner.
- Do not claim content is "fully compliant" unless an authorized accessibility review has happened. Prefer "aligned with the checked UCSD guidance" or "no issues found in the checks run."

## Web And App Review

Use this for websites, web apps, portals, LMS pages, dashboards, and forms.

- Provide one meaningful `h1` per page and a logical heading outline.
- Use landmarks and semantic structure: `header`, `nav`, `main`, `article`, `section`, `aside`, and `footer` where appropriate.
- Add a skip link that becomes visible on focus and targets the main content region when the page shell does not already provide one.
- Keep keyboard focus visible, high contrast, and predictable. Test `Tab`, `Shift+Tab`, `Enter`, `Space`, arrow keys for composite widgets, and `Esc` for dismissible overlays.
- Do not use positive `tabindex`. Use `tabindex="0"` only when a custom focusable element is unavoidable, and `tabindex="-1"` for managed focus targets.
- Use native controls first: `button` for actions, `a` for navigation, `label` for inputs, `fieldset` and `legend` for grouped choices.
- Use ARIA only to fill real semantic gaps. Do not add ARIA that conflicts with native semantics or creates custom-widget obligations the component does not satisfy.
- Keep link text descriptive. Warn users in link text when a link opens a new tab or window, downloads a file, opens a PDF, or requires login.
- Do not disable viewport zoom. Confirm the page works at 200 percent zoom and mobile widths without horizontal scrolling for normal reading.
- Ensure status messages, validation updates, loading states, and async results are announced through appropriate live regions or focus management.

## Forms

- Associate every input with a visible label.
- Use helper text with `aria-describedby` for format, requirement, privacy, or consequence guidance.
- Group related choices with `fieldset` and `legend`.
- Identify required fields in text, not color alone.
- On validation failure, place a summary above the form, move focus to it when appropriate, and link each error to the affected field.
- Keep inline errors programmatically associated with fields and update them in a way screen readers can detect.
- For legal, financial, enrollment, employment, health, or user-data changes, provide review, correction, confirmation, or reversal paths.

## Documents, Media, And Campaigns

- Prefer accessible HTML over PDF when the content is primarily web content and does not need a fixed document format.
- For PDFs, inspect the exported PDF, not only the source document. Check tags, headings, reading order, title, language, tables, figures, and image alternatives.
- For presentations, use built-in slide layouts, unique slide titles, logical reading order, and alt text for meaningful images.
- For images and charts, provide concise alt text or equivalent surrounding text. For complex charts, provide a text summary or data table.
- For audio and video, use a keyboard-accessible player, avoid autoplay, provide transcripts for audio, captions for video with audio, and audio description or equivalent text for meaningful visual-only information.
- For social posts, use platform-native alt text, captions for videos, descriptive links, and PascalCase or camelCase hashtags.
- For email campaigns, preserve robust reading order across common clients, use descriptive links, check contrast and alt text, and test in target clients when the campaign matters.

## Review Output

Lead with issues that block access or UCSD compliance:

1. Blockers: barriers that prevent keyboard, screen-reader, low-vision, mobile, caption/transcript, form, or document access.
2. Required fixes: concrete implementation changes with file paths or artifact locations.
3. Manual checks still needed: screen-reader flow, reading order, caption accuracy, email-client rendering, document tags, or policy exception confirmation.
4. Recommended improvements: usability and clarity changes that reduce accessibility risk.
5. Checks run: exact commands, tools, browsers, devices, assistive tech, files inspected, and checks not run.
