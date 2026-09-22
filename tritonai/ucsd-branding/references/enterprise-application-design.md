# Enterprise Application Design Standard for UC San Diego Decorator 5

## Provenance and currency

This is a product-team extension for enterprise application canvases inside
Decorator 5. It is not a Decorator or official UCSD brand source of truth.
Current as of September 21, 2026. Decorator-owned foundations remain governed by
`developer.ucsd.edu` and the installed Decorator templates. Fonts may be supplied
by Decorator (`Roboto` and `Teko`) or an approved project source.

## 1. Purpose

This document defines how an enterprise application should look, behave, and communicate inside UC San Diego Decorator 5.

Decorator 5 provides the institutional frame. This design standard governs the application experience inside that frame. The goal is a coherent UC San Diego experience without treating Decorator 5 as a complete enterprise application component library.

This document is intentionally written as a design contract. Requirements using **must**, **must not**, **should**, and **may** are intended to be testable by designers, developers, QA, and coding agents.

## 2. The governing boundary

Every page has two ownership zones.

| Zone | Owner | Examples | Change policy |
| --- | --- | --- | --- |
| **Decorator chrome** | UC San Diego Decorator 5 | Campus header, institutional identity, global/site navigation, search, mobile drawer, footer, associated scripts | Protected. Reuse canonical markup and behavior. Do not redesign, reconstruct, or override. |
| **Application canvas** | Product team | App navigation, page headers, workflows, forms, tables, cards, dashboards, dialogs, messages | Editable under this standard. |

### 2.1 Protected Decorator chrome

The following are outside the application design scope:

- UC San Diego header and wordmark
- Decorator global or site navigation
- Decorator search interfaces and search scope controls
- Decorator mobile navigation and drawer behavior
- Decorator footer
- Decorator-owned IDs, classes, data attributes, DOM hierarchy, styles, and scripts

The product team **must not**:

- redraw or approximate protected chrome;
- move application actions into the UC San Diego header or footer;
- use application CSS to restyle Decorator selectors;
- use application JavaScript to alter Decorator markup or behavior;
- copy markup from the browser's rendered DOM as the source of truth;
- replace a Decorator control with a visually similar custom control; or
- combine application navigation with institutional navigation.

The installed `ucsd-decorator-v5` templates are the implementation source of truth. The Decorator Kit rules and integrity checks are the source of truth for how the boundary is enforced.

### 2.2 Application canvas

The application canvas begins after the Decorator navigation and ends before the Decorator footer. Everything specific to the product belongs here, including:

- product identity and context;
- application navigation;
- page title, breadcrumbs, and page-level actions;
- business workflows;
- forms, tables, dashboards, and detail views;
- loading, empty, success, warning, and error states; and
- contextual help and product support.

The canvas **must** have one explicit root container. Application styles and scripts must be scoped to that root.

### 2.3 Decorator inheritance and override register

This document follows an **inherit first** rule. If Decorator already owns a foundation or behavior, the application uses it without restating or reimplementing it. A difference is allowed only when it appears in the intentional override/extension column below and remains scoped to the application canvas.

| Design concern | Decision | Reason and scope |
| --- | --- | --- |
| Header, institutional navigation, search, mobile drawer, and footer | **Inherit** | Protected Decorator chrome; never overridden by this document |
| Bootstrap grid mechanics, gutters, and responsive breakpoints | **Inherit** | Use the grid shipped with Decorator 5; do not publish competing grid tokens |
| Base document reset and chrome typography | **Inherit** | Decorator remains authoritative outside the application root |
| Application typography | **Intentional override** | `Roboto` and `Teko` apply only inside the application root and replace Decorator's base type choices there |
| Application semantic colors | **Application extension** | Named roles translate approved colors into stable application meaning; they do not restyle chrome |
| Application component spacing | **Application extension** | The 5 px scale governs component internals and non-Bootstrap layouts; Bootstrap rows retain inherited gutter behavior |
| Application buttons | **Intentional override** | The recipes in Section 6 apply only to application-owned buttons, not Decorator controls |
| Radius, elevation, icons, and motion | **Application extension** | Decorator does not serve as the enterprise component specification for these concerns |
| Forms, tables, cards, dialogs, workflow states, and content rules | **Application extension** | These rules cover enterprise behavior within the canvas without changing Decorator components |

Any future Decorator override must be added to this table with its reason, scope, owner, accessibility impact, and migration plan before implementation.

---

## 3. Design principles

### 3.1 Make the next action clear

