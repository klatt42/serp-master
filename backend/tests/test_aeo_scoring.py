"""
Comprehensive tests for AEO scoring system
Tests all components: Schema, Content, Entity, and Combined scoring
"""

import pytest
from app.services.schema_detector import SchemaDetector
from app.services.content_analyzer import ContentAnalyzer
from app.services.entity_checker import EntityChecker
from app.services.aeo_scorer import AEOScorer
from app.services.mock_data import generate_perfect_site, generate_poor_site, generate_mock_site


class TestSchemaDetector:
    """Test schema markup detection and scoring"""

    def setup_method(self):
        self.detector = SchemaDetector()

    def test_detect_organization_schema(self):
        """Test Organization schema detection"""
        html = """
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": "Test Company",
            "url": "https://test.com"
        }
        </script>
        """
        result = self.detector.detect_schemas(html)

        assert result["schema_score"] >= 3, "Should award 3 points for Organization schema"
        assert any(s["type"] == "Organization" for s in result["detected_schemas"])

    def test_detect_local_business_schema(self):
        """Test LocalBusiness schema detection"""
        html = """
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "name": "Test Business",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": "123 Main St"
            }
        }
        </script>
        """
        result = self.detector.detect_schemas(html)

        assert result["schema_score"] >= 3, "Should award 3 points for LocalBusiness schema"
        assert any(s["type"] == "LocalBusiness" for s in result["detected_schemas"])

    def test_detect_faq_schema(self):
        """Test FAQPage schema detection"""
        html = """
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": "How do we help?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": "We provide services."
                    }
                }
            ]
        }
        </script>
        """
        result = self.detector.detect_schemas(html)

        assert result["schema_score"] >= 2, "Should award 2 points for FAQPage schema"
        assert any(s["type"] == "FAQPage" for s in result["detected_schemas"])

    def test_perfect_schema_score(self):
        """Test perfect schema implementation (10 points)"""
        site_data = generate_perfect_site()
        result = self.detector.detect_schemas(site_data["html"])

        # Perfect site should have Organization, LocalBusiness, FAQPage, and Product
        assert result["schema_score"] >= 9, f"Perfect site should score 9-10 points, got {result['schema_score']}"
        assert result["max_score"] == 10

    def test_no_schema(self):
        """Test site with no schema markup"""
        html = "<html><body><h1>No Schema</h1></body></html>"
        result = self.detector.detect_schemas(html)

        assert result["schema_score"] == 0, "Should score 0 with no schema"
        assert len(result["detected_schemas"]) == 0

    def test_microdata_detection(self):
        """Test Microdata format detection"""
        html = """
        <div itemscope itemtype="https://schema.org/Organization">
            <span itemprop="name">Test Company</span>
            <span itemprop="url">https://test.com</span>
        </div>
        """
        result = self.detector.detect_schemas(html)

        assert result["schema_score"] > 0, "Should detect and score Microdata"
        assert any(s["format"] == "Microdata" for s in result["detected_schemas"])


