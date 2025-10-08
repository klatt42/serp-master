"""
Test script for Week 9: Platform Intelligence & Intent Matching
Tests all platform intelligence API endpoints
"""

import requests
import json
from time import sleep

API_URL = "http://localhost:8000"


def print_test_header(test_name):
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print(f"{'='*60}")


def test_supported_platforms():
    """Test GET /api/platform/platforms endpoint"""
    print_test_header("Get Supported Platforms")

    try:
        response = requests.get(f"{API_URL}/api/platform/platforms")
        response.raise_for_status()

        data = response.json()
        print(f"✓ Status Code: {response.status_code}")
        print(f"✓ Success: {data.get('success')}")
        print(f"✓ Number of platforms: {len(data.get('platforms', []))}")

        print("\nPlatforms:")
        for platform in data.get('platforms', []):
            print(f"  - {platform['name']} ({platform['id']})")
            print(f"    Intent: {platform['intent']}")
            print(f"    Content Type: {platform['content_type']}")

        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def test_intent_analysis():
    """Test POST /api/platform/intent endpoint"""
    print_test_header("Intent Analysis")

    payload = {
        "keywords": [
            "how to lose weight",
            "buy protein powder",
            "best gym equipment",
            "keto diet review",
            "trending workout"
        ]
    }

    try:
        response = requests.post(
            f"{API_URL}/api/platform/intent",
            json=payload
        )
        response.raise_for_status()

        data = response.json()
        print(f"✓ Status Code: {response.status_code}")
        print(f"✓ Success: {data.get('success')}")

        insights = data.get('data', {}).get('insights', {})
        print(f"\nIntent Distribution:")
        for intent, percentage in insights.get('intent_distribution', {}).items():
            print(f"  {intent}: {percentage}%")

        print(f"\nTop Platforms:")
        for platform, info in insights.get('top_platforms', [])[:3]:
            print(f"  {platform}: {info['count']} keywords")

        print(f"\nSample Classifications:")
        for classification in data.get('data', {}).get('classifications', [])[:3]:
            print(f"  Keyword: {classification['keyword']}")
            print(f"    Primary Intent: {classification['primary_intent']}")
            print(f"    Confidence: {classification['confidence']}")

        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def test_platform_analysis():
    """Test POST /api/platform/analyze endpoint"""
    print_test_header("Platform Analysis")

    payload = {
        "keywords": ["fitness", "nutrition"],
        "platforms": ["youtube", "tiktok", "amazon"],
        "location": "United States"
    }

    try:
        response = requests.post(
            f"{API_URL}/api/platform/analyze",
            json=payload
        )
        response.raise_for_status()

        data = response.json()
        print(f"✓ Status Code: {response.status_code}")
        print(f"✓ Success: {data.get('success')}")

        summary = data.get('summary', {})
        print(f"\nSummary:")
        print(f"  Platforms Analyzed: {summary.get('platforms_analyzed')}")
        print(f"  Keywords Analyzed: {summary.get('keywords_analyzed')}")
        print(f"  Cross-Platform Opportunities: {summary.get('cross_platform_opportunities')}")

        platform_data = data.get('data', {}).get('platforms', {})
        print(f"\nPlatform Results:")
        for platform_name, platform_info in platform_data.items():
            print(f"  {platform_name}:")
            if platform_name == 'youtube':
                print(f"    Keywords: {len(platform_info.get('keywords', []))}")
            elif platform_name == 'tiktok':
                print(f"    Content Ideas: {len(platform_info.get('content_ideas', []))}")
            elif platform_name == 'amazon':
                print(f"    Product Keywords: {len(platform_info.get('product_keywords', []))}")

        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def test_multi_platform_strategy():
    """Test POST /api/platform/strategy endpoint"""
    print_test_header("Multi-Platform Strategy Generation")

    payload = {
        "niche_keywords": ["weight loss", "healthy eating"],
        "target_platforms": ["youtube", "tiktok", "amazon", "reddit"],
        "location": "United States"
    }

    try:
        response = requests.post(
            f"{API_URL}/api/platform/strategy",
            json=payload
        )
        response.raise_for_status()

        data = response.json()
        print(f"✓ Status Code: {response.status_code}")
        print(f"✓ Success: {data.get('success')}")

        summary = data.get('summary', {})
        print(f"\nStrategy Summary:")
        print(f"  Platforms Covered: {summary.get('platforms_covered')}")
        print(f"  Content Opportunities: {summary.get('content_opportunities')}")
        print(f"  Cross-Platform Ideas: {summary.get('cross_platform_ideas')}")
        print(f"  Recommended Focus: {summary.get('recommended_focus')}")

        unified_strategy = data.get('data', {}).get('unified_strategy', {})
        print(f"\nUnified Strategy:")
        print(f"  Priority Platform: {unified_strategy.get('priority_platform')}")
        print(f"  Dominant Intent: {unified_strategy.get('dominant_intent')}")

        print(f"\nImmediate Actions:")
        for action in unified_strategy.get('immediate_actions', [])[:3]:
            print(f"  - {action}")

        print(f"\nCross-Platform Workflow Steps:")
        for step in unified_strategy.get('cross_platform_workflow', []):
            print(f"  Step {step['step']}: {step['action']}")

        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def main():
    print("\n" + "="*60)
    print("WEEK 9: PLATFORM INTELLIGENCE API TEST SUITE")
    print("="*60)

    results = []

    # Test 1: Get supported platforms
    results.append(("Supported Platforms", test_supported_platforms()))
    sleep(1)

    # Test 2: Intent analysis
    results.append(("Intent Analysis", test_intent_analysis()))
    sleep(1)

    # Test 3: Platform analysis
    results.append(("Platform Analysis", test_platform_analysis()))
    sleep(1)

    # Test 4: Multi-platform strategy
    results.append(("Multi-Platform Strategy", test_multi_platform_strategy()))

    # Print summary
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Week 9 Platform Intelligence is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the errors above.")


if __name__ == "__main__":
    main()