Each page should communicate where the user is, what matters now, and what they can do next. Prefer one obvious primary action over several equally prominent actions.

### 3.2 Optimize for real work

Enterprise users may complete long, repetitive, or high-consequence tasks. Favor legibility, predictable placement, efficient scanning, and error prevention over novelty.

### 3.3 Reveal complexity progressively

Show essential information first. Place advanced controls, infrequent settings, and supporting detail behind clear disclosure patterns without hiding information required to make a decision.

### 3.4 Be accessible by default

Accessibility is a design input, not a final audit. Every component and flow must work without color alone, without a mouse, at browser zoom, and with assistive technology.

### 3.5 Respect the institutional frame

The application should feel compatible with UC San Diego while remaining visually subordinate to the Decorator shell. Use brand color to establish identity and hierarchy, not to decorate every surface.

### 3.6 Prefer consistency over cleverness

One concept should have one name, one interaction pattern, and one visual treatment across the product.

---

## 4. Page anatomy

Use the following order for standard application pages:

1. Decorator header and institutional navigation
2. Application identity and application navigation
3. Optional breadcrumbs
4. Page header
   - page title
   - concise description or status when needed
   - primary and secondary page actions
5. Optional page-level message
6. Main content
7. Optional contextual or secondary content
8. Decorator footer

### 4.1 Page header

- Each route must have one visible `h1` that matches the user's current task or object.
- Page titles should use plain language and normally remain under 60 characters.
- Place the primary page action at the end of the title row on wide screens and beneath the title on narrow screens.
- Show no more than one filled primary button in the page header.
- Put low-frequency actions in an overflow menu when crowding occurs.
- Do not use cards solely to contain a page title.

### 4.2 Breadcrumbs

- Use breadcrumbs for hierarchies deeper than one level or when users commonly move to a parent record.
- Do not use breadcrumbs as a substitute for application navigation.
- The current page may be plain text and must not link to itself.
- On small screens, shorten the trail while preserving access to the immediate parent.

---

## 5. Layout and responsive behavior

### 5.1 Layout rules

- Use a centered content area with consistent horizontal gutters.
- Prefer readable line lengths for prose and wider regions for tables, dashboards, and complex forms.
- A page may use an application sidebar, a full-width content layout, or a content-plus-aside layout. It should not mix these without a workflow reason.
- Align related headings, fields, tables, and actions to a shared grid.
- Avoid nested cards and repeated boxes when spacing and headings create sufficient grouping.

### 5.2 Spacing

Use the canonical application spacing tokens for component internals and non-Bootstrap application layouts. The scale follows a 5 px rhythm and aligns with Bootstrap 3's inherited 15 px half-gutter and 30 px full gutter. It extends Decorator; it does not replace Decorator's grid.

| Token | Value | Typical use |
| --- | ---: | --- |
| `0` | 0 px | Remove spacing explicitly |
| `xxs` | 5 px | Very tight icon or inline relationships |
| `xs` | 10 px | Compact internal gaps |
| `sm` | 15 px | Bootstrap 3 half-gutter and control relationships |
| `md` | 20 px | Standard component padding |
| `lg` | 25 px | Section or card padding |
| `xl` | 30 px | Bootstrap 3 full grid gutter and major separation |
| `xxl` | 45 px | Page-section separation |
| `xxxl` | 60 px | Rare, large layout intervals |

When using the inherited Bootstrap 3 grid:

- Use Decorator's `.container`, `.row`, and `.col-*-*` implementation as shipped.
- Do not redeclare container padding, column padding, or negative row margins in application tokens.
- Do not use CSS `gap` as a substitute for the Bootstrap gutter on Bootstrap rows.
- Avoid nesting padded containers when that would produce unintended 30 px or 45 px edge spacing.
- Application components that are not Bootstrap rows may use the spacing scale normally.

### 5.3 Responsive behavior

Design behavior, not only breakpoints.

| Wide viewport | Narrow viewport |
| --- | --- |
| Application sidebar may remain visible | Sidebar becomes an application-owned drawer or menu inside the canvas |
| Page title and actions may share a row | Actions stack below the title |
| Multi-column forms may use two columns | Forms become one column |
| Tables show priority columns | Lower-priority columns hide, collapse into rows, or move to a detail view |
| Secondary panel may sit beside content | Secondary panel moves below content or opens on demand |

The application must not take control of or conflict with the Decorator mobile drawer. Responsive layout uses the breakpoints shipped with Decorator's Bootstrap 3.3.7 distribution. This document does not define a second breakpoint scale.

