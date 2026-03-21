import logging
import sys

from fastapi import FastAPI

from .routers import scraping

# Ensure pelota.scraping logs appear in the console (uvicorn terminal)
_scrape_logger = logging.getLogger("pelota.scraping")
_scrape_logger.setLevel(logging.DEBUG)
if not _scrape_logger.handlers:
    _handler = logging.StreamHandler(sys.stderr)
    _handler.setLevel(logging.DEBUG)
    _handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
    )
    _scrape_logger.addHandler(_handler)
_scrape_logger.propagate = False

app = FastAPI(title="Pelota Scraping Service")
app.include_router(scraping.router, prefix="/scrape", tags=["scraping"])


@app.get("/")
async def root():
    return {"message": "Pelota Scraping Service"}