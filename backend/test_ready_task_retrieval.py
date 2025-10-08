#!/usr/bin/env python3
"""
Test retrieving tasks from tasks_ready list
"""
import asyncio
import json
from app.services.dataforseo_client import DataForSEOClient

async def test_ready_task_retrieval():
    """Test if we can retrieve tasks from ready list"""
    client = DataForSEOClient()

    print("=" * 60)
    print("Testing task retrieval from tasks_ready")
    print("=" * 60)
    print()

    # Get ready tasks
    print("Fetching ready tasks...")
    ready = await client.tasks_ready()

    # IMPORTANT: Task IDs are in 'result' array, not 'tasks'
    print(f"Ready tasks count: {len(ready.get('result', []))}")
    print(f"Top-level API request ID (ignore): {ready.get('id')}")
    print()

    if not ready.get('result'):
        print("No ready tasks found")
        return

    # Try to get each ready task - use 'result' array!
    for i, task in enumerate(ready['result'][:5], 1):
        task_id = task.get('id')
        print(f"Task #{i}: {task_id}")
        print(f"  Status: {task.get('status_message')}")

        # Try to retrieve this task
        try:
            result = await client.task_get(task_id)
            print(f"  ✅ Retrieved successfully!")

            if result.get("tasks") and len(result["tasks"]) > 0:
                task_data = result["tasks"][0]

                if task_data.get("result") and len(task_data["result"]) > 0:
                    crawl_result = task_data["result"][0]

                    print(f"    Target: {crawl_result.get('target', 'N/A')}")
                    print(f"    Progress: {crawl_result.get('crawl_progress')}")
                    print(f"    Pages Crawled: {crawl_result.get('pages_crawled')}")
                    print(f"    Items: {len(crawl_result.get('items', []))}")

                    # Show full task structure for first task
                    if i == 1:
                        print(f"\n  Full task data structure:")
                        print(f"  {json.dumps(task_data.get('data', {}), indent=4)}")
                else:
                    print(f"    No results in task")
            else:
                print(f"    No task data")

        except Exception as e:
            print(f"  ❌ Failed to retrieve: {e}")

        print()

    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_ready_task_retrieval())