---

## 6. Visual language

### 6.0 Canonical design tokens

The following token set is the source of truth only for application-specific semantics and intentional overrides in the **application canvas**. Inherited Decorator foundations are deliberately absent. Components must bind to semantic roles, never to an unnamed raw palette value. Primitive palette tokens are deliberately withheld.

The literal values below define the semantic roles; they do not authorize application code to restyle protected Decorator chrome. When a token changes, consumers inherit the change through the semantic name rather than replacing values component by component.

```yaml
colors:
  # Semantic roles only. Primitives are withheld deliberately.
  primary: "{colors.theme-primary}"

  component-btn-gold: "#c69214"
  component-btn-label-black: "#000000"
  component-btn-label-primary: "#182b49"
  component-btn-label-secondary: "#182b49"
  component-btn-label-white: "#ffffff"
  component-btn-navy: "#182b49"
  component-btn-orange: "#fc8900"
  component-btn-primary: "#ffcd00"
  component-btn-secondary: "#00629b"
  component-btn-turquoise: "#00c6d7"

  component-card-blue: "#00629b"
  component-card-navy: "#182b49"
  component-card-semi-transparent-blue: "rgba(0, 98, 155, 0.8)"
  component-card-semi-transparent-navy: "rgba(24, 43, 73, 0.8)"
  component-icon: "#182b49"
  component-link: "#00629b"
  component-menu: "#747678"

  foreground-body-text: "#313232"
  foreground-body-text-focus: "#182b49"
  foreground-card-border: "#d4d5d5"
  foreground-divider: "#647185"
  foreground-eyebrow: "#182b49"
  foreground-h1-heading: "#00629b"
  foreground-h2-heading: "#182b49"
  foreground-h3-heading: "#182b49"
  foreground-heading-light: "#ffffff"
  foreground-subcard-border: "#182b49"
  foreground-subheading: "#182b49"

  status-critical: "#bd1900"
  status-good: "#109b00"
  status-warning: "#fc8900"

  surface-1: "#ffffff"
  surface-2: "#f5f0e6"
  surface-3: "#00629b"
  surface-4: "#182b49"
  surface-5: "#f8f8f9"

  system-bg-error: "#f8e8e6"
  system-bg-information: "#e6eff5"
  system-bg-success: "#e7f5e6"
  system-bg-warning: "#fff3e6"
  system-error: "#bd1900"
  system-foreground-error: "#ac1700"
  system-foreground-information: "#00629b"
  system-foreground-success: "#0b6e00"
  system-foreground-warning: "#975200"
  system-information: "#00629b"
  system-success: "#109b00"
  system-success-small-text: "#0a8902"
  system-warning: "#fc8900"

  theme-accent: "#ffcd00"
  theme-primary: "#182b49"
  theme-secondary: "#00629b"

typography:
  body-sm:
    fontFamily: "'Roboto'"
    fontSize: "14px"
    lineHeight: "18px"
    fontWeight: 400
    letterSpacing: "0"
  body-md:
    fontFamily: "'Roboto'"
    fontSize: "18px"
    lineHeight: "23px"
    fontWeight: 400
    letterSpacing: "-0.08px"
  body-lg:
    fontFamily: "'Roboto'"
    fontSize: "20px"
    lineHeight: "30px"
    fontWeight: 400
    letterSpacing: "-0.08px"
  body-xlg:
    fontFamily: "'Roboto'"
    fontSize: "24px"
    lineHeight: "29px"
    fontWeight: 400
    letterSpacing: "0"
  eyebrow:
    fontFamily: "'Teko'"
    fontSize: "14px"
    lineHeight: "16px"
    fontWeight: 600
    letterSpacing: "0.8px"
  h1:
    fontFamily: "'Teko'"
    fontSize: "56px"
    lineHeight: "56px"
    fontWeight: 600
    letterSpacing: "0.6px"
  h2:
    fontFamily: "'Teko'"
    fontSize: "40px"
    lineHeight: "40px"
    fontWeight: 600
    letterSpacing: "0.5px"
  h3:
    fontFamily: "'Teko'"
    fontSize: "24px"
    lineHeight: "24px"
    fontWeight: 600
    letterSpacing: "0"
  subheading:
    fontFamily: "'Roboto'"
    fontSize: "15px"
    lineHeight: "15px"
    fontWeight: 900
    letterSpacing: "1.75px"
  btn-primary:
    fontFamily: "'Roboto'"
    fontSize: "15px"
    lineHeight: "20px"
    fontWeight: 900
    letterSpacing: "1.4px"
  btn-secondary:
    fontFamily: "'Roboto'"
    fontSize: "15px"
    lineHeight: "20px"
    fontWeight: 900
    letterSpacing: "1.4px"
  body:
    fontFamily: "'Roboto'"
  mono:
    fontFamily: "ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace"
  h2-small:
    fontFamily: "'Roboto'"
    fontWeight: 900
    fontSize: "12px"
    lineHeight: "18px"
    letterSpacing: "0"

spacing:
  "0": "0px"
  xxs: "5px"
  xs: "10px"
  sm: "15px"
  md: "20px"
  lg: "25px"
  xl: "30px"
  xxl: "45px"
  xxxl: "60px"

rounded:
  rounded-0: "0px"
  rounded-sm: "5px"
  rounded-md: "10px"
  rounded-lg: "15px"
  rounded-circle: "100px"

components:
  btn-primary:
    backgroundColor: "{colors.component-btn-primary}"
    textColor: "{colors.component-btn-label-primary}"
    rounded: "{rounded.rounded-sm}"
    typography: "{typography.btn-primary}"
    textTransform: "uppercase"
  btn-secondary:
    backgroundColor: "transparent"
    textColor: "{colors.component-btn-label-secondary}"
    textDecorationLine: "underline"
    textDecorationColor: "{colors.component-btn-secondary}"
    typography: "{typography.btn-secondary}"
    textTransform: "uppercase"

icons:
  sm: "10px"
  md: "15px"
  lg: "20px"
  xl: "30px"

elevation:
  "0": "none"
  "1": "0 1px 2px 0 rgba(24, 43, 73, 0.08)"
  "2": "0 2px 6px 0 rgba(24, 43, 73, 0.10)"
  "3": "0 6px 16px 0 rgba(24, 43, 73, 0.12)"
  "4": "0 12px 32px 0 rgba(24, 43, 73, 0.16)"

motion:
  duration:
    fast: "120ms"
    base: "200ms"
    slow: "320ms"
  easing:
    standard: "cubic-bezier(0.2, 0, 0, 1)"
    enter: "cubic-bezier(0, 0, 0, 1)"
    exit: "cubic-bezier(0.3, 0, 1, 1)"
```


