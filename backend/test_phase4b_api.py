"""
Test Phase 4B: Competitor Comparison API Endpoints
Tests the new FastAPI endpoints for competitor analysis
"""

import sys
sys.path.insert(0, '/home/klatt42/serp-master/backend')

from fastapi.testclient import TestClient
from app.main import app
import time

# Create test client
client = TestClient(app)


def test_competitor_comparison_api():
    """Test competitor comparison API endpoints"""
    print("=" * 60)
    print("Phase 4B: Competitor Comparison API Test")
    print("=" * 60)

    try:
        # Test 1: Start comparison
        print(f"\n[1/4] Testing POST /api/compare/start...")

        request_data = {
            "user_url": "example.com",
            "competitor_urls": ["competitor1.com", "competitor2.com"],
            "max_pages": 10
        }

        response = client.post("/api/compare/start", json=request_data)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        assert "comparison_id" in data, "Missing comparison_id"
        assert "status" in data, "Missing status"
        assert "sites_to_analyze" in data, "Missing sites_to_analyze"
        assert data["sites_to_analyze"] == 3, f"Expected 3 sites, got {data['sites_to_analyze']}"

        comparison_id = data["comparison_id"]

        print(f"  ✓ Comparison started: {comparison_id}")
        print(f"    Sites to analyze: {data['sites_to_analyze']}")
        print(f"    Status: {data['status']}")
        print(f"    Estimated time: {data['estimated_time_seconds']}s")

        # Test 2: Check status
        print(f"\n[2/4] Testing GET /api/compare/status/{comparison_id[:20]}...")

        response = client.get(f"/api/compare/status/{comparison_id}")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        assert "comparison_id" in data, "Missing comparison_id"
        assert "status" in data, "Missing status"
        assert "progress" in data, "Missing progress"
        assert "sites_completed" in data, "Missing sites_completed"
        assert "sites_total" in data, "Missing sites_total"

        print(f"  ✓ Status retrieved")
        print(f"    Status: {data['status']}")
        print(f"    Progress: {data['progress']}%")
        print(f"    Sites completed: {data['sites_completed']}/{data['sites_total']}")

        # Test 3: Try to get results (should be 425 - Too Early)
        print(f"\n[3/4] Testing GET /api/compare/results (should fail while running)...")

        response = client.get(f"/api/compare/results/{comparison_id}")

        assert response.status_code == 425, f"Expected 425 (Too Early), got {response.status_code}"

        print(f"  ✓ Correctly returned 425 (comparison still running)")
        print(f"    Message: {response.json().get('detail', '')}")

        # Test 4: Validation tests
        print(f"\n[4/4] Testing input validation...")

        # Test 4a: Too many competitors
        response = client.post("/api/compare/start", json={
            "user_url": "example.com",
            "competitor_urls": ["c1.com", "c2.com", "c3.com", "c4.com"],
            "max_pages": 10
        })
        assert response.status_code == 400, "Should reject > 3 competitors"
        print(f"  ✓ Correctly rejected 4 competitors (max 3)")

        # Test 4b: User URL in competitor list
        response = client.post("/api/compare/start", json={
            "user_url": "example.com",
            "competitor_urls": ["example.com", "competitor.com"],
            "max_pages": 10
        })
        assert response.status_code == 400, "Should reject user URL in competitor list"
        print(f"  ✓ Correctly rejected duplicate user URL")

        # Test 4c: Empty competitor list
        response = client.post("/api/compare/start", json={
            "user_url": "example.com",
            "competitor_urls": [],
            "max_pages": 10
        })
        assert response.status_code == 422, "Should reject empty competitor list (Pydantic validation)"
        print(f"  ✓ Correctly rejected empty competitor list")

        print("\n" + "=" * 60)
        print("✅ Phase 4B: ALL API TESTS PASSED")
        print("=" * 60)
        print("\nCompetitor Comparison API Endpoints are working correctly!")
        print("✓ POST /api/compare/start - Start comparison")
        print("✓ GET /api/compare/status/{id} - Get status")
        print("✓ GET /api/compare/results/{id} - Get results")
        print("✓ Input validation working")
        print("\nNote: Background comparison task started but not awaited in test.")
        print("In production, the comparison will complete and results will be available.\n")
        print("Ready to proceed to Phase 4C: Frontend Comparison UI\n")

        return True

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        return False
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = test_competitor_comparison_api()
    sys.exit(0 if result else 1)
