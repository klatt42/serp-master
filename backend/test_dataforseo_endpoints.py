#!/usr/bin/env python3
"""
Test script to understand DataForSEO endpoint behavior during crawl lifecycle
"""
import asyncio
import sys
from app.services.dataforseo_client import DataForSEOClient

async def test_endpoint_availability():
    """Test when different endpoints become available"""
    client = DataForSEOClient()

    print("=" * 70)
    print("DataForSEO Endpoint Availability Test")
    print("=" * 70)
    print()

    # Create a small, fast crawl task
    target = "https://example.com"
    max_pages = 1

    print(f"Creating crawl task for {target} (max {max_pages} pages)...")
    try:
        response = await client.task_post(target, max_pages)
        task_id = response["tasks"][0]["id"]
        print(f"✅ Task created: {task_id}")
        print()
    except Exception as e:
        print(f"❌ Failed to create task: {e}")
        return

    # Test both endpoints immediately
    print("Testing endpoint availability immediately after task creation:")
    print()

    # Test 1: /summary/ endpoint
    print("1. Testing /summary/ endpoint...")
    try:
        result = await client.task_status(task_id)
        print(f"   ✅ /summary/ AVAILABLE")
        if result.get("tasks") and result["tasks"][0].get("result"):
            crawl_result = result["tasks"][0]["result"][0]
            print(f"   Progress: {crawl_result.get('crawl_progress')}")
            print(f"   Pages crawled: {crawl_result.get('pages_crawled', 0)}")
            print(f"   Pages in queue: {crawl_result.get('pages_in_queue', 0)}")
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg:
            print(f"   ❌ /summary/ NOT AVAILABLE (404)")
        elif "TASK_IN_QUEUE" in error_msg:
            print(f"   ⏳ /summary/ says: TASK IN QUEUE")
        elif "TASK_IN_PROGRESS" in error_msg:
            print(f"   ⏳ /summary/ says: TASK IN PROGRESS")
        else:
            print(f"   ❌ /summary/ ERROR: {error_msg[:100]}")

    print()

    # Test 2: /pages/ endpoint
    print("2. Testing /pages/ endpoint...")
    try:
        result = await client.task_get(task_id)
        print(f"   ✅ /pages/ AVAILABLE")
        if result.get("tasks") and result["tasks"][0].get("result"):
            crawl_result = result["tasks"][0]["result"][0]
            print(f"   Progress: {crawl_result.get('crawl_progress')}")
            print(f"   Pages crawled: {crawl_result.get('pages_crawled', 0)}")
            print(f"   Items: {len(crawl_result.get('items', []))}")
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg:
            print(f"   ❌ /pages/ NOT AVAILABLE (404)")
        elif "TASK_IN_QUEUE" in error_msg:
            print(f"   ⏳ /pages/ says: TASK IN QUEUE")
        elif "TASK_IN_PROGRESS" in error_msg:
            print(f"   ⏳ /pages/ says: TASK IN PROGRESS")
        else:
            print(f"   ❌ /pages/ ERROR: {error_msg[:100]}")

    print()
    print("=" * 70)
    print("Polling for 60 seconds to see when endpoints become available...")
    print("=" * 70)
    print()

    # Poll for 60 seconds
    for i in range(6):
        await asyncio.sleep(10)

        print(f"Poll #{i+1} (after {(i+1)*10}s):")

        # Try summary
        try:
            result = await client.task_status(task_id)
            if result.get("tasks") and result["tasks"][0].get("result"):
                crawl_result = result["tasks"][0]["result"][0]
                progress = crawl_result.get('crawl_progress')
                pages_done = crawl_result.get('pages_crawled', 0)
                pages_queued = crawl_result.get('pages_in_queue', 0)
                print(f"  /summary/ ✅ Progress: {progress}, Done: {pages_done}, Queue: {pages_queued}")

                if progress == "finished":
                    print(f"  Crawl finished! Testing /pages/ endpoint...")
                    try:
                        pages_result = await client.task_get(task_id)
                        if pages_result.get("tasks") and pages_result["tasks"][0].get("result"):
                            items_count = len(pages_result["tasks"][0]["result"][0].get("items", []))
                            print(f"  /pages/ ✅ Retrieved {items_count} page items")
                        break
                    except Exception as pages_error:
                        print(f"  /pages/ ❌ Still not available: {str(pages_error)[:50]}")
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg:
                print(f"  /summary/ ❌ Still 404")
            elif "TASK_IN_QUEUE" in error_msg:
                print(f"  /summary/ ⏳ Task in queue")
            elif "TASK_IN_PROGRESS" in error_msg:
                print(f"  /summary/ ⏳ Task in progress")
            else:
                print(f"  /summary/ ❌ Error: {error_msg[:50]}")

        print()

    print("=" * 70)
    print("Test Complete")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_endpoint_availability())
