# Accessibility Gate for UCSD Branding and Decorator Work

Use this gate every time a UCSD-branded web page, template, component, module,
widget, or shared style changes. Automated checks are required but cannot prove
full accessibility.

## Live sources

Fetch the relevant live pages before policy-sensitive or public-facing work:

- UC San Diego Digital Accessibility Standards:
  <https://accessibility.ucsd.edu/policies-standards/ucsd-accessibility-guidelines.html>
- Website Accessibility Checklist:
  <https://accessibility.ucsd.edu/checklists/websites.html>
- Accessibility Tools:
  <https://accessibility.ucsd.edu/tools/index.html>
- Decorator 5 Kitchen Sink:
  <https://developer.ucsd.edu/design/v5-kitchen-sink/kitchen-sink/index.html>

UC San Diego currently states that websites and digital platforms must be
designed and maintained to WCAG 2.1 AA with ongoing monitoring. The website
checklist also says supported Campus CMS templates and modules are already
optimized for accessibility; do not override their styles, sizing, colors, or
formatting without a concrete, tested reason. If these sources change, follow
the live pages.

## Durable project enforcement

Do not rely on an agent remembering to run a one-time audit.

1. Expose one documented accessibility command in the project, such as
   `test:a11y`, that builds or serves the actual output and exits nonzero on
   failures.
2. Include that command in the default validation command used by contributors.
3. Run it in pull-request checks and in the production-branch deployment job.
4. Derive coverage from a documented route inventory and scan every route at
   each required mobile and desktop width by default. If a route/viewport pair
   cannot be scanned, record the route, viewport, reason, owner, and required
   manual follow-up in the CI report so the exception is reviewable.
5. Fail on browser-load errors, new axe/WCAG violations, horizontal overflow,
   and failed shared-component keyboard interactions.
6. Save a machine-readable report as a CI artifact so reviewers can inspect the
   affected route, viewport, rule, impact, and target.
7. Keep applicable manual checks in the definition of done even when CI passes.
   A pending or failed check blocks publication unless an authorized repository,
   content, or accessibility owner records an explicit waiver naming the
   approver, scope, reason, unresolved risks, remediation owner, and follow-up.
   An agent must not grant its own waiver or infer that approval exists.

Use the project's existing commands and package manager. Do not invent a second
test stack when an equivalent maintained check already exists.

## Page and shell checks

- Provide a unique page title, one meaningful `h1`, logical headings, semantic
  landmarks, and a visible-on-focus skip link targeting the main content.
- Keep page language, reading order, repeated navigation order, link purpose,
  and accessible names programmatically clear.
- Do not use positive `tabindex`, disable viewport zoom, rely on color alone,
  or introduce normal-reading horizontal scrolling.
- Verify text at 200 percent zoom, mobile reflow, portrait and landscape
  orientation, visible focus, and sufficient text and component contrast.
- Check the accessibility statement or assistance path remains reachable.

## Decorator component and module checks

| Surface | Required checks |
|---|---|
| Header, navbar, search, dropdowns, sidebar, drawers | Native links/buttons; unique names; correct `aria-expanded` and `aria-controls`; logical focus order; keyboard open/close; `Escape` closes dismissible UI; focus returns predictably. |
| Carousels | A pause/stop control; keyboard-operable previous/next controls; named slides and controls; hidden slides removed from the focus order; meaningful image alternatives; no ungoverned auto-advance. |
| Tabs and collapse panels | Correct tab/tabpanel or disclosure semantics; arrow-key behavior where the tab pattern is used; `Enter`/`Space` activation; synchronized selected/expanded state; hidden content not focusable. |
| Modals, tooltips, and popovers | Trigger is keyboard accessible; modal has a name; focus moves into the modal, stays within it, returns to the trigger, and closes with `Escape`; essential information is not available only on hover. |
| Forms, input groups, MaxChar, and Wizard | Visible labels; fieldset/legend for grouped choices; instructions and constraints associated with controls; required state communicated in text; errors summarized and tied to fields; dynamic counts, validation, and completion states announced. |
| Tables and DataTables | Use tables only for tabular data; provide headers and `scope`; add a caption or accessible region name when context is not otherwise clear; make horizontal scroll regions keyboard reachable; expose sort state and ensure all controls work by keyboard. |
| Buttons, button dropdowns, and pagination | Use native controls; accessible name matches visible text; current, expanded, and disabled states are programmatic; mobile targets are at least 44 by 44 CSS pixels when practical. |
| Alerts, progress bars, badges, and status messages | Do not communicate status by color alone; expose names, values, and state; announce important async changes without unexpectedly moving focus; honor reduced motion. |
| Images, icons, and helper classes | Meaningful images have concise alternatives; decorative images use empty alternatives; decorative Glyphicons are hidden from assistive technology; visible text remains available when icons fail. |
| FullCalendar | Keyboard access to dates and events; clear current/selected state; meaningful event names; equivalent non-visual access to schedule information. |
| Media | Keyboard-accessible controls; no unmuted autoplay; captions for video with audio; transcripts for audio; descriptions or equivalent text for meaningful visual-only information. |

## Required manual pass

For each affected page and state:

1. Complete the primary task with `Tab`, `Shift+Tab`, `Enter`, `Space`, arrow
   keys for composite widgets, and `Escape` for dismissible UI.
2. Confirm focus is always visible, follows a logical order, and is restored
   after dialogs, drawers, menus, or overlays close.
3. Review at mobile width and 200 percent zoom for content loss, overlap, and
   horizontal scrolling.
4. Spot-check headings, landmarks, names, states, and live announcements with
   VoiceOver, NVDA, or another available screen reader.
5. Inspect component states that automation often misses: open, closed,
   selected, disabled, loading, empty, error, and success.
6. Confirm alternatives, captions, instructions, and error text communicate the
   same purpose as the visual design.

## Completion report

Report:

- exact automated commands and route/viewports checked;
- keyboard, focus, zoom/reflow, contrast, and screen-reader checks completed;
- violations fixed and any remaining manual review;
- checks that could not be run and why.

Say “no issues found in the checks run” rather than “fully compliant” unless an
authorized accessibility review has certified the result.