#### Token-use rules

- Use semantic aliases in component definitions, even when two roles currently resolve to the same value.
- Do not replace aliases with literals in application components.
- Do not create primitive names such as `blue-500` or `yellow-300` in this contract.
- Do not recreate inherited Decorator grid, breakpoint, reset, or chrome tokens in the application token output.
- Use `component-*` roles only for the component family named by the token.
- Use `system-*` roles for messages and feedback; use `status-*` roles for compact statuses and data indicators.
- Validate contrast in the actual foreground/background pairing. A token's presence does not guarantee that every combination is accessible.
- Font assets must come from an approved UC San Diego or project source. Do not fetch substitute webfonts from an unapproved third party.
- Token changes require design-system review; do not override a token locally to fix a single component.

### 6.1 Color

Use the semantic color roles defined in Section 6.0. Decorator assets remain authoritative for protected chrome; this application token set governs the canvas.

Application color roles must be semantic:

| Role | Intended use |
| --- | --- |
| Primary | Main action, active application navigation, selected state |
| Neutral | Text, borders, backgrounds, disabled surfaces |
| Information | Neutral system information |
| Success | Confirmed completion or positive status |
| Warning | Condition requiring attention but not blocking progress |
| Danger | Error, failure, destructive or irreversible action |

Rules:

- Never rely on color alone to communicate state.
- Pair semantic color with text and, when useful, an icon.
- Reserve strong saturated color for small, meaningful areas.
- Do not use yellow or gold body text on white.
- Links must remain visually identifiable outside of hover.
- Text and interactive elements must meet WCAG 2.2 AA contrast requirements.

### 6.2 Typography

- Use the typography tokens in Section 6.0. This is an intentional, canvas-scoped override of Decorator's base typography: `Roboto` is the application body and control family, while `Teko` is reserved for the defined display hierarchy. Decorator typography remains unchanged outside the application root.
- Use sentence case for page titles, headings, field labels, tabs, and menu items. All visible textual button labels render in uppercase.
- Use `body-md` as the default body style. `body-sm` is reserved for compact supporting metadata and must not become the default page copy style.
- Apply `h1`, `h2`, and `h3` according to semantic document structure; never select a heading token only for its appearance.
- Use weight, size, and spacing before introducing additional colors.
- Do not use more than three heading levels on a typical page.
- Use tabular numerals where columns of changing numeric values must align.

