#!/usr/bin/env python3
"""CLI script to run the scraper directly with debug output."""

import argparse
import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from backend directory
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)
print(f"📄 Loaded .env from: {env_path}")

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.scraper import scrape_url
from app.config import get_settings

async def main():
    parser = argparse.ArgumentParser(description="Run CTPB scraper")
    parser.add_argument(
        "--ingest",
        action="store_true",
        help="Ingest scraped games into database after scraping",
    )
    parser.add_argument(
        "--url",
        type=str,
        action="append",
        help="URL(s) to scrape (can be specified multiple times)",
    )
    args = parser.parse_args()

    settings = get_settings()
    print(f"🔧 Database URL: {settings.database_url[:50]}...")
    
    # Default CTPB competitions to scrape
    competitions = args.url or [
        "https://ctpb.euskalpilota.fr/resultats.php?InSel=&InCompet=20260102&InSpec=11&InVille=&InClub=&InDate=&InDatef=&InCat=0&InPhase=0&InVoir=Voir+les+r%C3%A9sultats",
        "https://ctpb.euskalpilota.fr/resultats.php?InSel=&InCompet=20260104&InSpec=11&InVille=&InClub=&InDate=&InDatef=&InCat=0&InPhase=0&InVoir=Voir+les+r%C3%A9sultats",
    ]
    
    print(f"🚀 Starting scraper for {len(competitions)} competitions...")
    if args.ingest:
        print("📦 Will ingest results into database after scraping")
    
    total_games = 0
    total_competitions = set()
    
    for url in competitions:
        print(f"\n📊 Scraping: {url[:100]}...")
        result = await scrape_url(url)
        print(f"   Status: {result.status}")
        if result.status == "success":
            print(f"   ✅ Success!")
            if hasattr(result, 'raw_content') and result.raw_content:
                content = result.raw_content
                games = content.get("games", []) if isinstance(content, dict) else []
                games_count = len(games) if isinstance(games, list) else 0
                print(f"   Games found: {games_count}")
                total_games += games_count
                
                # Extract competition info from discipline_context
                if isinstance(games, list) and games:
                    for game in games:
                        if "discipline_context" in game:
                            total_competitions.add(game["discipline_context"])
                
                if args.ingest and games:
                    print(f"   📦 Ingesting {games_count} games...")
                    from app.services.ingestion_service import ingest_scraped_games
                    ingest_result = await ingest_scraped_games(games)
                    print(f"      - Competitions created: {ingest_result.get('competitions_created', 0)}")
                    print(f"      - Games created: {ingest_result.get('games_created', 0)}")
                    print(f"      - Games updated: {ingest_result.get('games_updated', 0)}")
        elif result.errors:
            print(f"   ❌ Errors: {result.errors}")
    
    print(f"\n✅ Scraper finished!")
    print(f"   Total games: {total_games}")
    print(f"   Total competitions: {len(total_competitions)}")
    if args.ingest:
        print(f"   All games ingested into database")

if __name__ == "__main__":
    asyncio.run(main())
