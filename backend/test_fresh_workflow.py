#!/usr/bin/env python3
"""
Test fresh workflow: create task -> wait for tasks_ready -> retrieve
"""
import asyncio
import json
from datetime import datetime
from app.services.dataforseo_client import DataForSEOClient

async def test_fresh_workflow():
    """Test complete fresh workflow"""
    client = DataForSEOClient()

    print("=" * 70)
    print("Fresh DataForSEO Workflow Test")
    print("="  * 70)
    print()

    # Step 1: Create a fresh task
    target_url = "https://example.com"
    max_pages = 5

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Creating task...")
    print(f"  Target: {target_url}")
    print(f"  Max Pages: {max_pages}")
    print()

    task_response = await client.task_post(target_url, max_pages)
    task_id_created = task_response["tasks"][0]["id"]

    print(f"✅ Task created successfully")
    print(f"  Task ID: {task_id_created}")
    print(f"  Cost: ${task_response['cost']}")
    print()

    # Step 2: Poll tasks_ready until our task appears
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Polling tasks_ready (max 5 minutes)...")
    print(f"  Checking every 15 seconds for task to complete")
    print()

    start_time = asyncio.get_event_loop().time()
    max_wait = 300  # 5 minutes
    poll_interval = 15  # 15 seconds

    found_task_id = None
    poll_count = 0

    while True:
        elapsed = asyncio.get_event_loop().time() - start_time
        if elapsed > max_wait:
            print(f"⏱️ Timeout after {max_wait} seconds")
            break

        poll_count += 1
        timestamp = datetime.now().strftime('%H:%M:%S')

        ready = await client.tasks_ready()
        # FIXED: Use 'result' array, not 'tasks'
        ready_count = len(ready.get('result', []))

        print(f"[{timestamp}] Poll #{poll_count} - {ready_count} tasks in ready list")

        # Check if any of the ready tasks match our target URL
        # FIXED: Use 'result' array, not 'tasks'
        if ready.get('result'):
            for task in ready['result']:
                task_id = task.get('id')

                # Try to get this task
                try:
                    result = await client.task_get(task_id)

                    if result.get("tasks") and len(result["tasks"]) > 0:
                        task_data = result["tasks"][0]

                        # Check if this is for our target URL
                        if task_data.get("result") and len(task_data["result"]) > 0:
                            crawl_result = task_data["result"][0]
                            task_target = crawl_result.get('target', '')

                            if target_url in task_target or task_target in target_url:
                                found_task_id = task_id
                                print(f"\n✅ Found our task!")
                                print(f"  Task ID in ready list: {task_id}")
                                print(f"  Original task ID: {task_id_created}")
                                print(f"  IDs match: {task_id == task_id_created}")
                                print(f"  Target: {task_target}")
                                print(f"  Crawl Progress: {crawl_result.get('crawl_progress')}")
                                print(f"  Pages Crawled: {crawl_result.get('pages_crawled')}")
                                print(f"  Items: {len(crawl_result.get('items', []))}")
                                print()

                                # Save results
                                print(f"Full crawl result:")
                                print(json.dumps(crawl_result, indent=2))
                                return

                except Exception as e:
                    # Silently skip 404s from already-collected tasks
                    if "404" not in str(e):
                        print(f"  Error getting task {task_id}: {e}")

        # Wait before next poll
        await asyncio.sleep(poll_interval)

    if not found_task_id:
        print(f"\n❌ Task never appeared in ready list within {max_wait} seconds")
        print(f"\nThis could mean:")
        print(f"  1. Task is still processing (crawls can take 2-5 minutes)")
        print(f"  2. Task failed during execution")
        print(f"  3. DataForSEO API has task retention issues")

    print()
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_fresh_workflow())