Recommended hierarchy:

| Style | Purpose |
| --- | --- |
| Page title | One per page; identifies the route or object |
| Section heading | Divides major page regions |
| Subsection heading | Groups closely related content |
| Body | Default content and instructions |
| Label | Names an input or compact data field |
| Supporting text | Help, metadata, timestamps, secondary detail |

### 6.3 Shape, borders, and elevation

- Use the `rounded` and `elevation` tokens in Section 6.0.
- Use borders or background changes for most grouping.
- Prefer elevation `0` or `1` for persistent surfaces. Reserve stronger elevation for temporary layers such as dialogs, popovers, menus, and drawers.
- Do not add ornamental shadows to every card.
- Focus indication must remain visually stronger than ordinary borders.

#### UI Border and Corner Guideline

UI elements may have rounded corners on only some sides. That is allowed.

The rule is: **never draw a border line along a side or corner that is rounded**.

If a side has a visible border, divider, selection line, outline segment, or accent stroke, that side should remain square. Rounded corners should only appear where no border line is being drawn through or along that rounded edge.

##### Do

- Use partial corner rounding when it suits the shape or layout.
- Use border lines on straight edges only.
- Allow rounded corners on sides that do not carry a border line.

##### Don't

- Do not apply a border line to a side that has rounded corners.
- Do not let a one-sided border or accent stroke follow a rounded corner.
- Do not create a curved or pill-like border segment at the end of a one-sided line.

For example, a selected navigation item can have rounded outer corners, but if it uses a blue selection line on the left edge, the left-side corners should be square so the line remains straight and does not wrap around a rounded edge.

### 6.4 Icons

- Icons support labels; they do not replace unfamiliar labels.
- Icon-only controls require an accessible name and a discoverable tooltip where appropriate.
- Use one approved icon family throughout the application.
- Size icons with the `icons` scale in Section 6.0.
- Do not use an icon whose meaning changes between screens.

### 6.5 Motion

- Motion must explain change, location, or hierarchy.
- Avoid decorative motion in task-focused workflows.
- Use the duration and easing tokens in Section 6.0 rather than introducing component-specific timing values.
- Respect `prefers-reduced-motion`.
- Do not make users wait for an animation before they can continue.

---

## 7. Application navigation

Application navigation belongs entirely inside the canvas and must be visually distinct from Decorator navigation.

### 7.1 Information architecture

- Organize navigation around user goals, not internal departments or database structures.
- Keep the primary level stable across routes.
- Use no more than two visible nesting levels.
- Use the same label in navigation, page title, and documentation for the same concept.
- Hide an inaccessible destination only when revealing it would be inappropriate; otherwise show it disabled only when the reason is useful and explainable.

### 7.2 States

Navigation must define:

- default;
- hover;
- keyboard focus;
- current/active;
- expanded and collapsed, when nested;
- disabled, only when necessary; and
- loading, when permissions or configuration are unresolved.

The active item must be identifiable without color alone.

### 7.3 Mobile behavior

The application menu may become a separate in-canvas drawer, disclosure, or destination list. It must not reuse, imitate, inject content into, or compete with the Decorator mobile navigation control.

---

## 8. Core components

Every component must document its purpose, variants, states, content rules, responsive behavior, accessibility behavior, and examples.

### 8.1 Buttons and actions

| Variant | Use |
| --- | --- |
| Primary | The single most important action in the current context |
| Secondary | Common supporting actions; navy text with a blue underline and no fill |
| Tertiary/text | Low-emphasis or compact actions |
| Danger | Destructive action; use sparingly |

Application-owned primary buttons use the `components.btn-primary` recipe, and application-owned secondary buttons use `components.btn-secondary`. These recipes intentionally override Decorator button presentation only inside the application root; they must not target or alter Decorator controls. Additional gold, navy, orange, and turquoise button roles may be defined only as documented variants with a specific interaction purpose; their existence as color tokens does not make them interchangeable visual options.

Secondary buttons must render uppercase with `#182b49` text, a `#00629b` underline, and a transparent background. The underline is part of the persistent default treatment, not a hover-only affordance. Hover, focus, active, disabled, and loading states must preserve recognition as the same secondary action and continue to meet contrast requirements.

Rules:

