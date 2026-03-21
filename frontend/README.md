# Pelota Frontend

Angular application for displaying game results, filters, player analytics, and next scheduled matches. Consumes the Pelota Node API. Theme: Basque flag colors (green, red, white).

## Requirements

- Node.js 18+
- npm or yarn

## Setup

```bash
npm install
```

Configure the API base URL in `src/environments/environment.ts`: `apiUrl` must point to the Node.js API (default **port 3000**, or whatever `PELOTA_API_SERVER_PORT` is set to).

## Development

1. Install dependencies: `npm install`.
2. Ensure the Pelota API is running (e.g. port 3000) and optionally the backend scraper (8001).
3. Run: `ng serve` (or `npm start`). Open http://localhost:4200.

**Full stack locally**: at repo root, run `docker compose up`.

## Build production

```bash
ng build --configuration production
```

Output is in `dist/` (e.g. `dist/pelota-temp/browser`).

## Deployment (Docker / CapRover)

The Dockerfile builds the Angular app and serves it with nginx. Set the API URL at build time (e.g. `ARG API_URL`) or at runtime if configured. Health: nginx responds on port 80 and `/health`.
