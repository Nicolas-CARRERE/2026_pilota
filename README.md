# Pilota

Basque Pelota results and statistics tracking application.

## Project Structure

- `frontend/` — Angular 18+ application
- `backend/` — API server
- `api/` — Additional API services

## Development

```bash
cd frontend
npm install
npm run dev
```

## Accessibility Guidelines

### Images and Alt Text

All images must include descriptive alt text:

```html
<img [src]="imageUrl" [alt]="imageDescription" />
```

**Rules:**
- Decorative images: use `alt=""` (empty string)
- Informative images: describe the content and purpose
- Avoid "image of" or "picture of" prefixes
- Keep alt text concise but meaningful

### ARIA Labels

- All interactive elements must have accessible names
- Use `aria-label` for icon-only buttons
- Use `aria-describedby` for additional context
- Use `role` attributes where semantic HTML is insufficient

### Focus States

- All interactive elements have visible focus indicators
- Skip link provided for keyboard navigation
- Focus order follows visual layout

### Color Contrast

- Text meets WCAG AA contrast requirements (4.5:1 for normal text)
- Interactive elements have distinct hover/focus states

## UI/UX Improvements Log

See `UI-UX-AUDIT-REPORT.md` for the full audit and implementation status.