- Render every visible textual button label in uppercase, including primary, secondary, tertiary, danger, menu-trigger, and dialog buttons.
- Apply uppercase through the shared application button style rather than rewriting labels independently in each component. Source labels should remain clear verb phrases so accessible names and analytics remain readable.
- Use verb-first labels such as “SAVE CHANGES,” “SUBMIT REQUEST,” or “ADD PERSON.”
- Avoid vague labels such as “OK,” “YES,” “NO,” or “SUBMIT” when a specific action fits.
- Show progress after activation and prevent accidental duplicate submission.
- Do not use color alone to distinguish destructive actions.
- Put “CANCEL” before or after the main action consistently across the product.
- A disabled action should not be used as the only explanation of what is missing.
- Icon-only buttons have no visible text to transform, but still require a sentence-case accessible name describing the action.

### Component color rules

Being part of the UC San Diego brand palette does not mean a color should be exposed as an option on every component.

Components should provide only color variants appropriate to their function.

#### Buttons

- Blue
- Navy when explicitly required
- Yellow for approved high-emphasis CTA treatments

##### Button hover colors
If the primary button is blue or yellow, then the hover background color should be navy, and the text should be white.

Example:

.btn-primary:hover {
    background-color: var(--component-btn-navy);
    color: var(--component-btn-label-white);
}

If the primary background behind the button is navy, then the hover background color should be turquoise, and the text should be navy.

Example:
.btn-primary:hover {
    background-color: var(--component-btn-turquoise);
    color: var(--component-btn-label-primary);
}

### 8.2 Links

- Use links for navigation and buttons for actions.
- Link text must describe the destination out of context.
- Avoid “click here” and bare URLs in body copy.
- External destinations should be disclosed when leaving the application would be unexpected.

### 8.3 Form controls

- Every input must have a persistent visible label.
- Put essential instructions before the field and concise help near it.
- Mark optional fields as “Optional” when most fields are required; otherwise state the required convention at the start of the form.
- Do not use placeholder text as the label or as essential instructions.
- Use native controls where they meet the need.
- Match the control type to the data and expected input method.
- Preserve user input after validation errors.

Required states:

- default;
- hover when relevant;
- keyboard focus;
- filled/selected;
- disabled;
- read-only;
- error;
- warning when distinct from error; and
- loading for async controls.

### 8.4 Validation

- Validate at a moment that helps the user; avoid scolding while they are still typing.
- Place field errors beside the field and provide an error summary at the start of a submitted form with multiple errors.
- Error text must explain the problem and how to fix it.
- Move focus to the error summary after an unsuccessful submission.
- Do not clear correct values because another field is invalid.

### 8.5 Tables and data grids

Use a table when users need to compare values across records. Use a list or cards when each record has different content or only one or two comparable attributes.

Tables must define:

- column priority;
- sorting and default sort;
- filtering and applied-filter visibility;
- search scope;
- pagination or progressive loading;
- row and bulk actions;
- empty, loading, partial, and error states;
- responsive behavior; and
- keyboard and screen-reader behavior.

Rules:

- Left-align text and normally right-align comparable numbers.
- Keep headers visible for long tables when technically appropriate.
- Do not encode status with color alone.
- Keep destructive row actions out of the highest-emphasis position.
- Preserve filters and sort when users open a record and return.
- Never force essential record actions to exist only on hover.

### 8.6 Cards

- Use cards for a discrete object, summary, or actionable group.
- Do not place every page section in a card.
- A card should have one clear subject and hierarchy.
- If the whole card is interactive, ensure nested actions remain unambiguous and keyboard accessible.

### 8.7 Tabs

- Use tabs for peer views of the same object or context.
- Do not use tabs as the primary navigation for unrelated destinations.
- Keep tab labels short and stable.
- Preserve the selected tab in the URL when direct linking or browser navigation matters.
- On narrow screens, use a documented overflow treatment rather than shrinking labels until unreadable.

### 8.8 Dialogs

- Use a dialog for a focused decision or short task that should not become a page.
- The title must name the decision or task.
- Initial focus, focus containment, Escape behavior, close behavior, and focus return must be specified.
- Do not use a dialog for long, multi-step, or reference-heavy forms.
- Require explicit confirmation for consequential destructive actions.

### 8.9 Status badges

- Use a short noun or adjective such as “Draft,” “Approved,” or “Past due.”
- Status labels must use the same vocabulary everywhere.
- Pair color with readable text.
- Do not make a badge look interactive unless it is interactive.

### 8.10 Alerts and notifications

