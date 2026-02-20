# Lab Report: AI Usage Experience

## Task

Create a simple static website using HTML + CSS with SCSS preprocessor, without JavaScript.

## How AI was used

- ChatGPT was used to generate the initial page content and text sections.
- ChatGPT was used to suggest semantic HTML structure and SCSS partial organization.
- AI image generators were considered for artwork references; this version uses available local poster images.

## What was generated with AI

- Base layout idea: header, hero section, cards, table, modal, and footer.
- SCSS architecture idea:
  - `abstracts` (variables, mixins)
  - `base` (reset, typography)
  - `layout` (header, footer)
  - `components` (buttons, cards, forms, tables, modal)
  - `pages` (home-level page styles)

## Manual adjustments

- Improved responsive behavior for mobile screens.
- Aligned all pages to one visual style.
- Ensured there is no JavaScript and all interactivity is CSS/HTML only (`:target` modal).
- Fixed stylesheet paths and UTF-8 text consistency.

## SCSS compilation demo

Compilation command used for demonstration:

```bash
sass scss/main.scss css/main.css
```

Watch mode command:

```bash
sass --watch scss/main.scss:css/main.css
```

## GitHub Pages publication

Project can be published as a static site via GitHub Pages using the `frontend` folder as the Pages source.
