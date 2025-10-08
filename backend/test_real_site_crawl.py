#!/usr/bin/env python3
"""
Test crawling a real site to see what DataForSEO returns
"""
import asyncio
import json
from app.services.site_crawler import SiteCrawler

async def test_real_site():
    """Test crawler with a real, crawlable site"""
    crawler = SiteCrawler()

    print("=" * 70)
    print("Real Site Crawl Test")
    print("=" * 70)
    print()

    # Try a site known to allow crawlers
    test_url = "https://httpbin.org"  # Simple test site that allows crawling
    max_pages = 25

    try:
        print(f"Starting crawl for {test_url} (max {max_pages} pages)...")
        print()

        results = await crawler.crawl_site(test_url, max_pages=max_pages)

        print("✅ Crawl completed!")
        print()
        print("=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Pages crawled: {results['summary']['pages_crawled']}")
        print(f"Pages in queue: {results['summary']['pages_in_queue']}")
        print(f"Crawl progress: {results['summary']['crawl_progress']}")
        print(f"Pages with issues: {results['summary']['pages_with_issues']}")
        print(f"Total issues: {results['summary']['total_issues']}")
        print()

        print("=" * 70)
        print("PAGES DETAIL")
        print("=" * 70)
        for i, page in enumerate(results['pages'][:5], 1):
            print(f"\nPage {i}:")
            print(f"  URL: {page.get('url', 'N/A')}")
            print(f"  Status: {page.get('status_code', 'N/A')}")
            print(f"  Title: {page.get('meta', {}).get('title', 'N/A')[:60]}")
            print(f"  HTTPS: {page.get('is_https', False)}")
            print(f"  Issues: {len(page.get('issues', []))}")

        print()
        print("=" * 70)
        print("METADATA")
        print("=" * 70)
        print(f"Task ID: {results['metadata']['task_id']}")
        print(f"Target URL: {results['metadata']['target_url']}")
        print(f"Duration: {results['metadata']['crawl_duration_seconds']:.1f}s")
        print()

        if results['summary']['pages_crawled'] > 0:
            print("✅ SUCCESS: Got actual page data!")
            print()
            print("Sample raw data from first page:")
            if results.get('raw_result', {}).get('items'):
                first_item = results['raw_result']['items'][0]
                print(json.dumps({
                    'url': first_item.get('url'),
                    'status_code': first_item.get('status_code'),
                    'has_meta': bool(first_item.get('meta')),
                    'has_checks': bool(first_item.get('checks')),
                    'item_keys': list(first_item.keys())[:10]
                }, indent=2))
        else:
            print("⚠️  No pages crawled - site may block crawlers or have robots.txt restrictions")

        print()
        print("=" * 70)

    except Exception as e:
        print(f"❌ Crawl failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_real_site())
