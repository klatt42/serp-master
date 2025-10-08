#!/usr/bin/env python3
"""
Test to see the RAW API response from DataForSEO
This will help us understand what's actually being returned
"""
import asyncio
import json
from app.services.dataforseo_client import DataForSEOClient

async def inspect_raw_api():
    """Inspect raw API responses"""
    client = DataForSEOClient()

    print("=" * 70)
    print("RAW DataForSEO API Response Inspector")
    print("=" * 70)
    print()

    # Create a task for a well-known crawlable site
    target = "https://en.wikipedia.org"

    print(f"Step 1: Creating crawl task for {target}...")
    task_response = await client.task_post(target, max_crawl_pages=25)

    print("RAW task_post response:")
    print(json.dumps(task_response, indent=2))
    print()

    task_id = task_response["tasks"][0]["id"]
    print(f"Task ID: {task_id}")
    print()

    # Wait a bit for crawl to start
    print("Waiting 30 seconds for crawl to start...")
    await asyncio.sleep(30)

    print()
    print("Step 2: Checking status via /summary/ endpoint...")
    try:
        summary_response = await client.task_status(task_id)
        print("RAW /summary/ response:")
        print(json.dumps(summary_response, indent=2))
    except Exception as e:
        print(f"Error: {e}")

    print()
    print("Step 3: Trying /pages/ endpoint...")
    try:
        pages_response = await client.task_get(task_id)
        print("RAW /pages/ response:")
        print(json.dumps(pages_response, indent=2))
    except Exception as e:
        print(f"Error: {e}")

    print()
    print("=" * 70)
    print("Waiting for crawl to complete (up to 2 minutes)...")
    print("=" * 70)

    # Poll until complete
    for i in range(12):
        await asyncio.sleep(10)

        try:
            summary = await client.task_status(task_id)
            result = summary["tasks"][0]["result"][0] if summary.get("tasks") and summary["tasks"][0].get("result") else {}

            progress = result.get("crawl_progress", "unknown")
            pages_done = result.get("pages_crawled", 0)
            pages_queued = result.get("pages_in_queue", 0)

            print(f"Poll #{i+1}: progress={progress}, done={pages_done}, queued={pages_queued}")

            if progress == "finished":
                print()
                print("=" * 70)
                print("CRAWL FINISHED - FINAL RAW RESPONSE:")
                print("=" * 70)
                print(json.dumps(summary, indent=2))
                print()

                # Try pages endpoint now
                print("Attempting /pages/ endpoint...")
                try:
                    pages_resp = await client.task_get(task_id)
                    print("SUCCESS! /pages/ response:")
                    print(json.dumps(pages_resp, indent=2)[:2000])  # First 2000 chars
                except Exception as e:
                    print(f"/pages/ failed: {e}")

                break
        except Exception as e:
            print(f"Poll #{i+1}: Error - {e}")

if __name__ == "__main__":
    asyncio.run(inspect_raw_api())
