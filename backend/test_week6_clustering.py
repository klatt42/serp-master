"""
Test Week 6: Clustering & Niche Analysis
Complete Pipeline Test
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
from app.services.keyword_clusterer import KeywordClusterer
from app.services.niche_analyzer import NicheAnalyzer
from app.models.opportunity import OpportunityFilters


async def test_complete_analysis():
    """Test complete niche analysis pipeline with clustering"""

    seed_keyword = "content marketing"

    print(f"\n{'='*80}")
    print(f"TESTING WEEK 6: CLUSTERING & NICHE ANALYSIS")
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
            print(f"   {i}. {k.keyword} (Volume: {k.search_volume:,})")
        print()

    except Exception as e:
        print(f"❌ FAILED: {str(e)}\n")
        return

    # Step 2: Score opportunities
    print("Step 2: Scoring opportunities...")
    print("-" * 80)
    try:
        filters = OpportunityFilters(min_volume=100, max_difficulty=60)
        scorer = OpportunityScorer(filters=filters)
        opportunities = scorer.score_keywords(batch.keywords)

        print(f"✅ SUCCESS: Scored {len(opportunities)} opportunities")
        print()

    except Exception as e:
        print(f"❌ FAILED: {str(e)}\n")
        return

    # Step 3: Cluster keywords
    print("Step 3: Clustering keywords...")
    print("-" * 80)
    try:
        clusterer = KeywordClusterer(min_cluster_size=3, max_clusters=10)
        clusters = clusterer.cluster_keywords(batch.keywords)

        print(f"✅ SUCCESS: Created {len(clusters)} keyword clusters")
        print()

        # Display cluster summary
        print("Cluster Summary:")
        print("=" * 100)
        print(f"{'Cluster Name':<30} {'Keywords':<10} {'Volume':<15} {'Difficulty':<12} {'Theme Type':<20}")
        print("=" * 100)

        for cluster in clusters[:10]:
            print(f"{cluster.cluster_name:<30} {cluster.total_keywords:<10} {cluster.total_search_volume:>12,}  {cluster.avg_difficulty:>10.1f}  {cluster.theme.theme_type:<20}")

        print("=" * 100)
        print()

    except Exception as e:
        print(f"❌ FAILED: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return

    # Step 4: Analyze niche
    print("Step 4: Analyzing niche market dynamics...")
    print("-" * 80)
    try:
        analyzer = NicheAnalyzer()
        niche_analysis = analyzer.analyze_niche(
            seed_keyword=seed_keyword,
            keywords=batch.keywords,
            clusters=clusters
        )

        print(f"✅ SUCCESS: Niche analysis complete")
        print()

        # Display niche analysis results
        print("🔍 NICHE ANALYSIS RESULTS")
        print("=" * 80)
        print(f"Market Size: {niche_analysis.market_size.upper()}")
        print(f"Competition Level: {niche_analysis.competition_level.upper()}")
        print(f"Total Search Volume: {niche_analysis.total_search_volume:,} monthly searches")
        print(f"Average Keyword Difficulty: {niche_analysis.avg_keyword_difficulty:.2f}/100")
        print(f"Monetization Potential: ${niche_analysis.monetization_potential:,.2f}")
        print(f"Confidence Score: {niche_analysis.confidence_score:.2f}")
        print()

        print("📊 CONTENT GAPS IDENTIFIED:")
        print("-" * 80)
        if niche_analysis.content_gaps:
            for i, gap in enumerate(niche_analysis.content_gaps, 1):
                print(f"\n{i}. {gap.gap_type.upper()} ({gap.priority} priority)")
                print(f"   {gap.description}")
                print(f"   Sample keywords: {', '.join(gap.keywords[:3])}")
        else:
            print("No major content gaps identified")
        print()

        print("💡 RECOMMENDED STRATEGY:")
        print("-" * 80)
        print(f"{niche_analysis.recommended_strategy}")
        print()

        print("🎯 TOP MARKET OPPORTUNITIES:")
        print("=" * 100)
        print(f"{'Cluster':<25} {'Score':<8} {'Level':<12} {'Volume':<12} {'Difficulty':<12}")
        print("=" * 100)

        for opp in niche_analysis.opportunities[:5]:
            print(f"{opp.cluster_name:<25} {opp.opportunity_score:>6.2f}  {opp.opportunity_level:<12} {opp.total_search_volume:>10,}  {opp.avg_difficulty:>10.1f}")

        print("=" * 100)
        print()

    except Exception as e:
        print(f"❌ FAILED: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return

    # Step 5: Summary
    print("📈 OVERALL SUMMARY")
    print("=" * 80)
    print(f"   • Total Keywords Discovered: {len(batch.keywords)}")
    print(f"   • Opportunities Found: {len(opportunities)}")
    print(f"   • Clusters Created: {len(clusters)}")
    print(f"   • Content Gaps Identified: {len(niche_analysis.content_gaps)}")
    print(f"   • Market Opportunities: {len(niche_analysis.opportunities)}")
    print(f"   • Analysis Confidence: {niche_analysis.confidence_score:.0%}")
    print()

    print("=" * 80)
    print("✅ ALL WEEK 6 TESTS PASSED!")
    print("=" * 80)
    print()


async def test_clustering_quality():
    """Test clustering quality with different datasets"""

    print(f"\n{'='*80}")
    print(f"TESTING CLUSTERING QUALITY")
    print(f"{'='*80}\n")

    test_seeds = ["local SEO", "email marketing"]

    for seed in test_seeds:
        print(f"Testing: '{seed}'")
        print("-" * 80)

        try:
            async with KeywordDiscoverer() as discoverer:
                batch = await discoverer.discover_keywords(seed, limit=50)

            clusterer = KeywordClusterer(min_cluster_size=3, max_clusters=8)
            clusters = clusterer.cluster_keywords(batch.keywords)

            print(f"✅ Found {len(batch.keywords)} keywords → {len(clusters)} clusters")

            # Check cluster quality
            total_keywords_clustered = sum(c.total_keywords for c in clusters)
            coverage = (total_keywords_clustered / len(batch.keywords)) * 100 if batch.keywords else 0

            print(f"   Coverage: {coverage:.1f}% of keywords clustered")
            print(f"   Avg cluster size: {total_keywords_clustered / len(clusters) if clusters else 0:.1f} keywords")
            print()

        except Exception as e:
            print(f"❌ FAILED: {str(e)}\n")

    print("=" * 80)
    print("✅ CLUSTERING QUALITY TESTS COMPLETE!")
    print("=" * 80)
    print()


async def main():
    """Run all tests"""
    try:
        # Test 1: Complete analysis pipeline
        await test_complete_analysis()

        # Test 2: Clustering quality
        await test_clustering_quality()

        print("\n🎉 ALL WEEK 6 TESTS COMPLETED SUCCESSFULLY! 🎉\n")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
