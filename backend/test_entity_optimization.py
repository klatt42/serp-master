#!/usr/bin/env python3
"""
Test Entity Optimization APIs (Week 13)
Comprehensive testing of all entity optimization features
"""

import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
TIMEOUT = 30.0


async def test_entity_health():
    """Test entity optimization health endpoint"""
    print("\n" + "="*70)
    print("TEST 1: Entity Optimization Health Check")
    print("="*70)

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(f"{BASE_URL}/api/entity/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        print("✅ Health check passed")
        return True


async def test_business_descriptions():
    """Test business description generation"""
    print("\n" + "="*70)
    print("TEST 2: Business Description Generation")
    print("="*70)

    request_data = {
        "site_url": "https://example-plumbing.com",
        "business_name": "Example Plumbing Services",
        "industry": "plumbing services",
        "location": "Austin, TX",
        "target_keywords": ["plumber", "emergency plumbing", "water heater"],
        "existing_description": "We are a local plumbing company serving Austin since 2010."
    }

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.post(
            f"{BASE_URL}/api/entity/descriptions/generate",
            json=request_data
        )
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"\n📝 Generated {len(data['variations'])} description variations")
            print(f"\nTop Description (Score: {data['variations'][0]['overall_score']}/100):")
            print(f"  {data['variations'][0]['description']}")
            print(f"\n  SEO Score: {data['variations'][0]['seo_score']}/100")
            print(f"  Local Relevance: {data['variations'][0]['local_relevance_score']}/100")
            print(f"  Entity Clarity: {data['variations'][0]['entity_clarity_score']}/100")
            print(f"  Readability: {data['variations'][0]['readability_score']}/100")
            print(f"\n  Keywords Included: {', '.join(data['variations'][0]['keywords_included'])}")
            print(f"  Location Mentioned: {'Yes' if data['variations'][0]['location_mentioned'] else 'No'}")

            print(f"\n💡 Recommendations ({len(data['recommendations'])}):")
            for i, rec in enumerate(data['recommendations'][:3], 1):
                print(f"  {i}. {rec}")

            print("✅ Business description generation passed")
            return True
        else:
            print(f"❌ Failed: {response.text}")
            return False


async def test_schema_generation():
    """Test schema markup generation"""
    print("\n" + "="*70)
    print("TEST 3: Schema Markup Generation")
    print("="*70)

    request_data = {
        "site_url": "https://example-plumbing.com",
        "business_type": "Plumber",
        "generate_types": ["Organization", "LocalBusiness", "Service"]
    }

    site_data = {
        "business_name": "Example Plumbing Services",
        "description": "Professional plumbing services in Austin, TX since 2010",
        "phone": "(512) 555-0123",
        "address": {
            "street": "123 Main St",
            "city": "Austin",
            "state": "TX",
            "zip": "78701"
        },
        "logo": "/logo.png",
        "services": [
            {"name": "Emergency Plumbing", "type": "Emergency Services"},
            {"name": "Water Heater Installation", "type": "Installation"}
        ]
    }

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.post(
            f"{BASE_URL}/api/entity/schema/generate",
            json={"request": request_data, "site_data": site_data}
        )
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"\n📋 Generated {len(data['schemas'])} schema markups")

            for i, schema in enumerate(data['schemas'], 1):
                print(f"\n  Schema {i}: {schema['schema_type']}")
                print(f"    Validation: {schema['validation_status']}")
                print(f"    Rich Snippet Eligible: {'Yes' if schema['rich_snippet_eligible'] else 'No'}")
                print(f"    Validation Messages: {len(schema['validation_messages'])}")

                # Show first 500 chars of HTML snippet
                snippet_preview = schema['html_snippet'][:500]
                print(f"\n    HTML Snippet Preview:")
                print(f"    {snippet_preview}...")

            print(f"\n💡 Recommendations ({len(data['recommendations'])}):")
            for i, rec in enumerate(data['recommendations'][:3], 1):
                print(f"  {i}. {rec}")

            print("✅ Schema generation passed")
            return True
        else:
            print(f"❌ Failed: {response.text}")
            return False


