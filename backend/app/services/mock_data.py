"""
Mock Data Generator
Generates realistic mock crawl data for testing AEO scoring without DataForSEO
"""

import json
from typing import Dict, Any, List, Optional


def generate_mock_html(
    has_org_schema: bool = True,
    has_local_business_schema: bool = False,
    has_faq_schema: bool = False,
    has_product_schema: bool = False,
    business_name: str = "Prism Specialties",
    question_headers: int = 0,
    has_about_page: bool = True,
    readability_level: str = "easy"  # easy, moderate, difficult
) -> str:
    """
    Generate mock HTML with various schema types and content patterns

    Args:
        has_org_schema: Include Organization schema
        has_local_business_schema: Include LocalBusiness schema
        has_faq_schema: Include FAQPage schema
        has_product_schema: Include Product schema
        business_name: Business name to use
        question_headers: Number of question-format headers to include
        has_about_page: Include about page indicators
        readability_level: Text complexity (easy, moderate, difficult)

    Returns:
        Mock HTML string
    """
    schemas = []

    # Organization schema
    if has_org_schema:
        org_schema = {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": business_name,
            "url": f"https://{business_name.lower().replace(' ', '')}.com",
            "logo": f"https://{business_name.lower().replace(' ', '')}.com/logo.png",
            "description": f"{business_name} - Expert services in the DMV area",
            "sameAs": [
                "https://facebook.com/prismspecialties",
                "https://twitter.com/prismspecialties"
            ]
        }
        schemas.append(org_schema)

    # LocalBusiness schema
    if has_local_business_schema:
        local_schema = {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "name": business_name,
            "address": {
                "@type": "PostalAddress",
                "streetAddress": "123 Main St",
                "addressLocality": "Arlington",
                "addressRegion": "VA",
                "postalCode": "22201",
                "addressCountry": "US"
            },
            "telephone": "+1-555-123-4567",
            "openingHours": "Mo-Fr 08:00-18:00",
            "geo": {
                "@type": "GeoCoordinates",
                "latitude": "38.8816",
                "longitude": "-77.0910"
            }
        }
        schemas.append(local_schema)

    # FAQPage schema
    if has_faq_schema:
        faq_schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": "How do we fix water damage?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": "We use professional equipment to extract water, dry affected areas, and restore your property."
                    }
                },
                {
                    "@type": "Question",
                    "name": "What causes mold growth?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": "Mold grows in damp, humid conditions often resulting from water damage or poor ventilation."
                    }
                }
            ]
        }
        schemas.append(faq_schema)

    # Product schema
    if has_product_schema:
        product_schema = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": "Water Damage Restoration Service",
            "description": "Professional water damage restoration for homes and businesses",
            "brand": {
                "@type": "Brand",
                "name": business_name
            },
            "offers": {
                "@type": "Offer",
                "price": "299.00",
                "priceCurrency": "USD"
            }
        }
        schemas.append(product_schema)

    # Generate schema markup HTML
    schema_html = ""
    for schema in schemas:
        schema_html += f'<script type="application/ld+json">\n{json.dumps(schema, indent=2)}\n</script>\n'

    # Generate question headers
    question_header_html = ""
    question_templates = [
        "How do we fix water damage?",
        "What causes mold growth?",
        "When should you call for emergency services?",
        "Why is water damage dangerous?",
        "Where does mold typically grow?",
        "How long does restoration take?",
        "What equipment do we use?",
        "Can water damage affect health?",
        "Does insurance cover water damage?",
        "Is mold removal safe?",
        "Should I leave during restoration?",
        "How much does restoration cost?"
    ]

    for i in range(min(question_headers, len(question_templates))):
        question_header_html += f'<h2>{question_templates[i]}</h2>\n<p>Answer to the question goes here.</p>\n'

    # Generate content based on readability level
    if readability_level == "easy":
        content = """
        <p>We fix water damage fast. Our team helps homes and businesses.
        We use top tools. We dry your space well. Call us today for help.</p>
        """
    elif readability_level == "moderate":
        content = """
        <p>Our company provides professional water damage restoration services.
        We serve residential and commercial properties throughout the region.
        Our certified technicians use advanced equipment to ensure complete restoration.</p>
        """
    else:  # difficult
        content = """
        <p>Utilizing state-of-the-art dehumidification and moisture detection apparatus,
        our organization facilitates comprehensive remediation of aqueous deterioration incidents.
        We implement sophisticated protocols to ensure optimal structural rehabilitation outcomes.</p>
        """

    # Generate about page content if requested
    about_content = ""
    if has_about_page:
        about_content = f"""
        <h1>About {business_name}</h1>
        <p>{business_name} has been serving the DMV area for over 15 years.
        We specialize in water damage restoration, mold remediation, and emergency services.
        Our team of certified professionals is available 24/7 to help you recover from disasters.</p>
        <p>Founded in 2008, {business_name} has grown from a small local operation to a trusted
        regional provider. We pride ourselves on quick response times, quality workmanship, and
        excellent customer service. Our mission is to restore your property and your peace of mind.</p>
        <p>We are IICRC certified, fully licensed and insured, and maintain an A+ rating with the BBB.
        Our team includes water damage specialists, mold remediation experts, and project managers
        dedicated to delivering the best possible results for every customer.</p>
        """

    # Construct full HTML
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{business_name} - Water Damage Restoration</title>
        <meta name="description" content="{business_name} provides expert water damage restoration, mold remediation, and emergency services in the DC, Maryland, and Virginia area. IICRC certified and available 24/7.">
        {schema_html}
    </head>
    <body>
        <header>
            <h1>{business_name}</h1>
            <nav>
                <a href="/">Home</a>
                <a href="/services">Services</a>
                <a href="/about">About</a>
                <a href="/faq">FAQ</a>
                <a href="/contact">Contact</a>
            </nav>
        </header>

        <main>
            {content}
            {question_header_html}
            {about_content}
        </main>

        <footer>
            <p>&copy; 2025 {business_name}. All rights reserved.</p>
            <p>Serving DC, Maryland, and Virginia</p>
        </footer>
    </body>
    </html>
    """

    return html


def generate_mock_site(
    has_org_schema: bool = True,
    has_local_business_schema: bool = False,
    has_faq_page: bool = True,
    has_product_schema: bool = False,
    business_name: str = "Prism Specialties",
    question_headers: int = 10,
    has_about_page: bool = True,
    readability_level: str = "easy"
) -> Dict[str, Any]:
    """
    Generate complete mock site data matching DataForSEO structure

    Returns:
        Dictionary mimicking DataForSEO crawl results
    """
    html = generate_mock_html(
        has_org_schema=has_org_schema,
        has_local_business_schema=has_local_business_schema,
        has_faq_schema=has_faq_page,
        has_product_schema=has_product_schema,
        business_name=business_name,
        question_headers=question_headers,
        has_about_page=has_about_page,
        readability_level=readability_level
    )

    return {
        "url": f"https://{business_name.lower().replace(' ', '')}.com",
        "html": html,
        "business_name": business_name,
        "pages": [
            {
                "url": "/",
                "title": f"{business_name} - Water Damage Restoration",
                "html": html,
                "meta": {
                    "title": f"{business_name} - Water Damage Restoration",
                    "description": f"{business_name} provides expert water damage restoration services"
                }
            },
            {
                "url": "/about",
                "title": f"About {business_name}",
                "html": html,
                "meta": {
                    "title": f"About {business_name}",
                    "description": f"Learn about {business_name} and our team"
                }
            },
            {
                "url": "/faq",
                "title": "Frequently Asked Questions",
                "html": html,
                "meta": {
                    "title": "FAQ - Common Questions",
                    "description": "Answers to common questions about water damage restoration"
                }
            } if has_faq_page else None
        ],
        "metadata": {
            "pages_crawled": 3 if has_faq_page else 2,
            "business_info": {
                "name": business_name,
                "has_about_page": has_about_page
            }
        }
    }


def generate_perfect_site() -> Dict[str, Any]:
    """Generate a site with perfect AEO score (25/25)"""
    return generate_mock_site(
        has_org_schema=True,
        has_local_business_schema=True,
        has_faq_page=True,
        has_product_schema=True,
        business_name="Prism Specialties",
        question_headers=12,
        has_about_page=True,
        readability_level="easy"
    )


def generate_poor_site() -> Dict[str, Any]:
    """Generate a site with poor AEO score for testing"""
    return generate_mock_site(
        has_org_schema=False,
        has_local_business_schema=False,
        has_faq_page=False,
        has_product_schema=False,
        business_name="Test Company",
        question_headers=0,
        has_about_page=False,
        readability_level="difficult"
    )
