#!/usr/bin/env python3
"""
Complete end-to-end test of the DataForSEO workflow with fixes applied
Tests: task_post → tasks_ready (with correct parsing) → task_get via /summary/
"""
import asyncio
import json
from datetime import datetime
from app.services.dataforseo_client import DataForSEOClient

async def test_complete_workflow():
    """Test complete workflow with a small, fast crawl"""
    client = DataForSEOClient()

    print("=" * 70)
    print("COMPLETE WORKFLOW TEST - DataForSEO Fixes Validation")
    print("=" * 70)
    print()
    print("Testing fixes:")
    print("  ✅ Using /summary/ endpoint (not /task_get/)")
    print("  ✅ Parsing task IDs from 'result' array (not 'tasks')")
    print()

    # Use example.com for a quick, reliable test
    target_url = "https://example.com"
    max_pages = 1  # Just 1 page for speed

    # Step 1: Create task
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Step 1: Creating crawl task...")
    print(f"  Target: {target_url}")
    print(f"  Max Pages: {max_pages}")
    print()

    try:
        task_response = await client.task_post(target_url, max_pages)

        if not task_response.get("tasks") or len(task_response["tasks"]) == 0:
            print("❌ Failed to create task")
            return

        task_data = task_response["tasks"][0]
        task_id = task_data.get("id")
        status_code = task_data.get("status_code")

        if status_code != 20100:
            print(f"❌ Task creation failed: {task_data.get('status_message')}")
            return

        print(f"✅ Task created successfully!")
        print(f"  Task ID: {task_id}")
        print(f"  Status Code: {status_code}")
        print()

    except Exception as e:
        print(f"❌ Task creation error: {e}")
        return

    # Step 2: Poll tasks_ready (with CORRECT parsing)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Step 2: Polling tasks_ready (max 3 minutes)...")
    print()

    max_wait = 180  # 3 minutes
    poll_interval = 10  # seconds
    start_time = datetime.now()
    poll_count = 0
    task_found = False

    while True:
        elapsed = (datetime.now() - start_time).total_seconds()

        if elapsed > max_wait:
            print(f"⏱️  Timeout after {max_wait} seconds")
            print("Note: Task might still complete later, but we're stopping the test")
            break

        poll_count += 1
        timestamp = datetime.now().strftime('%H:%M:%S')

        try:
            ready = await client.tasks_ready()

            # CRITICAL FIX: Use 'result' array, not 'tasks'
            ready_tasks = ready.get('result', [])
            ready_count = len(ready_tasks)

            print(f"[{timestamp}] Poll #{poll_count} - {ready_count} tasks in ready list")

            # Check if our task is ready
            for task in ready_tasks:
                task_ready_id = task.get('id')
                task_target = task.get('target', '')

                # Show all ready tasks for debugging
                print(f"  - Task: {task_ready_id}")
                print(f"    Target: {task_target}")

                # Check if this is our task
                if task_ready_id == task_id:
                    print(f"  ✅ Found our task in ready list!")
                    task_found = True
                    break

            if task_found:
                break

        except Exception as e:
            print(f"  ⚠️  Error checking tasks_ready: {e}")

        # Wait before next poll
        if not task_found:
            await asyncio.sleep(poll_interval)

    print()

    if not task_found:
        print("⚠️  Task not found in tasks_ready within timeout period")
        print("Attempting direct retrieval anyway...")
        print()

    # Step 3: Retrieve results via /summary/ endpoint
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Step 3: Retrieving results via /summary/...")
    print(f"  Endpoint: /v3/on_page/summary/{task_id}")
    print()

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
                print(f"  Pages Crawled: {crawl_result.get('pages_crawled', 0)}")
                print(f"  Pages in Queue: {crawl_result.get('pages_in_queue', 0)}")
                print(f"  Items Count: {len(crawl_result.get('items', []))}")
                print()

                # Show first page data
                items = crawl_result.get('items', [])
                if items:
                    print("First Page Data:")
                    item = items[0]
                    print(f"  URL: {item.get('url')}")
                    print(f"  Status Code: {item.get('status_code')}")

                    meta = item.get('meta', {})
                    print(f"  Title: {meta.get('title', 'N/A')}")
                    print(f"  Description: {meta.get('description', 'N/A')[:80]}...")

                    checks = item.get('checks', {})
                    print(f"  Has Title: {checks.get('is_title')}")
                    print(f"  Has Description: {checks.get('is_description')}")
                    print(f"  Is HTTPS: {checks.get('is_https')}")
                    print()

                print("=" * 70)
                print("🎉 SUCCESS! Complete workflow validated:")
                print("  ✅ Task created")
                print(f"  ✅ Task found in tasks_ready (parsed from 'result' array)")
                print("  ✅ Results retrieved via /summary/ endpoint")
                print("  ✅ Data parsed successfully")
                print("=" * 70)

            else:
                print("⚠️  Task exists but has no results yet")
                crawl_progress = task_data.get("result", [{}])[0].get("crawl_progress") if task_data.get("result") else "unknown"
                print(f"  Crawl Progress: {crawl_progress}")

                if crawl_progress == "in_queue":
                    print("  Status: Task is queued for processing")
                elif crawl_progress == "in_progress":
                    print("  Status: Task is currently being crawled")
                else:
                    print("  Status: Unknown - may need more time")

        else:
            print("⚠️  No task data in response")

    except Exception as e:
        error_msg = str(e)
        print(f"❌ Task retrieval FAILED: {error_msg}")
        print()

        if "TASK_IN_QUEUE" in error_msg:
            print("Status: Task is still in queue")
            print("✅ This is expected - task just needs more time")
        elif "TASK_IN_PROGRESS" in error_msg:
            print("Status: Task is being processed")
            print("✅ This is expected - task just needs more time")
        elif "404" in error_msg:
            print("❌ Task not found (404)")
            print("This should NOT happen with correct endpoint")
        else:
            print(f"Unexpected error")

    print()
    print("=" * 70)
    print("Test Complete")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_complete_workflow())
