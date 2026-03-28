#!/usr/bin/env python3
"""CLI script to run the scraper directly with debug output."""

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
        "https://ctpb.euskalpilota.fr/resultats.php?InSel=&InCompet=20260102&InSpec=11&InVille=&InClub=&InDate=&InDatef=&InCat=0&InPhase=0&InVoir=Voir+les+r%C3%A9sultats",
        "https://ctpb.euskalpilota.fr/resultats.php?InSel=&InCompet=20260104&InSpec=11&InVille=&InClub=&InDate=&InDatef=&InCat=0&InPhase=0&InVoir=Voir+les+r%C3%A9sultats",
    ]
    
    print(f"🚀 Starting scraper for {len(competitions)} competitions...")
    
    for url in competitions:
        print(f"\n📊 Scraping: {url[:100]}...")
        result = await scrape_url(url)
        print(f"   Status: {result.status}")
        if result.status == "success":
            print(f"   ✅ Success!")
            # Check what attributes result has
            print(f"   Result type: {type(result)}")
            print(f"   Result attributes: {dir(result)}")
            # Try to access raw_content safely
            if hasattr(result, 'raw_content'):
                content = result.raw_content
                print(f"   Raw content type: {type(content)}")
                print(f"   Raw content length: {len(content) if content else 0}")
                if content and len(content) > 0:
                    preview = content[:500] if isinstance(content, str) else str(content)[:500]
                    print(f"   Preview: {preview}...")
            else:
                print(f"   No raw_content attribute")
        elif result.errors:
            print(f"   ❌ Errors: {result.errors}")
    
    print("\n✅ Scraper finished!")

if __name__ == "__main__":
    asyncio.run(main())