| Pattern | Use |
| --- | --- |
| Inline message | Guidance or feedback tied to a field or section |
| Page alert | Important state affecting the whole page |
| Toast | Brief confirmation that does not require immediate action |
| Banner | Rare, persistent system-wide or product-wide condition |

Errors requiring action must not disappear automatically. Success toasts may time out if the same result is also apparent in the page.

---

## 9. Forms and workflows

### 9.1 Form layout

- Use one column by default.
- Use multiple columns only for short, strongly related fields such as city/state/postal code or start/end dates.
- Group fields under descriptive headings.
- Put labels above controls unless a specialized pattern has been tested.
- Keep the primary action near the end of the content it submits.
- For long forms, provide progress, section navigation, save status, or draft behavior as appropriate.

### 9.2 Saving

Each workflow must explicitly choose one model:

- explicit **SAVE**;
- save draft plus final submission;
- autosave with visible saved/saving/error status; or
- immediate update for small reversible settings.

Do not mix models without explaining the transition. Never imply that data is saved before confirmation from the system.

### 9.3 Destructive actions

- Use specific labels such as “DELETE REPORT,” not “CONFIRM.”
- Explain the effect, scope, and recoverability.
- Add confirmation when the action is difficult to reverse or has broad consequences.
- For highly consequential actions, require a stronger confirmation pattern proportionate to the risk.
- After completion, explain what happened and whether recovery is possible.

### 9.4 Multi-step workflows

- Show the user's current step and total progress when the sequence is fixed.
- Allow backward navigation without losing valid information.
- Summarize consequential inputs before final submission.
- Distinguish “SAVE AND EXIT” from “CONTINUE.”
- Do not use a wizard when users need to compare information across steps continuously.

---

## 10. System states

Every data-dependent page and component must design these states before implementation:

| State | Requirement |
| --- | --- |
| Initial loading | Preserve layout where possible; announce meaningful async status |
| Background loading | Keep usable content visible and identify what is updating |
| Empty—first use | Explain the purpose and offer a relevant first action |
| Empty—no results | Preserve filters and offer a way to broaden or clear them |
| Success | Confirm the completed action and its effect |
| Warning | Explain the risk and available choices |
| Error—recoverable | Explain what happened and provide a retry or correction path |
| Error—blocking | Explain what the user can do next and how to get help |
| Partial data | Identify missing or stale data without presenting it as complete |
| No permission | Explain the limitation without exposing restricted information |
| Session timeout | Warn before timeout when possible and preserve recoverable work |
| Offline/interrupted | Protect entered data and explain reconnection behavior |

Loading placeholders should resemble the eventual structure and must not create distracting animation.

---

## 11. Accessibility standard

The product must meet **WCAG 2.2 Level AA** for the application canvas and must not reduce the accessibility of Decorator chrome.

Minimum requirements:

- complete keyboard access in a logical order;
- a clearly visible focus indicator;
- semantic headings, landmarks, lists, tables, and form relationships;
- accessible names for all controls;
- sufficient text and non-text contrast;
- no information conveyed by color, position, shape, sound, or motion alone;
- reflow and usability at 400% browser zoom where applicable;
- touch targets sized and spaced to reduce accidental activation;
- status and error updates announced appropriately;
- captions, transcripts, and alternatives for media;
- reduced-motion support; and
- instructions that do not depend only on sensory characteristics.

### 11.1 Definition of done for accessibility

A feature is not complete until it has:

- been reviewed in all documented states;
- passed keyboard-only use;
- been checked at 200% and 400% zoom;
- been checked for contrast;
- been tested with at least one supported screen reader for critical workflows; and
- resolved all critical and serious automated accessibility findings, with manual review because automation is not sufficient.

---

## 12. Content design

### 12.1 Voice

Use a calm, direct, respectful voice. Assume users are capable but may be unfamiliar with institutional terminology or the current process.

### 12.2 Writing rules

- Lead with what the user needs to know or do.
- Use familiar words and short sentences.
- Use sentence case for prose, headings, navigation, tabs, field labels, and system messages. Visible textual button labels are the intentional exception and render in uppercase.
- Use the same term for the same concept.
- Avoid internal acronyms; define unavoidable ones on first use.
- State dates unambiguously, including the year when relevant.
- Include time zone when deadlines or event times may be interpreted across zones.
- Make error messages specific, constructive, and free of blame.
- Do not use “successfully” when the confirmed result is already clear.

### 12.3 Labels and help

- Navigation labels name destinations.
- Button labels name actions.
- Headings describe the content that follows.
- Help text answers a likely question and should not repeat the label.
- Tooltips provide supplementary detail, never essential instructions.