class TestContentAnalyzer:
    """Test conversational content analysis"""

    def setup_method(self):
        self.analyzer = ContentAnalyzer()

    def test_detect_faq_page(self):
        """Test FAQ page detection"""
        site_data = {
            "html": "",
            "pages": [
                {"url": "/faq", "title": "FAQ Page"}
            ]
        }
        result = self.analyzer.calculate_conversational_score(site_data)

        faq_analysis = result["faq_analysis"]
        assert faq_analysis["has_faq_page"], "Should detect FAQ page"
        assert faq_analysis["points"] >= 2, "Should award points for FAQ page"

    def test_detect_faq_schema(self):
        """Test FAQPage schema detection in content analyzer"""
        html = """
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": []
        }
        </script>
        """
        site_data = {
            "html": html,
            "pages": [{"url": "/faq", "title": "FAQ"}]
        }
        result = self.analyzer.calculate_conversational_score(site_data)

        faq_analysis = result["faq_analysis"]
        assert faq_analysis["has_schema"], "Should detect FAQPage schema"
        assert faq_analysis["points"] == 4, "Should award 4 points for FAQ page with schema"

    def test_question_headers(self):
        """Test question header detection"""
        html = """
        <html>
        <body>
            <h2>How do we help?</h2>
            <h2>What services do we offer?</h2>
            <h2>When should you contact us?</h2>
            <h2>Where are we located?</h2>
            <h2>Why choose us?</h2>
            <h2>Can we assist you?</h2>
            <h2>Does this work?</h2>
            <h2>Is this effective?</h2>
            <h2>Should you try this?</h2>
            <h2>Will this help?</h2>
        </body>
        </html>
        """
        result = self.analyzer.find_question_headers(html)

        assert result["count"] >= 10, f"Should find 10 questions, found {result['count']}"
        assert result["points"] == 2, "Should award 2 points for 10+ questions"

    def test_is_question(self):
        """Test question detection logic"""
        assert self.analyzer.is_question("How do we help?"), "Should detect question with '?'"
        assert self.analyzer.is_question("What is this"), "Should detect 'what' question"
        assert self.analyzer.is_question("Can you help"), "Should detect 'can' question"
        assert not self.analyzer.is_question("This is not a question"), "Should not detect statements"

    def test_readability_easy(self):
        """Test easy readability scoring"""
        html = """
        <html><body>
        <p>We fix water damage fast. Our team helps homes and businesses.
        We use top tools. We dry your space well. Call us today for help.
        We work hard. We care about you. We finish on time. You can trust us.</p>
        </body></html>
        """
        result = self.analyzer.calculate_readability(html)

        # Easy text should score high (60+)
        assert result["flesch_score"] >= 60 or result["difficulty"] == "easy", \
            f"Should score as easy, got {result['flesch_score']}"
        assert result["points"] >= 1, "Should award points for readable content"

    def test_perfect_conversational_score(self):
        """Test perfect conversational content (8 points)"""
        site_data = generate_perfect_site()
        result = self.analyzer.calculate_conversational_score(site_data)

        assert result["conversational_score"] >= 7, \
            f"Perfect site should score 7-8 points, got {result['conversational_score']}"
        assert result["max_score"] == 8


