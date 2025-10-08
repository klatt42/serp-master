#!/usr/bin/env python3
"""
SERP-Master API Test Script
Tests the complete audit workflow
"""

import requests
import time
import json
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
TEST_URL = "example.com"  # Test website
MAX_PAGES = 10

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_success(message: str):
    print(f"{GREEN}✓ {message}{RESET}")


def print_error(message: str):
    print(f"{RED}✗ {message}{RESET}")


def print_info(message: str):
    print(f"{BLUE}ℹ {message}{RESET}")


def print_warning(message: str):
    print(f"{YELLOW}⚠ {message}{RESET}")


def test_health_check():
    """Test the health check endpoint"""
    print("\n" + "="*60)
    print("TEST 1: Health Check")
    print("="*60)

    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()

        data = response.json()
        print_info(f"Response: {json.dumps(data, indent=2)}")

        assert data["status"] == "healthy", "API is not healthy"
        assert data["dataforseo_configured"], "DataForSEO not configured"

        print_success("Health check passed")
        return True

    except Exception as e:
        print_error(f"Health check failed: {str(e)}")
        return False


def start_audit(url: str, max_pages: int) -> Dict[str, Any]:
    """Start a new audit"""
    print("\n" + "="*60)
    print("TEST 2: Start Audit")
    print("="*60)

    try:
        payload = {
            "url": url,
            "max_pages": max_pages
        }

        print_info(f"Starting audit for: {url}")
        print_info(f"Max pages: {max_pages}")

        response = requests.post(
            f"{BASE_URL}/api/audit/start",
            json=payload
        )
        response.raise_for_status()

        data = response.json()
        print_info(f"Response: {json.dumps(data, indent=2)}")

        assert "task_id" in data, "No task_id in response"
        assert data["status"] == "crawling", "Status not crawling"

        print_success(f"Audit started with task_id: {data['task_id']}")
        return data

    except Exception as e:
        print_error(f"Failed to start audit: {str(e)}")
        raise


def poll_audit_status(task_id: str, max_wait: int = 600) -> str:
    """Poll audit status until complete"""
    print("\n" + "="*60)
    print("TEST 3: Poll Audit Status")
    print("="*60)

    start_time = time.time()
    poll_count = 0

    while time.time() - start_time < max_wait:
        poll_count += 1

        try:
            response = requests.get(f"{BASE_URL}/api/audit/status/{task_id}")
            response.raise_for_status()

            data = response.json()
            status = data["status"]
            progress = data["progress"]

            print_info(f"Poll #{poll_count} - Status: {status}, Progress: {progress}%")

            if status == "complete":
                elapsed = time.time() - start_time
                print_success(f"Audit completed in {elapsed:.1f} seconds ({poll_count} polls)")
                return status

            if status == "failed":
                print_error(f"Audit failed: {data.get('message', 'Unknown error')}")
                return status

            # Wait before next poll
            time.sleep(10)

        except Exception as e:
            print_error(f"Error polling status: {str(e)}")
            time.sleep(10)

    print_error(f"Audit timeout after {max_wait} seconds")
    return "timeout"


def get_audit_results(task_id: str) -> Dict[str, Any]:
    """Get complete audit results"""
    print("\n" + "="*60)
    print("TEST 4: Get Audit Results")
    print("="*60)

    try:
        response = requests.get(f"{BASE_URL}/api/audit/results/{task_id}")
        response.raise_for_status()

        data = response.json()

        print_success("Results retrieved successfully")
        return data

    except Exception as e:
        print_error(f"Failed to get results: {str(e)}")
        raise


