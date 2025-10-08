#!/usr/bin/env python3
"""
Test DataForSEO task lifecycle to diagnose 404 issues
"""
import asyncio
import json
from app.services.dataforseo_client import DataForSEOClient

async def test_task_lifecycle():
    """Test complete task lifecycle with detailed logging"""
    client = DataForSEOClient()

    print("=" * 60)
    print("DataForSEO Task Lifecycle Test")
    print("=" * 60)
    print()

    # Step 1: Create task
    print("Step 1: Creating task for example.com...")
    target_url = "https://example.com"
    max_pages = 5

    task_response = await client.task_post(target_url, max_pages)
    print(f"Response: {json.dumps(task_response, indent=2)}")
    print()

    if not task_response.get("tasks") or len(task_response["tasks"]) == 0:
        print("❌ No tasks in response")
        return

    task_data = task_response["tasks"][0]
    task_id = task_data.get("id")
    status_code = task_data.get("status_code")
    status_message = task_data.get("status_message")

    print(f"Task ID: {task_id}")
    print(f"Status Code: {status_code}")
    print(f"Status Message: {status_message}")
    print()

    if status_code != 20100:
        print(f"❌ Task creation failed with status {status_code}")
        return

    # Step 2: Try to get task immediately
    print("Step 2: Trying to get task immediately after creation...")
    try:
        result = await client.task_get(task_id)
        print(f"✅ Success!")
        print(f"Response: {json.dumps(result, indent=2)}")

        if result.get("tasks") and len(result["tasks"]) > 0:
            task = result["tasks"][0]
            if task.get("result") and len(task["result"]) > 0:
                crawl_result = task["result"][0]
                print(f"\nCrawl Progress: {crawl_result.get('crawl_progress')}")
                print(f"Pages Crawled: {crawl_result.get('pages_crawled')}")
                print(f"Pages in Queue: {crawl_result.get('pages_in_queue')}")
    except Exception as e:
        print(f"❌ Failed: {e}")
    print()

    # Step 3: Check tasks_ready
    print("Step 3: Checking tasks_ready...")
    try:
        ready = await client.tasks_ready()
        # FIXED: Use 'result' array, not 'tasks'
        print(f"Ready tasks count: {len(ready.get('result', []))}")

        if ready.get('result'):
            for i, task in enumerate(ready['result'][:3], 1):
                print(f"\n  Task #{i}:")
                print(f"    ID: {task.get('id')}")
                print(f"    Target: {task.get('target')}")
                print(f"    Date Posted: {task.get('date_posted')}")

                # Check if this is our task
                if task.get('id') == task_id:
                    print(f"    ✅ Found our task in ready list!")
    except Exception as e:
        print(f"❌ Failed: {e}")
    print()

    # Step 4: Poll for completion
    print("Step 4: Polling for task completion (max 60 seconds)...")
    start_time = asyncio.get_event_loop().time()
    poll_count = 0

    while True:
        elapsed = asyncio.get_event_loop().time() - start_time
        if elapsed > 60:
            print("⏱️ Timeout after 60 seconds")
            break

        poll_count += 1
        print(f"\nPoll #{poll_count} (elapsed: {elapsed:.1f}s)")

        # Try task_get
        try:
            result = await client.task_get(task_id)

            if result.get("tasks") and len(result["tasks"]) > 0:
                task = result["tasks"][0]

                if task.get("result") and len(task["result"]) > 0:
                    crawl_result = task["result"][0]
                    progress = crawl_result.get("crawl_progress", "unknown")
                    pages_crawled = crawl_result.get("pages_crawled", 0)
                    pages_in_queue = crawl_result.get("pages_in_queue", 0)

                    print(f"  Progress: {progress}")
                    print(f"  Pages crawled: {pages_crawled}")
                    print(f"  Pages in queue: {pages_in_queue}")

                    if progress == "finished":
                        print("\n✅ Task completed!")
                        print(f"\nFinal results:")
                        print(f"  Total pages: {pages_crawled}")
                        print(f"  Items: {len(crawl_result.get('items', []))}")
                        break
                else:
                    print("  No results yet, task still being processed")
            else:
                print("  No task data yet")

        except Exception as e:
            print(f"  ❌ task_get failed: {e}")

        await asyncio.sleep(5)

    print()
    print("=" * 60)
    print("Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_task_lifecycle())