async def test_relationship_analysis():
    """Test entity relationship analysis"""
    print("\n" + "="*70)
    print("TEST 4: Entity Relationship Analysis")
    print("="*70)

    request_data = {
        "site_url": "https://example-law-firm.com"
    }

    site_data = {
        "content": "Founded in 2005, our firm is a member of the American Bar Association and certified by the Texas State Bar. We've won multiple Best Law Firm awards.",
        "about_content": "Our attorneys graduated from Harvard Law School and Stanford Law School. We're BBB accredited with an A+ rating.",
        "certifications_content": "Board Certified, Texas State Bar Certified, ABA Member since 2005"
    }

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.post(
            f"{BASE_URL}/api/entity/relationships/analyze",
            json={"request": request_data, "site_data": site_data}
        )
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"\n🔗 Found {len(data['relationships'])} entity relationships")

            # Group by category
            by_category = {}
            for rel in data['relationships']:
                cat = rel['relationship_type']
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(rel)

            for category, rels in by_category.items():
                print(f"\n  {category.title()} ({len(rels)}):")
                for rel in rels[:3]:  # Show top 3 per category
                    print(f"    • {rel['entity_name']} (Authority: {rel['authority_score']}/10, Relevance: {rel['relevance_score']}/10)")
                    print(f"      Trust Signal: {rel['trust_signal_strength']} | Schema Opportunity: {rel['schema_opportunity']}")

            print(f"\n📊 Authority Summary:")
            for key, value in data['authority_summary'].items():
                print(f"  {key.replace('_', ' ').title()}: {value}")

            print(f"\n⚠️ Missing Opportunities ({len(data['missing_opportunities'])}):")
            for i, opp in enumerate(data['missing_opportunities'][:3], 1):
                print(f"  {i}. {opp}")

            print("✅ Relationship analysis passed")
            return True
        else:
            print(f"❌ Failed: {response.text}")
            return False


async def test_about_page_optimization():
    """Test About page optimization"""
    print("\n" + "="*70)
    print("TEST 5: About Page Optimization")
    print("="*70)

    request_data = {
        "site_url": "https://example-company.com"
    }

    site_data = {
        "about_content": """
        Example Company was founded in 2010 by John Smith, a certified professional with 15 years of experience.
        Our team of 25+ professionals serves clients across Texas. We're committed to quality and excellence.
        Contact us at (512) 555-0123 or hello@example.com.
        """,
        "about_images_count": 3
    }

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.post(
            f"{BASE_URL}/api/entity/about-page/optimize",
            json={"request": request_data, "site_data": site_data}
        )
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            metrics = data['current_metrics']

            print(f"\n📊 Current Metrics:")
            print(f"  Overall Quality Score: {metrics['overall_quality_score']}/100")
            print(f"  Word Count: {metrics['word_count']}")
            print(f"  Entity Mentions: {metrics['entity_mentions']}")
            print(f"  Trust Signals: {metrics['trust_signals_count']}")
            print(f"  Team Members Mentioned: {metrics['team_members_mentioned']}")
            print(f"  Achievements Mentioned: {metrics['achievements_mentioned']}")
            print(f"  Contact Info Complete: {metrics['contact_info_complete']}")
            print(f"  Visual Content: {metrics['visual_content_count']}")

            print(f"\n⚠️ Missing Elements ({len(data['missing_elements'])}):")
            for i, element in enumerate(data['missing_elements'][:5], 1):
                print(f"  {i}. {element}")

            print(f"\n💡 Content Suggestions ({len(data['content_suggestions'])}):")
            for i, suggestion in enumerate(data['content_suggestions'][:3], 1):
                print(f"  {i}. {suggestion['section']} (Priority: {suggestion['priority']})")
                print(f"      {suggestion['content'][:100]}...")

            print("✅ About page optimization passed")
            return True
        else:
            print(f"❌ Failed: {response.text}")
            return False


async def test_nap_validation():
    """Test NAP consistency validation"""
    print("\n" + "="*70)
    print("TEST 6: NAP Consistency Validation")
    print("="*70)

    request_data = {
        "site_url": "https://example-company.com"
    }

    site_data = {
        "business_name": "Example Company LLC",
        "phone": "(512) 555-0123",
        "address": "123 Main St, Austin, TX 78701",
        "content": "Example Company - Call us at 512-555-0123. Located at 123 Main Street, Austin, Texas 78701",
        "footer_content": "Example Co | (512) 555-0123 | 123 Main St, Austin TX 78701",
        "existing_schema": [{
            "@type": "Organization",
            "name": "Example Company LLC",
            "telephone": "(512) 555-0123",
            "address": {
                "streetAddress": "123 Main St",
                "addressLocality": "Austin",
                "addressRegion": "TX",
                "postalCode": "78701"
            }
        }]
    }

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.post(
            f"{BASE_URL}/api/entity/nap/validate",
            json={"request": request_data, "site_data": site_data}
        )
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            print(f"\n📍 NAP Data Found ({len(data['nap_data_found'])} sources):")
            for nap in data['nap_data_found']:
                print(f"\n  Source: {nap['source']}")
                print(f"    Name: {nap['business_name']}")
                print(f"    Phone: {nap['phone']}")
                print(f"    Address: {nap['address'][:60]}..." if len(nap['address']) > 60 else f"    Address: {nap['address']}")

            print(f"\n🔍 Consistency Score: {data['consistency_score']}/100")

            if data['inconsistencies']:
                print(f"\n⚠️ Inconsistencies Detected ({len(data['inconsistencies'])}):")
                for inc in data['inconsistencies'][:5]:
                    print(f"  • {inc['field']} ({inc['severity']}): {inc['issue_type']}")
                    print(f"    Sources: {', '.join(inc['sources'])}")
                    print(f"    Suggestion: {inc['suggestion']}")
            else:
                print(f"\n✅ No inconsistencies detected!")

            print(f"\n✅ Standardized NAP:")
            std_nap = data['standardized_nap']
            print(f"  Name: {std_nap['business_name']}")
            print(f"  Phone: {std_nap['phone']}")
            print(f"  Address: {std_nap['address']}")

            print(f"\n💡 Recommendations ({len(data['recommendations'])}):")
            for i, rec in enumerate(data['recommendations'][:3], 1):
                print(f"  {i}. {rec}")

            print("✅ NAP validation passed")
            return True
        else:
            print(f"❌ Failed: {response.text}")
            return False


