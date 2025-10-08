#!/usr/bin/env python3
"""
Quick test to verify the crawl_status parsing fix works
"""
import asyncio
from app.services.site_crawler import SiteCrawler

async def test_wikipedia():
    """Test Wikipedia crawl with fixed parsing"""
    crawler = SiteCrawler()

    print("Testing Wikipedia crawl with crawl_status fix...")
    print()

    try:
        results = await crawler.crawl_site("https://en.wikipedia.org", max_pages=10)

        print("✅ Crawl completed!")
        print()
        print(f"Pages crawled: {results['summary']['pages_crawled']}")
        print(f"Pages with issues: {results['summary']['pages_with_issues']}")
        print(f"Total issues: {results['summary']['total_issues']}")
        print(f"Duration: {results['metadata']['crawl_duration_seconds']:.1f}s")

        if results['summary']['pages_crawled'] > 0:
            print()
            print(f"✅ SUCCESS! Crawled {results['summary']['pages_crawled']} pages!")
        else:
            print()
            print("⚠️  Still getting 0 pages - need to investigate further")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_wikipedia())
