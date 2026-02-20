# Frontend Lab 1 (Static HTML + SCSS)

This frontend is a static website for Lab 1:
- HTML for page structure
- SCSS for styling
- Compiled CSS output
- No JavaScript

## Project structure

- `index.html`, `movies.html`, `movie-details.html`, `login.html`, `user-profile.html`
- `scss/main.scss` and partials in `scss/**`
- Compiled file: `css/main.css`
- Lab report: `LAB_REPORT.md`

## Compile SCSS to CSS

If Sass is installed:

```bash
sass scss/main.scss css/main.css
```

Watch mode:

```bash
sass --watch scss/main.scss:css/main.css
```

## GitHub Pages

1. Push repository to GitHub.
2. Open repository settings -> Pages.
3. Set source to deploy from branch (`main`) and folder (`/frontend` or `/root` depending on repo layout).
4. Save and open the generated site URL.
