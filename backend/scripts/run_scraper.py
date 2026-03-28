#!/usr/bin/env python3
"""CLI script to run the scraper directly."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.scraper import scrape_url
from app.config import get_settings

async def main():
    settings = get_settings()
    
    # Default CTPB competitions to scrape
    competitions = [
        "https://ctpb.euskalpilota.fr/resultats.php?InSel=&InCompet=20260102&InSpec=11",
        "https://ctpb.euskalpilota.fr/resultats.php?InSel=&InCompet=20260104&InSpec=11",
    ]
    
    print(f"🚀 Starting scraper for {len(competitions)} competitions...")
    
    for url in competitions:
        print(f"\n📊 Scraping: {url[:80]}...")
        result = await scrape_url(url)
        print(f"   Status: {result.status}")
        if result.status == "success":
            print(f"   ✅ Success!")
            print(f"   Raw items: {len(result.raw_items) if hasattr(result, 'raw_items') else 'N/A'}")
            print(f"   Raw content length: {len(result.raw_content) if hasattr(result, 'raw_content') else 'N/A'}")
            # Print first 500 chars of raw content
            if hasattr(result, 'raw_content') and result.raw_content:
                print(f"   Preview: {result.raw_content[:500]}...")
        elif result.errors:
            print(f"   ❌ Errors: {result.errors}")
    
    print("\n✅ Scraper finished!")

if __name__ == "__main__":
    asyncio.run(main())
