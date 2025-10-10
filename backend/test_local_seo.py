"""
Test script for Week 14: Local SEO & GEO Enhancement Engine
Tests NAP consistency audit and local SEO services
"""

import requests
import json
from pprint import pprint

BASE_URL = "http://localhost:8000"


def print_section(title):
    """Print section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def test_local_health():
    """Test local SEO services health"""
    print_section("Testing Local SEO Health")

    response = requests.get(f"{BASE_URL}/api/local/health")

    print(f"Status: {response.status_code}")
    print("Response:")
    pprint(response.json())

    return response.status_code == 200


def test_citation_audit_perfect():
    """Test citation audit with perfect NAP consistency"""
    print_section("Test 1: Perfect NAP Consistency")

    data = {
        "site_url": "https://example-business.com",
        "business_name": "Example Business LLC",
        "address": "123 Main Street, Anytown, CA 90210",
        "phone": "(555) 123-4567",
        "search_radius_miles": 25
    }

    print("Request data:")
    pprint(data)
    print()

    response = requests.post(
        f"{BASE_URL}/api/local/citations/audit",
        json=data
    )

    print(f"Status: {response.status_code}")
    result = response.json()

    print(f"\n📊 Results:")
    print(f"  Citations Found: {result['total_citations']}")
    print(f"  Major Platform Coverage: {result['major_platform_coverage']}/10")
    print(f"  Consistency Score: {result['consistency_score']}/100")
    print(f"  Citation Score (GEO): {result['citation_score']}/8")
    print(f"  Inconsistencies: {len(result['inconsistencies'])}")

    print(f"\n📋 Missing Platforms ({len(result['missing_major_platforms'])}):")
    for platform in result['missing_major_platforms']:
        print(f"  - {platform}")

    print(f"\n💡 Recommendations:")
    for rec in result['recommendations']:
        print(f"  • {rec}")

    return response.status_code == 200


def test_citation_audit_inconsistent():
    """Test citation audit with NAP inconsistencies"""
    print_section("Test 2: NAP Inconsistencies Detected")

    data = {
        "site_url": "https://test-business.com",
        "business_name": "Test Business Co.",
        "address": "456 Oak Avenue, Springfield, IL 62701",
        "phone": "555.987.6543",
        "search_radius_miles": 25
    }

    print("Request data:")
    pprint(data)
    print()

    response = requests.post(
        f"{BASE_URL}/api/local/citations/audit",
        json=data
    )

    print(f"Status: {response.status_code}")
    result = response.json()

    print(f"\n📊 Results:")
    print(f"  Citations Found: {result['total_citations']}")
    print(f"  Consistency Score: {result['consistency_score']}/100")
    print(f"  Citation Score (GEO): {result['citation_score']}/8")
    print(f"  Inconsistencies: {len(result['inconsistencies'])}")

    if result['inconsistencies']:
        print(f"\n⚠️  NAP Inconsistencies Detected:")
        for issue in result['inconsistencies']:
            print(f"\n  Field: {issue['field'].upper()}")
            print(f"  Source 1 ({issue['source1']}): {issue['value1']}")
            print(f"  Source 2 ({issue['source2']}): {issue['value2']}")
            print(f"  Similarity: {issue['similarity']:.1%}")
            print(f"  Severity: {issue['severity'].upper()}")
            print(f"  → {issue['suggestion']}")

    print(f"\n💡 Recommendations:")
    for rec in result['recommendations']:
        print(f"  • {rec}")

    return response.status_code == 200


def test_get_citation_sources():
    """Test retrieving citation sources"""
    print_section("Test 3: Available Citation Sources")

    response = requests.get(f"{BASE_URL}/api/local/citations/sources")

    print(f"Status: {response.status_code}")
    sources = response.json()

    # Count total sources
    total = 0
    for category, items in sources.items():
        if category != "metadata" and isinstance(items, list):
            count = len(items)
            total += count
            print(f"  {category}: {count} sources")

    print(f"\n  Total: {total} citation sources")

    # Show major platforms
    if "major_platforms" in sources:
        print(f"\n📌 Major Platforms:")
        for platform in sources["major_platforms"]:
            print(f"  • {platform['name']} (importance: {platform['importance']}/10)")

    return response.status_code == 200


def test_gbp_optimization():
    """Test Google Business Profile optimization"""
    print_section("Test 4: Google Business Profile Optimization")

    data = {
        "site_url": "https://example-business.com"
    }

    print("Request data:")
    pprint(data)
    print()

    response = requests.post(
        f"{BASE_URL}/api/local/gbp/optimize",
        json=data
    )

    print(f"Status: {response.status_code}")
    result = response.json()

    print(f"\n📊 GBP Scores:")
    print(f"  Completeness Score: {result['completeness_score']}/100")
    print(f"  Total GBP Score: {result['gbp_score']}/12 points")
    print(f"\n  Score Breakdown:")
    print(f"    • Profile Complete: {result['profile_complete_score']}/5 points")
    print(f"    • Verification: {result['verification_score']}/3 points")
    print(f"    • Regular Posts: {result['posting_score']}/2 points")
    print(f"    • Photos Updated: {result['photo_score']}/2 points")

    print(f"\n⚙️  Profile Status:")
    print(f"  • Verified: {'✓' if result['is_verified'] else '✗'}")
    print(f"  • Profile Complete: {'✓' if result['profile_complete'] else '✗'}")
    print(f"  • Regular Posts: {'✓' if result['has_regular_posts'] else '✗'}")
    print(f"  • Updated Photos: {'✓' if result['has_updated_photos'] else '✗'}")

    if result['missing_sections']:
        print(f"\n📋 Missing Sections ({len(result['missing_sections'])}):")
        for section in result['missing_sections']:
            print(f"  - {section}")

    if result['optimization_plan']:
        print(f"\n💡 Top 3 Optimization Actions:")
        for i, action in enumerate(result['optimization_plan'][:3], 1):
            print(f"  {i}. [{action['priority'].upper()}] {action['action']}")
            print(f"      → {action['impact']} ({action['timeframe']})")

    return response.status_code == 200


def test_local_schema_generation():
    """Test local schema markup generation"""
    print_section("Test 5: Local Schema Markup Generation")

    # Test with Restaurant type
    data = {
        "site_url": "https://example-restaurant.com",
        "business_type": "Restaurant",
        "include_service_area": True,
        "include_hours": True
    }

    print("Request data:")
    pprint(data)
    print()

    response = requests.post(
        f"{BASE_URL}/api/local/schema/generate",
        json=data
    )

    print(f"Status: {response.status_code}")
    result = response.json()

    print(f"\n📋 Schema Details:")
    print(f"  Detected Type: {result['detected_type']}")
    print(f"  Validation Status: {result['validation_status'].upper()}")
    print(f"  Rich Features: {len(result['rich_features_eligible'])}")

    if result['rich_features_eligible']:
        print(f"\n✨ Eligible Rich Results:")
        for feature in result['rich_features_eligible'][:5]:
            feature_name = feature.replace("_", " ").title()
            print(f"  • {feature_name}")

    print(f"\n🔍 Validation Messages:")
    for msg in result['validation_messages'][:3]:
        print(f"  • {msg}")

    # Check schema structure
    json_ld = result['json_ld']
    print(f"\n📊 Schema Structure:")
    print(f"  @type: {json_ld.get('@type')}")
    print(f"  Name: {json_ld.get('name')}")
    print(f"  Address: {'✓' if json_ld.get('address') else '✗'}")
    print(f"  Phone: {'✓' if json_ld.get('telephone') else '✗'}")
    print(f"  Hours: {'✓' if json_ld.get('openingHoursSpecification') else '✗'}")
    print(f"  Geo Coordinates: {'✓' if json_ld.get('geo') else '✗'}")

    # Check HTML snippet is present
    has_html_snippet = len(result['html_snippet']) > 100
    print(f"\n📝 HTML Snippet: {'✓ Generated' if has_html_snippet else '✗ Missing'}")

    # Check implementation guide
    has_guide = len(result['implementation_guide']) > 200
    print(f"📖 Implementation Guide: {'✓ Generated' if has_guide else '✗ Missing'}")

    return response.status_code == 200


def test_review_management():
    """Test review management and analysis"""
    print_section("Test 6: Review Management")

    data = {
        "site_url": "https://example-business.com",
        "business_name": "Example Business LLC",
        "platforms": ["Google", "Yelp"]
    }

    print("Request data:")
    pprint(data)
    print()

    response = requests.post(
        f"{BASE_URL}/api/local/reviews/analyze",
        json=data
    )

    print(f"Status: {response.status_code}")
    result = response.json()

    print(f"\n📊 Review Analysis:")
    print(f"  Total Reviews: {result['analysis']['total_reviews']}")
    print(f"  Average Rating: {result['analysis']['average_rating']}/5")
    print(f"  Response Rate: {result['analysis']['response_rate']:.0%}")
    print(f"  Review Score (GEO): {result['review_score']}/5")

    print(f"\n⭐ Rating Distribution:")
    for rating in [5, 4, 3, 2, 1]:
        count = result['analysis']['rating_distribution'][str(rating)]
        print(f"  {rating} stars: {count}")

    print(f"\n😊 Sentiment Breakdown:")
    for sentiment, count in result['analysis']['sentiment_breakdown'].items():
        print(f"  {sentiment.capitalize()}: {count}")

    print(f"\n🔑 Top Keywords:")
    for keyword, count in result['analysis']['common_keywords'][:5]:
        print(f"  • {keyword}: {count} times")

    if result['response_suggestions']:
        print(f"\n💬 Response Suggestions ({len(result['response_suggestions'])}):")
        for sugg in result['response_suggestions'][:2]:
            print(f"\n  Reviewer: {sugg['reviewer']} ({sugg['rating']}⭐)")
            print(f"  Platform: {sugg['platform']}")
            print(f"  → Suggested response: {sugg['suggested_response'][:80]}...")

    if result['reputation_recommendations']:
        print(f"\n💡 Top 3 Recommendations:")
        for rec in result['reputation_recommendations'][:3]:
            print(f"  • {rec}")

    return response.status_code == 200


def test_competitor_analysis():
    """Test local competitor analysis"""
    print_section("Test 7: Local Competitor Analysis")

    data = {
        "site_url": "https://example-business.com",
        "business_name": "Example Business LLC",
        "address": "123 Main Street, Anytown, CA 90210",
        "radius_miles": 5,
        "target_keywords": ["professional services", "business consulting"],
        "max_competitors": 5
    }

    print("Request data:")
    pprint(data)
    print()

    response = requests.post(
        f"{BASE_URL}/api/local/competitors/analyze",
        json=data
    )

    print(f"Status: {response.status_code}")
    result = response.json()

    print(f"\n📊 Competitor Landscape:")
    print(f"  Competitors Found: {len(result['competitors'])}")
    print(f"  Your Rank: #{result['comparison']['your_rank']} out of {result['comparison']['total_competitors'] + 1}")

    print(f"\n⭐ Your Metrics vs. Market Average:")
    print(f"  Google Rating: {result['comparison']['your_google_rating']} vs {result['comparison']['avg_google_rating']}")
    print(f"  Google Reviews: {result['comparison']['your_google_reviews']} vs {result['comparison']['avg_google_reviews']}")
    print(f"  Citations: {result['comparison']['your_citation_count']} vs {result['comparison']['avg_citation_count']}")
    print(f"  Response Rate: {result['comparison']['your_response_rate']:.0%} vs {result['comparison']['avg_response_rate']:.0%}")

    if result['competitors']:
        print(f"\n🏢 Top Competitors:")
        for i, comp in enumerate(result['competitors'][:3], 1):
            print(f"  {i}. {comp['name']}")
            print(f"      Distance: {comp['distance_miles']} miles")
            print(f"      Google: {comp['google_rating']}⭐ ({comp['google_reviews']} reviews)")
            print(f"      Citations: {comp['citation_count']}")

    if result['citation_gaps']:
        print(f"\n📋 Top Citation Gaps ({len(result['citation_gaps'])}):")
        for gap in result['citation_gaps'][:3]:
            print(f"  • {gap['source']} (importance: {gap['importance']}/10)")
            print(f"      → {gap['opportunity']}")

    if result['keyword_gaps']:
        print(f"\n🔑 Keyword Opportunities ({len(result['keyword_gaps'])}):")
        for gap in result['keyword_gaps'][:3]:
            print(f"  • \"{gap['source']}\" - {len(gap['competitors_using'])} competitors ranking")

    if result['recommendations']:
        print(f"\n💡 Top 3 Strategic Recommendations:")
        for rec in result['recommendations'][:3]:
            print(f"  • {rec}")

    print(f"\n✅ Strengths:")
    for strength in result['comparison']['strengths'][:3]:
        print(f"  • {strength}")

    print(f"\n⚠️  Weaknesses:")
    for weakness in result['comparison']['weaknesses'][:3]:
        print(f"  • {weakness}")

    return response.status_code == 200


def test_stubbed_endpoints():
    """Test that stubbed endpoints return 501"""
    print_section("Test 8: Stubbed Endpoints (Phase 8)")

    endpoints = [
        ("Complete GEO Audit", "POST", "/api/local/geo/audit", {
            "site_url": "https://example.com",
            "business_name": "Example Business",
            "address": "123 Main St",
            "phone": "(555) 123-4567"
        })
    ]

    all_correct = True
    for name, method, endpoint, data in endpoints:
        if method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", json=data)
        else:
            response = requests.get(f"{BASE_URL}{endpoint}")

        expected = 501  # Not Implemented
        status = "✓" if response.status_code == expected else "✗"
        print(f"  {status} {name}: {response.status_code}")

        if response.status_code == expected:
            print(f"      → {response.json()['detail']}")

        all_correct = all_correct and (response.status_code == expected)

    return all_correct


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  WEEK 14: LOCAL SEO & GEO ENHANCEMENT ENGINE")
    print("  Phase 1-6: Full Local SEO Stack - TESTING")
    print("=" * 60)

    tests = [
        ("Local SEO Health Check", test_local_health),
        ("Citation Audit - Perfect NAP", test_citation_audit_perfect),
        ("Citation Audit - With Inconsistencies", test_citation_audit_inconsistent),
        ("Get Citation Sources", test_get_citation_sources),
        ("Google Business Profile Optimization", test_gbp_optimization),
        ("Local Schema Markup Generation", test_local_schema_generation),
        ("Review Management", test_review_management),
        ("Local Competitor Analysis", test_competitor_analysis),
        ("Stubbed Endpoints Check", test_stubbed_endpoints)
    ]

    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n❌ Error in {name}: {str(e)}")
            results.append((name, False))

    # Summary
    print_section("Test Summary")
    passed = sum(1 for _, success in results if success)
    total = len(results)

    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status}: {name}")

    print(f"\n  Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n  🎉 All tests passed! Phases 1-6 complete.")
    else:
        print(f"\n  ⚠️  {total - passed} test(s) failed.")

    print("\n" + "=" * 60)

    return passed == total


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