---

## 13. Roles, permissions, and privacy

- Design for the least-privileged relevant role, not only administrators.
- Do not show a control that will always fail for the current user.
- When a hidden control would create confusion, explain the restriction in context without revealing sensitive information.
- Clearly identify when users are acting on behalf of another person or organizational unit.
- Confirm changes with broad scope, such as updates affecting many records or users.
- Mask sensitive values by default and provide deliberate reveal behavior where appropriate.
- Do not expose private information in URLs, page titles, analytics labels, notifications, or error messages.

---

## 14. Design patterns for common enterprise pages

### 14.1 Dashboard

A dashboard should answer a small set of recurring questions. It must not become a collection of unrelated cards.

Recommended order:

1. page title and time/data context;
2. urgent tasks or exceptions;
3. key summary measures;
4. recent or assigned work;
5. supporting trends or shortcuts.

Every metric must define its time range, source or scope, update time, and link to detail when available.

### 14.2 Work queue

Include:

- clear scope and record count;
- search and filters;
- visible applied filters;
- sortable priority columns;
- ownership or assignment;
- status and age;
- row and bulk actions when appropriate; and
- preserved state when returning from a record.

### 14.3 Record detail

Recommended order:

1. record identity and status;
2. primary actions;
3. summary facts;
4. current task or next step;
5. detailed sections;
6. history, audit trail, or related records.

Separate editable and read-only states clearly. Do not make every field look editable when the page is in view mode.

### 14.4 Create or edit form

Use a descriptive title, short orientation, logically grouped fields, local help, clear saving behavior, and a predictable action area. For long workflows, support draft recovery and return visits.

### 14.5 Administration

Administration pages require stronger scope cues, explicit consequences, searchable records, auditability, and cautious destructive actions. Clearly distinguish configuration changes from content changes.

---

## 15. Anti-patterns

Do not:

- modify or imitate Decorator chrome;
- place application navigation inside the Decorator navigation;
- use global CSS selectors such as unscoped `header`, `nav`, `.container`, `.dropdown`, or `.form-control`;
- use more than one primary action in the same decision context;
- rely on hover to reveal essential information or actions;
- use placeholder text as a form label;
- place long workflows in dialogs;
- use cards as the default container for every section;
- invent a new status label when an existing one has the same meaning;
- show a blank area while data is loading;
- use a disabled button as the only form guidance;
- clear entered data after a recoverable error;
- use color alone for status or validation; or
- design entirely around the ideal, expected scenario where everything works correctly, and no errors occur.

---

## Appendix A: Instructions for coding agents

When generating or editing application UI:

1. Treat Decorator header, navigation, search, mobile drawer, footer, and associated runtime as protected external code.
2. Make changes only inside the declared application canvas unless the user explicitly provides an approved Decorator change.
3. Read the installed Decorator template and Decorator Kit instructions before integrating the shell. Do not infer canonical markup from the live browser DOM.
4. Inherit Decorator foundations when they already satisfy the requirement; do not duplicate them in application code or tokens.
5. Apply only the intentional overrides and application extensions listed in Section 2.3.
6. Scope application CSS and JavaScript to the application root.
7. Do not target selectors found only in protected chrome.
8. Use semantic HTML and native controls before custom equivalents.
9. Implement every state specified in the design, including loading, empty, error, permission, and responsive states.
10. Do not invent brand values when approved tokens or Decorator values exist.
11. Flag a conflict rather than silently overriding this document or Decorator behavior.
12. Run the project's Decorator Kit integrity checks before considering the work complete.

## Appendix B: Feature specification template

Copy this section for each feature:

```md
# Feature: [Name]

## User goal
[What the user is trying to accomplish]

## Users and permissions
[Roles, capabilities, and restrictions]

## Entry points
[How users reach the feature]

## Primary flow
1. [Step]
2. [Step]
3. [Outcome]

## Alternate and failure paths
- [Path]

## Layout and responsive behavior
[Wide and narrow viewport behavior]

## Components
- [Component and variant]

## States
- Loading:
- Empty:
- Success:
- Warning:
- Error:
- No permission:
- Partial or stale data:

## Content rules
[Labels, helper text, validation, formatting]

## Accessibility annotations
[Focus order, names, announcements, keyboard behavior, contrast]

## Data and system assumptions
[Sources, latency, limits, update behavior]

## Acceptance criteria
- [ ] [Testable requirement]
```