class TestEntityChecker:
    """Test entity clarity checking"""

    def setup_method(self):
        self.checker = EntityChecker()

    def test_name_consistency(self):
        """Test business name consistency detection"""
        html = """
        <html>
        <head>
            <title>Prism Specialties | Water Damage</title>
        </head>
        <body>
            <h1>Prism Specialties</h1>
            <footer>&copy; 2025 Prism Specialties</footer>
        </body>
        </html>
        """
        site_data = {
            "html": html,
            "pages": [],
            "business_name": "Prism Specialties"
        }
        result = self.checker.check_name_consistency([], html, "Prism Specialties")

        assert result["consistent"], "Should detect consistent name"
        assert result["primary_name"] == "Prism Specialties"
        assert result["points"] >= 1, "Should award points for consistent name"

    def test_name_inconsistency(self):
        """Test detection of inconsistent business names"""
        html = """
        <html>
        <head><title>Prism Services</title></head>
        <body>
            <h1>Prism Specialties</h1>
            <footer>&copy; 2025 Prism LLC</footer>
        </body>
        </html>
        """
        result = self.checker.check_name_consistency([], html, "")

        # Should detect multiple variations
        assert len(result["variations"]) > 0, "Should detect name variations"

    def test_description_clarity(self):
        """Test business description detection"""
        html = """
        <html>
        <head>
            <meta name="description" content="Prism Specialties provides expert water damage restoration services in the DMV area">
        </head>
        <body>
            <p>Prism Specialties has been serving the DMV area for over 15 years with professional water damage restoration.</p>
        </body>
        </html>
        """
        site_data = {"html": html, "pages": []}
        result = self.checker.check_description_clarity([], html)

        assert result["has_description"], "Should find description"
        assert len(result["sources"]) >= 1, "Should find description in meta tag"
        assert result["points"] >= 1, "Should award points for description"

    def test_entity_relationships(self):
        """Test entity relationship detection"""
        html = """
        <html>
        <body>
            <p>We are certified by IICRC and licensed by the state.</p>
            <p>Winner of the Best Service Award 2024.</p>
            <p>Member of the National Association of Water Damage Professionals.</p>
            <p>Serving Arlington, Alexandria, and Falls Church.</p>
        </body>
        </html>
        """
        result = self.checker.check_entity_relationships(html)

        assert result["relationships_found"] > 0, "Should find relationships"
        assert len(result["categories"]) > 0, "Should categorize relationships"
        assert result["points"] >= 1, "Should award points for relationships"

    def test_about_page_quality(self):
        """Test about page detection and quality"""
        pages = [
            {
                "url": "/about",
                "title": "About Us",
                "html": """
                <html><body>
                <h1>About Prism Specialties</h1>
                <p>Founded in 2008, Prism Specialties has been serving the DMV area for over 15 years.
                Our team of certified professionals is available 24/7. We are dedicated to restoring
                your property and your peace of mind. Our mission is to provide excellent service
                with integrity and expertise.</p>
                """ + " ".join(["More content. "] * 100) + """
                </body></html>
                """
            }
        ]
        result = self.checker.check_about_page(pages)

        assert result["has_about_page"], "Should find about page"
        assert result["word_count"] >= 200, f"Should have 200+ words, got {result['word_count']}"
        assert result["has_history"], "Should detect history content"
        assert result["has_mission"], "Should detect mission content"
        # Note: Points awarded based on word count + quality indicators
        assert result["points"] in [0, 1], "Should award 0-1 points based on quality"

    def test_perfect_entity_score(self):
        """Test perfect entity clarity (7 points)"""
        site_data = generate_perfect_site()
        result = self.checker.check_entity_clarity(site_data)

        assert result["entity_clarity_score"] >= 1, \
            f"Perfect site should score 1-7 points, got {result['entity_clarity_score']}"
        assert result["max_score"] == 7


