"""
Test Phase 4B: Competitor Comparison API Endpoints (Unit Test)
Tests API structure without making real DataForSEO calls
"""

import sys
sys.path.insert(0, '/home/klatt42/serp-master/backend')


def test_competitor_comparison_api_structure():
    """Test that API endpoints are properly defined"""
    print("=" * 60)
    print("Phase 4B: Competitor Comparison API Unit Test")
    print("=" * 60)

    try:
        # Test 1: Import models
        print(f"\n[1/5] Testing Pydantic models...")

        from app.models import (
            CompetitorComparisonRequest,
            CompetitorComparisonStartResponse,
            CompetitorComparisonStatus,
            CompetitorComparisonStatusResponse,
            CompetitorComparisonResults,
            SiteComparisonData,
            CompetitiveGap,
            CompetitiveAction,
            CompetitorQuickWin
        )

        print(f"  ✓ All models imported successfully")

        # Test 2: Validate CompetitorComparisonRequest model
        print(f"\n[2/5] Testing CompetitorComparisonRequest validation...")

        request = CompetitorComparisonRequest(
            user_url="example.com",
            competitor_urls=["comp1.com", "comp2.com"],
            max_pages=50
        )

        assert request.user_url == "example.com"
        assert len(request.competitor_urls) == 2
        assert request.max_pages == 50

        print(f"  ✓ Request model validation works")

        # Test 3: Test status enum
        print(f"\n[3/5] Testing CompetitorComparisonStatus enum...")

        assert CompetitorComparisonStatus.CRAWLING == "crawling"
        assert CompetitorComparisonStatus.ANALYZING == "analyzing"
        assert CompetitorComparisonStatus.COMPLETE == "complete"
        assert CompetitorComparisonStatus.FAILED == "failed"

        print(f"  ✓ Status enum defined correctly")

        # Test 4: Import routes
        print(f"\n[4/5] Testing routes import...")

        from app.api.routes import (
            start_competitor_comparison,
            get_comparison_status,
            get_comparison_results,
            run_competitor_comparison,
            comparison_tasks
        )

        print(f"  ✓ All endpoints imported successfully")
        print(f"    - start_competitor_comparison")
        print(f"    - get_comparison_status")
        print(f"    - get_comparison_results")
        print(f"    - run_competitor_comparison (background task)")

        # Test 5: Verify comparison_tasks storage exists
        print(f"\n[5/5] Testing comparison_tasks storage...")

        assert isinstance(comparison_tasks, dict)
        print(f"  ✓ Comparison tasks storage initialized")

        print("\n" + "=" * 60)
        print("✅ Phase 4B: ALL UNIT TESTS PASSED")
        print("=" * 60)
        print("\nCompetitor Comparison API is properly structured!")
        print("✓ Pydantic models defined (9 models)")
        print("✓ Status enum with 4 states")
        print("✓ Three API endpoints defined")
        print("✓ Background task function defined")
        print("✓ Task storage initialized")
        print("\nAPI Endpoints Available:")
        print("  POST   /api/compare/start")
        print("  GET    /api/compare/status/{comparison_id}")
        print("  GET    /api/compare/results/{comparison_id}")
        print("\nReady to proceed to Phase 4C: Frontend Comparison UI\n")

        return True

    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = test_competitor_comparison_api_structure()
    sys.exit(0 if result else 1)
