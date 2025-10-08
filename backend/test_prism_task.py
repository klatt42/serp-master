#!/usr/bin/env python3
"""
Test retrieving the specific prismspecialtiesdmv.com task mentioned by DataForSEO support
Task ID: 10061428-1060-0216-0000-989032d4e2c6
"""
import asyncio
import json
from app.services.dataforseo_client import DataForSEOClient

async def test_prism_task():
    """Test retrieving the prismspecialtiesdmv.com task"""
    client = DataForSEOClient()

    # Task ID mentioned by DataForSEO support
    task_id = "10061428-1060-0216-0000-989032d4e2c6"

    print("=" * 60)
    print("Testing Prism Specialties DMV Task Retrieval")
    print("=" * 60)
    print(f"Task ID: {task_id}")
    print(f"Website: prismspecialtiesdmv.com")
    print()
    print("According to DataForSEO support:")
    print("- Task completed successfully")
    print("- Was not marked as finished due to lag spike on their side")
    print("- They are fixing this issue")
    print()

    # Try to retrieve the task
    print("Attempting to retrieve task via /summary/ endpoint...")
    try:
        result = await client.task_get(task_id)

        print("✅ Task retrieval SUCCESSFUL!")
        print()

        if result.get("tasks") and len(result["tasks"]) > 0:
            task_data = result["tasks"][0]

            print("Task Data:")
            print(f"  Status Code: {task_data.get('status_code')}")
            print(f"  Status Message: {task_data.get('status_message')}")
            print()

            if task_data.get("result") and len(task_data["result"]) > 0:
                crawl_result = task_data["result"][0]

                print("Crawl Results:")
                print(f"  Target: {crawl_result.get('target', 'N/A')}")
                print(f"  Crawl Progress: {crawl_result.get('crawl_progress')}")
                print(f"  Pages Crawled: {crawl_result.get('pages_crawled')}")
                print(f"  Pages in Queue: {crawl_result.get('pages_in_queue')}")
                print(f"  Items Count: {crawl_result.get('items_count')}")
                print(f"  Items Available: {len(crawl_result.get('items', []))}")
                print()

                # Show some page data if available
                items = crawl_result.get('items', [])
                if items:
                    print(f"Sample Pages (first 3):")
                    for i, item in enumerate(items[:3], 1):
                        print(f"\n  Page {i}:")
                        print(f"    URL: {item.get('url')}")
                        print(f"    Status Code: {item.get('status_code')}")

                        meta = item.get('meta', {})
                        print(f"    Title: {meta.get('title', 'N/A')[:60]}...")
                        print(f"    H1 Count: {len(meta.get('htags', {}).get('h1', []))}")

                print()
                print("=" * 60)
                print("SUCCESS: Task data retrieved successfully!")
                print("This confirms the /summary/ endpoint is working.")
                print("=" * 60)

            else:
                print("⚠️  Task exists but has no results yet")
                print("This might mean the task is still processing")
        else:
            print("⚠️  No task data in response")

    except Exception as e:
        error_msg = str(e)
        print(f"❌ Task retrieval FAILED: {error_msg}")
        print()

        if "TASK_IN_QUEUE" in error_msg:
            print("Status: Task is still in queue (processing not started)")
        elif "TASK_IN_PROGRESS" in error_msg:
            print("Status: Task is currently being processed")
        elif "404" in error_msg:
            print("Status: Task not found (404)")
            print()
            print("This could mean:")
            print("  1. Task ID is incorrect")
            print("  2. Task has expired (DataForSEO keeps results for limited time)")
            print("  3. Task was from a different account")
        else:
            print(f"Unexpected error: {error_msg}")

        print()
        print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_prism_task())
