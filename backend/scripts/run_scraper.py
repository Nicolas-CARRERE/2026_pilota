#!/usr/bin/env python3
"""CLI script to run the scraper directly with debug output."""

import argparse
import asyncio
import json
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

# Fixture directory for testing
FIXTURES_DIR = Path(__file__).parent.parent / "tests" / "fixtures" / "ctpb"

def load_fixtures() -> dict:
    """Load saved fixtures for testing."""
    games_path = FIXTURES_DIR / "games.json"
    if not games_path.exists():
        raise FileNotFoundError(f"Fixtures not found: {games_path}")
    
    with open(games_path, "r", encoding="utf-8") as f:
        return json.load(f)

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
    parser.add_argument(
        "--use-fixtures",
        action="store_true",
        help="Use saved fixtures instead of live scraping (for testing)",
    )
    parser.add_argument(
        "--update-fixtures",
        action="store_true",
        help="Update fixtures from live scrape, then exit",
    )
    args = parser.parse_args()

    settings = get_settings()
    print(f"🔧 Database URL: {settings.database_url[:50]}...")
    
    # Handle fixture update mode
    if args.update_fixtures:
        print("🔄 Updating fixtures from live scrape...")
        from scripts.save_fixtures import save_ctpb_fixtures
        competitions = args.url or [
            "https://ctpb.euskalpilota.fr/resultats.php?InSel=&InCompet=20260102&InSpec=11&InVille=&InClub=&InDate=&InDatef=&InCat=0&InPhase=0&InVoir=Voir+les+r%C3%A9sultats",
        ]
        result = await save_ctpb_fixtures(competitions[0])
        if result.get("status") == "success":
            print(f"✅ Fixtures updated: {result.get('games_count')} games, {result.get('test_cases_count')} test cases")
            return
        else:
            print(f"❌ Fixture update failed: {result}")
            return
    
    # Handle fixture-only mode (no live scraping)
    if args.use_fixtures:
        print("📁 Using saved fixtures (no live scraping)...")
        try:
            fixture_data = load_fixtures()
            games = fixture_data.get("games", [])
            print(f"   📊 Loaded {len(games)} games from fixtures")
            
            total_games = len(games)
            total_competitions = set()
            
            # Extract competition info
            for game in games:
                if "discipline_context" in game:
                    total_competitions.add(game["discipline_context"])
            
            if args.ingest and games:
                print(f"   📦 Ingesting {len(games)} games from fixtures...")
                from app.services.ingestion_service import ingest_scraped_games
                ingest_result = await ingest_scraped_games(games)
                print(f"      - Competitions created: {ingest_result.get('competitions_created', 0)}")
                print(f"      - Games created: {ingest_result.get('games_created', 0)}")
                print(f"      - Games updated: {ingest_result.get('games_updated', 0)}")
            
            print(f"\n✅ Fixture test complete!")
            print(f"   Total games: {total_games}")
            print(f"   Total competitions: {len(total_competitions)}")
            return
        except FileNotFoundError as e:
            print(f"   ❌ {e}")
            print(f"   💡 Run with --update-fixtures first to create fixtures")
            return
    
    # Default: live scraping mode
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
