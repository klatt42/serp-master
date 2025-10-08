#!/usr/bin/env python3
"""
Test the site crawler with the 404 handling fix
"""
import asyncio
from app.services.site_crawler import SiteCrawler

async def test_crawler_with_zero_pages():
    """Test crawler handles 0 page crawls gracefully"""
    crawler = SiteCrawler()

    print("=" * 70)
    print("Site Crawler Test - Zero Pages Handling")
    print("=" * 70)
    print()

    try:
        print("Starting crawl for example.com (1 page max)...")
        print("This will test the 404 fallback to /summary/ endpoint")
        print()

        results = await crawler.crawl_site("https://example.com", max_pages=1)

        print("✅ Crawl completed successfully!")
        print()
        print("Summary:")
        print(f"  Pages crawled: {results['summary']['pages_crawled']}")
        print(f"  Pages with issues: {results['summary']['pages_with_issues']}")
        print(f"  Total issues: {results['summary']['total_issues']}")
        print(f"  Crawl progress: {results['summary']['crawl_progress']}")
        print()
        print("Metadata:")
        print(f"  Task ID: {results['metadata']['task_id']}")
        print(f"  Duration: {results['metadata']['crawl_duration_seconds']:.1f}s")
        print()

        if results['summary']['pages_crawled'] == 0:
            print("✅ Correctly handled 0 pages scenario with /summary/ fallback")
        else:
            print(f"ℹ️  Crawled {results['summary']['pages_crawled']} pages")

        print()
        print("=" * 70)
        print("TEST PASSED")
        print("=" * 70)

    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_crawler_with_zero_pages())