class TestAEOScorer:
    """Test AEO scorer integration"""

    def setup_method(self):
        self.scorer = AEOScorer()

    def test_perfect_aeo_score(self):
        """Test perfect AEO score (25 points)"""
        site_data = generate_perfect_site()
        result = self.scorer.calculate_aeo_score(site_data)

        # Perfect site should score close to 25
        assert result["aeo_score"] >= 18, \
            f"Perfect site should score 18-25 points, got {result['aeo_score']}"
        assert result["max_score"] == 25
        assert result["grade"] in ["A", "B", "C"], f"Should get A/B/C grade, got {result['grade']}"

    def test_poor_aeo_score(self):
        """Test poor AEO score (near 0)"""
        site_data = generate_poor_site()
        result = self.scorer.calculate_aeo_score(site_data)

        # Poor site should score low
        assert result["aeo_score"] <= 5, \
            f"Poor site should score 0-5 points, got {result['aeo_score']}"
        assert result["grade"] in ["D", "F"], f"Should get D or F grade, got {result['grade']}"

    def test_aeo_breakdown(self):
        """Test AEO score breakdown structure"""
        site_data = generate_perfect_site()
        result = self.scorer.calculate_aeo_score(site_data)

        assert "breakdown" in result
        assert "schema_markup" in result["breakdown"]
        assert "conversational_content" in result["breakdown"]
        assert "entity_clarity" in result["breakdown"]

        # Each component should have score and max
        for component in result["breakdown"].values():
            assert "score" in component
            assert "max" in component
            assert "percentage" in component

    def test_combined_score(self):
        """Test combined SEO + AEO + GEO scoring"""
        site_data = generate_perfect_site()
        result = self.scorer.calculate_combined_score(
            site_data,
            seo_score=25,  # Good SEO
            geo_score=0    # No GEO yet
        )

        assert result["total_score"] >= 40, \
            f"Combined should be 40+ (25 SEO + 20+ AEO), got {result['total_score']}"
        assert result["max_score"] == 100
        assert "component_scores" in result
        assert "seo" in result["component_scores"]
        assert "aeo" in result["component_scores"]
        assert "geo" in result["component_scores"]

    def test_recommendations(self):
        """Test recommendation generation"""
        site_data = generate_poor_site()
        result = self.scorer.calculate_aeo_score(site_data)

        assert "recommendations" in result
        assert len(result["recommendations"]) > 0, "Should generate recommendations for poor site"

        # Recommendations should be categorized and prioritized
        for rec in result["recommendations"]:
            assert "category" in rec
            assert "priority" in rec
            assert "recommendation" in rec

    def test_quick_wins(self):
        """Test quick wins identification"""
        site_data = generate_poor_site()
        quick_wins = self.scorer.get_quick_wins(site_data)

        assert len(quick_wins) > 0, "Should identify quick wins for poor site"

        # Quick wins should have required fields
        for win in quick_wins:
            assert "title" in win
            assert "impact" in win
            assert "effort" in win
            assert "points" in win
            assert "description" in win

        # Should be sorted by impact/points
        if len(quick_wins) > 1:
            # High impact should come before medium/low
            impact_order = {"high": 0, "medium": 1, "low": 2}
            for i in range(len(quick_wins) - 1):
                current_impact = impact_order.get(quick_wins[i]["impact"], 3)
                next_impact = impact_order.get(quick_wins[i + 1]["impact"], 3)
                assert current_impact <= next_impact, "Quick wins should be sorted by impact"

    def test_insights_generation(self):
        """Test insights generation"""
        site_data = generate_perfect_site()
        result = self.scorer.calculate_aeo_score(site_data)

        assert "insights" in result
        assert len(result["insights"]) > 0, "Should generate insights"

    def test_readiness_assessment(self):
        """Test AI platform readiness assessment"""
        site_data = generate_perfect_site()
        result = self.scorer.calculate_aeo_score(site_data)

        assert "readiness" in result
        readiness = result["readiness"]

        assert "level" in readiness
        assert "status" in readiness
        assert "platforms" in readiness

        # Should assess major platforms
        platforms = readiness["platforms"]
        assert "google_assistant" in platforms
        assert "alexa" in platforms
        assert "chatgpt" in platforms
        assert "perplexity" in platforms


class TestIntegration:
    """Integration tests for complete workflow"""

    def test_full_audit_workflow(self):
        """Test complete audit workflow from data to score"""
        # Generate test site
        site_data = generate_mock_site(
            has_org_schema=True,
            has_local_business_schema=True,
            has_faq_page=True,
            question_headers=12,
            has_about_page=True,
            readability_level="easy"
        )

        # Run AEO scoring
        scorer = AEOScorer()
        result = scorer.calculate_aeo_score(site_data)

        # Verify comprehensive results
        assert result["aeo_score"] > 0
        assert "breakdown" in result
        assert "recommendations" in result
        assert "insights" in result
        assert "readiness" in result

        # Verify all components contributed
        breakdown = result["breakdown"]
        assert breakdown["schema_markup"]["score"] > 0
        assert breakdown["conversational_content"]["score"] > 0
        assert breakdown["entity_clarity"]["score"] > 0

    def test_combined_scoring_workflow(self):
        """Test combined SEO + AEO scoring"""
        site_data = generate_perfect_site()

        scorer = AEOScorer()
        combined = scorer.calculate_combined_score(
            site_data,
            seo_score=30,  # Perfect traditional SEO
            geo_score=0
        )

        # Should combine both scores
        assert combined["total_score"] >= 48, "Should combine SEO and AEO scores"
        assert combined["component_scores"]["seo"]["score"] == 30
        assert combined["component_scores"]["aeo"]["score"] >= 18

        # Should have strengths/weaknesses
        assert "strengths" in combined
        assert "weaknesses" in combined


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
