# Pelota API

Node.js API for Pelota. Owns the PostgreSQL database and proxies scraping requests to the FastAPI scraper service. Called by the Angular frontend.

## Requirements

- Node.js 18+
- PostgreSQL 15+
- npm or yarn

## Setup

```bash
npm install
```

Copy `.env.example` to `.env` and set your values:

```bash
cp .env.example .env
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PELOTA_POSTGRES_DATABASE_URL` | PostgreSQL connection string | required |
| `PELOTA_FASTAPI_SCRAPER_SERVICE_URL` | FastAPI scraper base URL | `http://localhost:8001` |
| `PELOTA_API_SERVER_PORT` | HTTP server port | `3000` |

## Database

Generate Prisma client:

```bash
npm run db:generate
```

Run migrations (creates tables):

```bash
npm run db:migrate
```

For production:

```bash
npm run db:migrate:deploy
```

Optional: open Prisma Studio to inspect data:

```bash
npm run db:studio
```

## Travailler en local

1. Install dependencies: `npm install`
2. Configure `.env` with `PELOTA_POSTGRES_DATABASE_URL` and `PELOTA_FASTAPI_SCRAPER_SERVICE_URL` (e.g. `http://localhost:8001`).
3. Start PostgreSQL, then: `npm run db:generate`, `npm run db:migrate`.
4. Run the FastAPI scraper (backend) on port 8001 so scrape endpoints work.
5. Start the API: `npm run dev` (listens on port 3000).

**Pour tout lancer en local (API + backend + frontend + PostgreSQL)** : à la racine du monorepo, exécuter `docker compose up`.

## Tests

```bash
npm test
```

(Placeholder: add unit/integration tests as needed.)

## Run

Development (with watch):

```bash
npm run dev
```

Production:

```bash
npm run build
npm run start
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | API info |
| GET | `/health` | Health check |
| POST | `/scrape/trigger` | Trigger scrape via FastAPI, persist results |
| POST | `/scrape/batch` | Batch scrape multiple URLs |
| GET | `/scrape/ctpb/filters` | CTPB filter options (proxy) |
| POST | `/scrape/ctpb/filters/sync` | Sync CTPB filters to DB |
| POST | `/scrape/ctpb/resultats` | CTPB results with filters (proxy) |
| POST | `/scrape/ctpb/pipeline` | CTPB full pipeline (combinations + scrape + persist) |

### POST /scrape/trigger

Request body:

```json
{
  "url": "https://example.com/data",
  "sourceId": "optional-source-uuid"
}
```

If `sourceId` matches an existing `Source` record, the scrape result is stored in `ScrapingJobRun`.

### POST /scrape/batch

Request body:

```json
{
  "urls": [
    { "url": "https://example.com/1", "source_id": "optional" },
    { "url": "https://example.com/2" }
  ]
}
```

## Déploiement production (CapRover / Docker)

Build the image:

```bash
docker build -t pelota-api .
```

Run with environment variables:

- `PELOTA_POSTGRES_DATABASE_URL` — PostgreSQL connection string.
- `PELOTA_FASTAPI_SCRAPER_SERVICE_URL` — FastAPI scraper service URL (e.g. internal hostname in Docker/CapRover).
- `PELOTA_API_SERVER_PORT` — optional, default 3000.

Health check: `GET /health` should return `{ "status": "ok" }`.

On CapRover: deploy the image and set the env vars; ensure the app can reach PostgreSQL and the scraper service.

## Architecture

```
Angular → Node.js API (this repo) → FastAPI Scraper
                ↓
           PostgreSQL
```
