"""
Test Phase 4A: Competitor Analyzer
Verifies competitor analysis functionality
"""

import asyncio
import sys
sys.path.insert(0, '/home/klatt42/serp-master/backend')

from app.services.competitor_analyzer import CompetitorAnalyzer


async def test_competitor_analyzer():
    """Test competitor analysis with mock data"""
    print("=" * 60)
    print("Phase 4A: Competitor Analyzer Test")
    print("=" * 60)

    analyzer = CompetitorAnalyzer()

    # Test data
    user_url = "example.com"
    competitor_urls = [
        "competitor-a.com",
        "competitor-b.com"
    ]

    print(f"\n✓ CompetitorAnalyzer initialized")
    print(f"  User URL: {user_url}")
    print(f"  Competitors: {len(competitor_urls)}")

    try:
        # Test basic instantiation
        print(f"\n[1/5] Testing class initialization...")
        assert hasattr(analyzer, 'analyze_competitors'), "Missing analyze_competitors method"
        assert hasattr(analyzer, 'audit_multiple_sites'), "Missing audit_multiple_sites method"
        assert hasattr(analyzer, 'compare_scores'), "Missing compare_scores method"
        assert hasattr(analyzer, 'calculate_gaps'), "Missing calculate_gaps method"
        assert hasattr(analyzer, 'generate_competitive_strategy'), "Missing generate_competitive_strategy method"
        print("  ✓ All required methods present")

        # Test individual audit
        print(f"\n[2/5] Testing single site audit...")
        single_audit = await analyzer.audit_site("test.com", max_pages=10)
        assert "url" in single_audit, "Missing URL in audit result"
        assert "status" in single_audit, "Missing status in audit result"
        assert "total_score" in single_audit, "Missing total_score in audit result"
        print(f"  ✓ Single audit returned: {single_audit.get('url')}")
        print(f"    Status: {single_audit.get('status')}")
        print(f"    Score: {single_audit.get('total_score', 0)}")

        # Test multiple site audits (parallel)
        print(f"\n[3/5] Testing parallel multi-site audits...")
        test_urls = ["site1.com", "site2.com", "site3.com"]
        multi_audits = await analyzer.audit_multiple_sites(test_urls, max_pages=10)
        assert len(multi_audits) == 3, f"Expected 3 results, got {len(multi_audits)}"
        print(f"  ✓ Parallel audits completed: {len(multi_audits)} sites")
        for audit in multi_audits:
            print(f"    - {audit.get('url')}: {audit.get('status')}")

        # Test score comparison
        print(f"\n[4/5] Testing score comparison...")
        user_mock = {"url": "user.com", "total_score": 45, "scores": {}}
        comp_mock = [
            {"url": "comp1.com", "total_score": 55, "scores": {}, "status": "complete"},
            {"url": "comp2.com", "total_score": 35, "scores": {}, "status": "complete"}
        ]
        comparison = analyzer.compare_scores(user_mock, comp_mock)
        assert "user_rank" in comparison, "Missing user_rank"
        assert "rankings" in comparison, "Missing rankings"
        print(f"  ✓ Comparison calculated")
        print(f"    User rank: {comparison.get('user_rank')}")
        print(f"    Total sites: {comparison.get('total_sites')}")
        print(f"    Score gap to first: {comparison.get('score_gap_to_first')}")

        # Test gap calculation
        print(f"\n[5/5] Testing gap calculation...")
        user_with_scores = {
            "url": "user.com",
            "total_score": 40,
            "scores": {
                "seo": {"total_score": 20},
                "aeo": {"aeo_score": 15, "schema_markup": {"score": 5}}
            }
        }
        comp_with_scores = [{
            "url": "comp.com",
            "total_score": 50,
            "status": "complete",
            "scores": {
                "seo": {"total_score": 25},
                "aeo": {"aeo_score": 20, "schema_markup": {"score": 8}}
            }
        }]
        gaps = analyzer.calculate_gaps(user_with_scores, comp_with_scores)
        print(f"  ✓ Gaps identified: {len(gaps)}")
        for gap in gaps[:3]:  # Show first 3
            print(f"    - {gap.get('dimension')}: {gap.get('issue')} (gap: {gap.get('gap')} pts)")

        print("\n" + "=" * 60)
        print("✅ Phase 4A: ALL TESTS PASSED")
        print("=" * 60)
        print("\nCompetitor Analyzer is working correctly!")
        print("Ready to proceed to Phase 4B: Comparison API Endpoints\n")

        return True

    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(test_competitor_analyzer())
    sys.exit(0 if result else 1)