async def test_full_entity_optimization():
    """Test full entity optimization (all features combined)"""
    print("\n" + "="*70)
    print("TEST 7: Full Entity Optimization")
    print("="*70)

    request_data = {
        "site_url": "https://example-business.com",
        "business_name": "Example Business",
        "include_description": True,
        "include_schema": True,
        "include_relationships": True,
        "include_about_page": True,
        "include_nap": True
    }

    site_data = {
        "business_name": "Example Business",
        "industry": "professional services",
        "location": "Austin, TX",
        "keywords": ["consulting", "business services"],
        "meta_description": "Professional business consulting in Austin",
        "phone": "(512) 555-0123",
        "address": {"street": "123 Main St", "city": "Austin", "state": "TX", "zip": "78701"},
        "content": "Founded 2015. BBB Accredited. 10+ years experience.",
        "about_content": "We are a certified consulting firm in Austin, Texas."
    }

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.post(
            f"{BASE_URL}/api/entity/optimize",
            json={"request": request_data, "site_data": site_data}
        )
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            scores = data['scores']

            print(f"\n📊 Entity Optimization Scores:")
            print(f"  Overall Score: {scores['overall_score']}/100")
            print(f"  Description Score: {scores['description_score']}/100")
            print(f"  Schema Score: {scores['schema_score']}/100")
            print(f"  Relationship Score: {scores['relationship_score']}/100")
            print(f"  About Page Score: {scores['about_page_score']}/100")
            print(f"  NAP Consistency Score: {scores['nap_consistency_score']}/100")

            print(f"\n⚡ Quick Wins ({len(data['quick_wins'])}):")
            for i, win in enumerate(data['quick_wins'][:3], 1):
                print(f"  {i}. {win['title']} (Effort: {win['effort']})")
                print(f"      {win['description']}")

            print(f"\n🎯 Priority Actions ({len(data['priority_actions'])}):")
            for i, action in enumerate(data['priority_actions'][:3], 1):
                priority_emoji = ["🔴", "🟡", "🟢", "✅"][action['priority'] - 1]
                print(f"  {i}. {priority_emoji} {action['title']}")
                print(f"      {action['description']}")
                print(f"      Action: {action['action']}")

            # Component results
            if data.get('business_descriptions'):
                print(f"\n✅ Business Descriptions: {len(data['business_descriptions']['variations'])} variations generated")

            if data.get('schema_markups'):
                print(f"✅ Schema Markups: {len(data['schema_markups']['schemas'])} schemas generated")

            if data.get('relationships'):
                print(f"✅ Relationships: {len(data['relationships']['relationships'])} relationships found")

            if data.get('about_page_analysis'):
                print(f"✅ About Page: Quality score {data['about_page_analysis']['current_metrics']['overall_quality_score']}/100")

            if data.get('nap_validation'):
                print(f"✅ NAP Validation: Consistency score {data['nap_validation']['consistency_score']}/100")

            print("\n✅ Full entity optimization passed")
            return True
        else:
            print(f"❌ Failed: {response.text}")
            return False


async def test_schema_templates():
    """Test schema templates endpoint"""
    print("\n" + "="*70)
    print("TEST 8: Schema Templates")
    print("="*70)

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(f"{BASE_URL}/api/entity/schema/templates")
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"\n📋 Available Schema Templates ({len(data['templates'])}):")

            for i, template in enumerate(data['templates'], 1):
                print(f"\n  {i}. {template['type']}")
                print(f"     Description: {template['description']}")
                print(f"     Use Case: {template['use_case']}")
                print(f"     Required Fields: {', '.join(template['required_fields'])}")

            print("✅ Schema templates passed")
            return True
        else:
            print(f"❌ Failed: {response.text}")
            return False


async def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("ENTITY OPTIMIZATION API TESTS (WEEK 13)")
    print("="*70)
    print(f"Testing against: {BASE_URL}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    tests = [
        ("Health Check", test_entity_health),
        ("Business Descriptions", test_business_descriptions),
        ("Schema Generation", test_schema_generation),
        ("Relationship Analysis", test_relationship_analysis),
        ("About Page Optimization", test_about_page_optimization),
        ("NAP Validation", test_nap_validation),
        ("Full Entity Optimization", test_full_entity_optimization),
        ("Schema Templates", test_schema_templates),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test failed with exception: {str(e)}")
            results.append((name, False))

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    print(f"\nTotal: {passed}/{total} tests passed ({int(passed/total*100)}%)")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")

    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    asyncio.run(main())