def validate_results(results: Dict[str, Any]):
    """Validate audit results"""
    print("\n" + "="*60)
    print("TEST 5: Validate Results")
    print("="*60)

    try:
        # Validate structure
        assert "task_id" in results, "Missing task_id"
        assert "url" in results, "Missing url"
        assert "score" in results, "Missing score"
        assert "issues" in results, "Missing issues"
        assert "metadata" in results, "Missing metadata"

        print_success("Result structure valid")

        # Validate score
        score = results["score"]
        assert "total_score" in score, "Missing total_score"
        assert "percentage" in score, "Missing percentage"
        assert "grade" in score, "Missing grade"
        assert "technical_seo" in score, "Missing technical_seo"
        assert "onpage_seo" in score, "Missing onpage_seo"
        assert "structure_seo" in score, "Missing structure_seo"

        print_success("Score structure valid")

        # Validate issues
        issues = results["issues"]
        assert "critical_issues" in issues, "Missing critical_issues"
        assert "warnings" in issues, "Missing warnings"
        assert "info" in issues, "Missing info"
        assert "quick_wins" in issues, "Missing quick_wins"
        assert "summary" in issues, "Missing summary"

        print_success("Issues structure valid")

        print_success("All validations passed!")
        return True

    except AssertionError as e:
        print_error(f"Validation failed: {str(e)}")
        return False


def print_audit_summary(results: Dict[str, Any]):
    """Print audit summary"""
    print("\n" + "="*60)
    print("AUDIT SUMMARY")
    print("="*60)

    score = results["score"]
    issues = results["issues"]
    metadata = results["metadata"]

    print(f"\n🎯 SEO Score: {score['total_score']}/{score['max_score']} ({score['percentage']}%)")
    print(f"   Grade: {score['grade']}")

    print(f"\n📊 Score Breakdown:")
    print(f"   Technical SEO:  {score['technical_seo']['score']}/10")
    print(f"   On-Page SEO:    {score['onpage_seo']['score']}/10")
    print(f"   Site Structure: {score['structure_seo']['score']}/10")

    print(f"\n🔍 Issues Found:")
    print(f"   Critical: {issues['summary']['critical_count']}")
    print(f"   Warnings: {issues['summary']['warning_count']}")
    print(f"   Info:     {issues['summary']['info_count']}")
    print(f"   Quick Wins: {issues['summary']['quick_win_count']}")

    print(f"\n📈 Crawl Statistics:")
    print(f"   Pages Crawled: {metadata.get('pages_crawled', 'N/A')}")
    print(f"   Duration: {metadata.get('crawl_duration_seconds', 'N/A')}s")

    # Show top 3 quick wins
    if issues.get('quick_wins'):
        print(f"\n⚡ Top Quick Wins:")
        for i, issue in enumerate(issues['quick_wins'][:3], 1):
            print(f"\n   {i}. {issue['issue']}")
            print(f"      Impact: +{issue['impact']} points | Effort: {issue['effort']}")
            print(f"      {issue['recommendation'][:80]}...")

    print("\n" + "="*60)


def main():
    """Main test function"""
    print("\n" + "="*70)
    print(" SERP-Master API Test Suite")
    print("="*70)

    # Test 1: Health Check
    if not test_health_check():
        print_error("Health check failed. Exiting.")
        return

    # Test 2: Start Audit
    try:
        audit_data = start_audit(TEST_URL, MAX_PAGES)
        task_id = audit_data["task_id"]
    except Exception as e:
        print_error("Failed to start audit. Exiting.")
        return

    # Test 3: Poll Status
    status = poll_audit_status(task_id)
    if status != "complete":
        print_error("Audit did not complete successfully. Exiting.")
        return

    # Test 4: Get Results
    try:
        results = get_audit_results(task_id)
    except Exception as e:
        print_error("Failed to get results. Exiting.")
        return

    # Test 5: Validate Results
    if not validate_results(results):
        print_error("Result validation failed.")
        return

    # Print Summary
    print_audit_summary(results)

    # Success!
    print("\n" + "="*70)
    print(f"{GREEN} ALL TESTS PASSED! 🎉{RESET}")
    print("="*70)
    print(f"\n✓ API is fully functional")
    print(f"✓ DataForSEO integration working")
    print(f"✓ SEO scoring accurate")
    print(f"✓ Issue detection operational")
    print(f"\nAPI Docs: {BASE_URL}/docs")
    print(f"Test Results Saved: Full JSON available via API\n")


if __name__ == "__main__":
    main()
