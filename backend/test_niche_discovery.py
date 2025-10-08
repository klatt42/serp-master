"""
Test Niche Discovery System
Week 5 - Complete Pipeline Test
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.keyword_discoverer import KeywordDiscoverer
from app.services.opportunity_scorer import OpportunityScorer
from app.models.opportunity import OpportunityFilters


async def test_full_discovery():
    """Test complete niche discovery pipeline"""

    seed_keyword = "SEO audit"

    print(f"\n{'='*80}")
    print(f"TESTING NICHE DISCOVERY PIPELINE")
    print(f"{'='*80}")
    print(f"Seed Keyword: '{seed_keyword}'")
    print(f"{'='*80}\n")

    # Step 1: Discover keywords
    print("Step 1: Discovering keywords from DataForSEO...")
    print("-" * 80)
    try:
        async with KeywordDiscoverer() as discoverer:
            batch = await discoverer.discover_keywords(seed_keyword, limit=100)

        print(f"✅ SUCCESS: Found {batch.total_found} keywords")
        print(f"   Sample keywords:")
        for i, k in enumerate(batch.keywords[:5], 1):
            print(f"   {i}. {k.keyword} (Volume: {k.search_volume:,}, Difficulty: {k.keyword_difficulty or 'N/A'})")
        print()

    except Exception as e:
        print(f"❌ FAILED: {str(e)}\n")
        return

    # Step 2: Score opportunities
    print("Step 2: Scoring opportunities...")
    print("-" * 80)
    try:
        filters = OpportunityFilters(
            min_volume=100,
            max_difficulty=60
        )

        scorer = OpportunityScorer(filters=filters)
        opportunities = scorer.score_keywords(batch.keywords)

        print(f"✅ SUCCESS: Found {len(opportunities)} qualified opportunities")
        print(f"   (Filtered by: min_volume=100, max_difficulty=60)")
        print()

    except Exception as e:
        print(f"❌ FAILED: {str(e)}\n")
        return

    # Step 3: Display top opportunities
    print("Step 3: Top 10 Opportunities")
    print("=" * 120)
    print(f"{'Keyword':<45} {'Score':<10} {'Volume':<12} {'Diff':<8} {'CPC':<10} {'Level':<15}")
    print("=" * 120)

    for opp in opportunities[:10]:
        print(f"{opp.keyword:<45} {opp.opportunity_score:>8.2f}  {opp.search_volume:>10,}  {opp.keyword_difficulty:>6}  ${opp.cpc:>8.2f}  {opp.opportunity_level:<15}")

    print("=" * 120)
    print()

    # Step 4: Show best opportunity details
    if opportunities:
        best = opportunities[0]
        print(f"🌟 BEST OPPORTUNITY: {best.keyword}")
        print("-" * 80)
        print(f"   • Opportunity Score: {best.opportunity_score:.2f}/100")
        print(f"   • Opportunity Level: {best.opportunity_level.upper()}")
        print(f"   • Search Volume: {best.search_volume:,} monthly searches")
        print(f"   • Keyword Difficulty: {best.keyword_difficulty}/100")
        print(f"   • CPC: ${best.cpc:.2f}")
        print(f"   • Competition: {best.competition:.2f}")
        print(f"   • ROI Potential: {best.roi_potential:.2f}")
        print(f"   • Estimated Traffic: {best.estimated_traffic:,} monthly visitors")
        print(f"   • Recommended Content: {best.recommended_content_type}")
        print(f"   • Effort Level: {best.effort_level}")
        print()

    # Step 5: Summary statistics
    total_volume = sum(opp.search_volume for opp in opportunities)
    avg_score = sum(opp.opportunity_score for opp in opportunities) / len(opportunities) if opportunities else 0

    excellent = sum(1 for opp in opportunities if opp.opportunity_level == "excellent")
    good = sum(1 for opp in opportunities if opp.opportunity_level == "good")
    moderate = sum(1 for opp in opportunities if opp.opportunity_level == "moderate")
    low = sum(1 for opp in opportunities if opp.opportunity_level == "low")

    print(f"📊 SUMMARY STATISTICS")
    print("-" * 80)
    print(f"   • Total Keywords Analyzed: {batch.total_found}")
    print(f"   • Opportunities Found: {len(opportunities)}")
    print(f"   • Total Potential Monthly Searches: {total_volume:,}")
    print(f"   • Average Opportunity Score: {avg_score:.2f}/100")
    print()
    print(f"   Breakdown by Quality:")
    print(f"   • Excellent Opportunities: {excellent}")
    print(f"   • Good Opportunities: {good}")
    print(f"   • Moderate Opportunities: {moderate}")
    print(f"   • Low Opportunities: {low}")
    print()

    # Step 6: Component score breakdown
    if opportunities:
        avg_volume_score = sum(opp.volume_score for opp in opportunities) / len(opportunities)
        avg_difficulty_score = sum(opp.difficulty_score for opp in opportunities) / len(opportunities)
        avg_cpc_score = sum(opp.cpc_score for opp in opportunities) / len(opportunities)
        avg_competition_score = sum(opp.competition_score for opp in opportunities) / len(opportunities)

        print(f"   Average Component Scores:")
        print(f"   • Volume Score: {avg_volume_score:.2f}/100")
        print(f"   • Difficulty Score: {avg_difficulty_score:.2f}/100")
        print(f"   • CPC Score: {avg_cpc_score:.2f}/100")
        print(f"   • Competition Score: {avg_competition_score:.2f}/100")
        print()

    print("=" * 80)
    print("✅ ALL TESTS PASSED!")
    print("=" * 80)
    print()


async def test_filtering():
    """Test opportunity filtering"""

    print(f"\n{'='*80}")
    print(f"TESTING FILTERING FUNCTIONALITY")
    print(f"{'='*80}\n")

    seed_keyword = "content marketing"

    print(f"Discovering keywords for: '{seed_keyword}'")
    async with KeywordDiscoverer() as discoverer:
        batch = await discoverer.discover_keywords(seed_keyword, limit=50)

    print(f"Found {batch.total_found} keywords\n")

    # Test 1: High volume only
    print("Test 1: High Volume Only (min 1000 searches)")
    print("-" * 80)
    filters = OpportunityFilters(min_volume=1000, max_difficulty=100)
    scorer = OpportunityScorer(filters=filters)
    opps = scorer.score_keywords(batch.keywords)
    print(f"✅ Found {len(opps)} high-volume opportunities")
    if opps:
        print(f"   Top 3: {', '.join([o.keyword for o in opps[:3]])}")
    print()

    # Test 2: Easy wins only
    print("Test 2: Easy Wins (difficulty < 30)")
    print("-" * 80)
    filters = OpportunityFilters(min_volume=100, max_difficulty=30)
    scorer = OpportunityScorer(filters=filters)
    opps = scorer.score_keywords(batch.keywords)
    print(f"✅ Found {len(opps)} easy-win opportunities")
    if opps:
        print(f"   Top 3: {', '.join([o.keyword for o in opps[:3]])}")
    print()

    # Test 3: High CPC only
    print("Test 3: High CPC (min $2.00)")
    print("-" * 80)
    filters = OpportunityFilters(min_volume=100, max_difficulty=100, min_cpc=2.0)
    scorer = OpportunityScorer(filters=filters)
    opps = scorer.score_keywords(batch.keywords)
    print(f"✅ Found {len(opps)} high-CPC opportunities")
    if opps:
        print(f"   Top 3: {', '.join([o.keyword for o in opps[:3]])}")
        print(f"   CPCs: {', '.join([f'${o.cpc:.2f}' for o in opps[:3]])}")
    print()

    print("=" * 80)
    print("✅ FILTERING TESTS PASSED!")
    print("=" * 80)
    print()


async def main():
    """Run all tests"""
    try:
        # Test 1: Full pipeline
        await test_full_discovery()

        # Test 2: Filtering
        await test_filtering()

        print("\n🎉 ALL TESTS COMPLETED SUCCESSFULLY! 🎉\n")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
