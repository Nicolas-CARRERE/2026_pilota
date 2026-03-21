# Pelota Scraping Service

FastAPI service that scrapes URLs and returns structured payloads. Called by the Node.js API; stateless (no database).

## Requirements

- Python 3.9+
- pip or uv

## Setup

```bash
pip install -r requirements.txt
```

Or with uv:

```bash
uv pip install -r requirements.txt
```

Copy `.env.example` to `.env` and adjust if needed:

```bash
cp .env.example .env
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PELOTA_SCRAPER_HTTP_TIMEOUT_SECONDS` | HTTP request timeout in seconds | `30.0` |
| `PELOTA_SCRAPER_MAX_RETRY_ATTEMPTS` | Max retries on transient failures | `3` |
| `PELOTA_SCRAPER_RETRY_BACKOFF_FACTOR` | Exponential backoff factor for retries | `1.5` |

## Travailler en local

1. Install dependencies: `pip install -r requirements.txt` (or `uv pip install -r requirements.txt`).
2. Optional: copy `.env.example` to `.env` and adjust timeouts/retries.
3. Run: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8001`.

**Pour tout lancer en local (API + backend + frontend + PostgreSQL)** : à la racine du monorepo, exécuter `docker compose up`.

## Tests

```bash
pytest
```

(Placeholder: add tests in `tests/` as needed.)

## Run

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Service info |
| GET | `/scrape/health` | Health check |
| POST | `/scrape/run` | Scrape a single URL |
| POST | `/scrape/batch` | Batch scrape multiple URLs |
| GET | `/scrape/ctpb/filters` | CTPB resultats.php form filter options |
| POST | `/scrape/ctpb/resultats` | CTPB results with filters (competition, specialty, etc.) |
| POST | `/scrape/ctpb/pipeline` | CTPB pipeline: fetch filters, generate combinations, scrape sequentially |

### POST /scrape/run

Request body:

```json
{
  "url": "https://example.com/data",
  "source_id": "optional-uuid",
  "timeout_seconds": 30
}
```

Response: `{ status, raw_content?, total_items?, errors? }`

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

Response: `{ results: Array<ScrapeRunResponse> }`

### GET /scrape/ctpb/filters

Returns filter options from CTPB resultats.php (competitions, specialties, cities, clubs, categories, phases).

### POST /scrape/ctpb/resultats

Body: `{ competition?, specialty?, ville?, club?, date_from?, date_to?, category?, phase? }` — returns scraped games for the selected filters.

### POST /scrape/ctpb/pipeline

Body: `{ already_scraped_urls, max_combinations?, request_delay_seconds? }`. Generates pending (competition × specialty) combinations, scrapes each URL sequentially, returns results and counts.

## Error Handling

| Status | Code | Meaning |
|--------|------|---------|
| 200 | `success` | Scrape completed |
| 200 | `partial` | Some items scraped, some failed |
| 200 | `failed` | Network, timeout, 404, 429, or parse error |

## Déploiement production (CapRover / Docker)

Build the image:

```bash
docker build -t pelota-backend .
```

Run with environment variables for timeout and retries if needed. Health check: `GET /scrape/health`.

On CapRover: deploy the image and set env vars; the Node API will call this service by its internal URL.
