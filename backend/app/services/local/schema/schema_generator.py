"""
Local Schema Markup Generator
Generates schema.org JSON-LD markup for local businesses
"""

import logging
import json
from typing import Dict, Optional, List, Any
from datetime import datetime
import html

from app.models.local_models import (
    LocalSchemaRequest,
    LocalSchemaResponse,
    LocalSchemaType
)

logger = logging.getLogger(__name__)


class LocalSchemaGenerator:
    """Generate local business schema markup"""

    def __init__(self):
        """Initialize schema generator"""
        # Business type keywords for detection
        self.type_keywords = {
            LocalSchemaType.RESTAURANT: ["restaurant", "cafe", "bistro", "diner", "eatery", "food", "dining"],
            LocalSchemaType.STORE: ["store", "shop", "retail", "boutique", "market"],
            LocalSchemaType.PROFESSIONAL_SERVICE: ["service", "consultant", "agency", "firm", "professional"],
            LocalSchemaType.AUTO_DEALER: ["auto", "car", "vehicle", "dealer", "automotive"],
            LocalSchemaType.DENTIST: ["dentist", "dental", "orthodont"],
            LocalSchemaType.PHYSICIAN: ["doctor", "physician", "medical", "clinic", "health"],
            LocalSchemaType.ATTORNEY: ["attorney", "lawyer", "legal", "law"],
            LocalSchemaType.REAL_ESTATE_AGENT: ["real estate", "realtor", "property", "homes"]
        }

        # Required fields for valid schema
        self.required_fields = ["name", "address", "telephone"]

    async def generate_schema(
        self,
        request: LocalSchemaRequest,
        site_data: Optional[Dict] = None
    ) -> LocalSchemaResponse:
        """
        Generate local business schema markup

        Args:
            request: Schema generation request
            site_data: Optional site data from crawling

        Returns:
            Schema response with JSON-LD markup and implementation guide
        """
        try:
            logger.info(f"Generating local schema for: {request.site_url}")

            # Extract business information
            business_data = self._extract_business_data(request, site_data)

            # Detect business type
            detected_type = self._detect_business_type(
                business_data.get("category", ""),
                business_data.get("description", ""),
                request.business_type
            )

            # Generate JSON-LD schema
            json_ld = self._generate_json_ld(
                detected_type,
                business_data,
                request
            )

            # Validate schema
            validation_status, validation_messages = self._validate_schema(json_ld)

            # Generate HTML snippet
            html_snippet = self._generate_html_snippet(json_ld)

            # Determine rich features eligibility
            rich_features = self._check_rich_features(json_ld, detected_type)

            # Generate implementation guide
            implementation_guide = self._generate_implementation_guide(
                detected_type,
                validation_status,
                rich_features
            )

            return LocalSchemaResponse(
                detected_type=detected_type,
                json_ld=json_ld,
                html_snippet=html_snippet,
                validation_status=validation_status,
                validation_messages=validation_messages,
                implementation_guide=implementation_guide,
                rich_features_eligible=rich_features,
                generated_at=datetime.now()
            )

        except Exception as e:
            logger.error(f"Error generating schema: {str(e)}")
            raise

    def _extract_business_data(
        self,
        request: LocalSchemaRequest,
        site_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Extract business data from request and site data"""
        # In production, this would extract from actual site crawling
        # For now, simulate with sample data
        return {
            "name": site_data.get("business_name", "Example Business") if site_data else "Example Business",
            "address": {
                "street": "123 Main Street",
                "city": "Anytown",
                "state": "CA",
                "postal_code": "90210",
                "country": "US"
            },
            "phone": "(555) 123-4567",
            "email": "contact@example.com",
            "url": request.site_url,
            "category": "Professional Services",
            "description": "A professional business providing excellent services to the local community.",
            "hours": {
                "monday": "09:00-17:00",
                "tuesday": "09:00-17:00",
                "wednesday": "09:00-17:00",
                "thursday": "09:00-17:00",
                "friday": "09:00-17:00",
                "saturday": "closed",
                "sunday": "closed"
            },
            "geo": {
                "latitude": 34.0522,
                "longitude": -118.2437
            },
            "price_range": "$$",
            "accepts_reservations": True,
            "service_area": ["Los Angeles County", "Orange County"]
        }

    def _detect_business_type(
        self,
        category: str,
        description: str,
        override_type: Optional[str] = None
    ) -> LocalSchemaType:
        """Detect business type from category and description"""
        # If type is explicitly provided, use it
        if override_type:
            try:
                return LocalSchemaType(override_type)
            except ValueError:
                pass

        # Check keywords in category and description
        text = f"{category} {description}".lower()

        for schema_type, keywords in self.type_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return schema_type

        # Default to LocalBusiness if no match
        return LocalSchemaType.LOCAL_BUSINESS

    def _generate_json_ld(
        self,
        business_type: LocalSchemaType,
        business_data: Dict[str, Any],
        request: LocalSchemaRequest
    ) -> Dict[str, Any]:
        """Generate JSON-LD schema markup"""
        # Base schema structure
        schema = {
            "@context": "https://schema.org",
            "@type": business_type.value,
            "name": business_data["name"],
            "url": business_data["url"],
            "telephone": business_data["phone"],
            "email": business_data.get("email"),
            "description": business_data.get("description"),
            "priceRange": business_data.get("price_range"),
        }

        # Address
        if business_data.get("address"):
            addr = business_data["address"]
            schema["address"] = {
                "@type": "PostalAddress",
                "streetAddress": addr.get("street"),
                "addressLocality": addr.get("city"),
                "addressRegion": addr.get("state"),
                "postalCode": addr.get("postal_code"),
                "addressCountry": addr.get("country", "US")
            }

        # Geo coordinates
        if business_data.get("geo") and request.include_service_area:
            geo = business_data["geo"]
            schema["geo"] = {
                "@type": "GeoCoordinates",
                "latitude": geo.get("latitude"),
                "longitude": geo.get("longitude")
            }

        # Business hours
        if business_data.get("hours") and request.include_hours:
            hours_specs = []
            days_map = {
                "monday": "Monday",
                "tuesday": "Tuesday",
                "wednesday": "Wednesday",
                "thursday": "Thursday",
                "friday": "Friday",
                "saturday": "Saturday",
                "sunday": "Sunday"
            }

            for day, hours in business_data["hours"].items():
                if hours and hours.lower() != "closed":
                    hours_specs.append({
                        "@type": "OpeningHoursSpecification",
                        "dayOfWeek": days_map.get(day, day.capitalize()),
                        "opens": hours.split("-")[0],
                        "closes": hours.split("-")[1] if "-" in hours else hours
                    })

            if hours_specs:
                schema["openingHoursSpecification"] = hours_specs

        # Service area
        if request.include_service_area and business_data.get("service_area"):
            schema["areaServed"] = [
                {"@type": "City", "name": area}
                for area in business_data["service_area"]
            ]

        # Type-specific enhancements
        if business_type == LocalSchemaType.RESTAURANT:
            schema["servesCuisine"] = business_data.get("cuisine", "American")
            if business_data.get("accepts_reservations"):
                schema["acceptsReservations"] = "True"

        elif business_type in [LocalSchemaType.DENTIST, LocalSchemaType.PHYSICIAN]:
            schema["medicalSpecialty"] = business_data.get("specialty", "General Practice")

        elif business_type == LocalSchemaType.ATTORNEY:
            schema["areaOfLaw"] = business_data.get("area_of_law", "General Practice")

        # Aggregate rating (if available)
        if business_data.get("rating"):
            schema["aggregateRating"] = {
                "@type": "AggregateRating",
                "ratingValue": business_data["rating"].get("value", 4.5),
                "reviewCount": business_data["rating"].get("count", 10),
                "bestRating": "5",
                "worstRating": "1"
            }

        # Remove None values
        schema = {k: v for k, v in schema.items() if v is not None}

        return schema

    def _validate_schema(self, schema: Dict[str, Any]) -> tuple[str, List[str]]:
        """Validate schema markup"""
        messages = []
        status = "valid"

        # Check required fields
        if not schema.get("name"):
            messages.append("Missing required field: name")
            status = "error"

        if not schema.get("address"):
            messages.append("Missing required field: address")
            status = "error"

        if not schema.get("telephone"):
            messages.append("Missing required field: telephone")
            status = "error"

        # Check recommended fields
        if not schema.get("url"):
            messages.append("Recommended: Add website URL")
            if status == "valid":
                status = "warning"

        if not schema.get("openingHoursSpecification"):
            messages.append("Recommended: Add business hours")
            if status == "valid":
                status = "warning"

        if not schema.get("geo"):
            messages.append("Recommended: Add geographic coordinates for map features")
            if status == "valid":
                status = "warning"

        if not schema.get("description"):
            messages.append("Recommended: Add business description")
            if status == "valid":
                status = "warning"

        if not schema.get("aggregateRating"):
            messages.append("Recommended: Add aggregate rating for star snippets")
            if status == "valid":
                status = "warning"

        # Success message
        if status == "valid":
            messages.append("✓ All required fields present")
            messages.append("✓ Schema is valid and ready for implementation")

        return status, messages

    def _generate_html_snippet(self, schema: Dict[str, Any]) -> str:
        """Generate HTML implementation snippet"""
        json_str = json.dumps(schema, indent=2, ensure_ascii=False)
        escaped_json = html.escape(json_str)

        snippet = f'''<!-- Local Business Schema Markup -->
<script type="application/ld+json">
{json_str}
</script>

<!--
IMPLEMENTATION INSTRUCTIONS:
1. Copy the entire <script> tag above
2. Paste it in the <head> section of your website
3. Place it on your homepage and/or location pages
4. Test using Google's Rich Results Test: https://search.google.com/test/rich-results
-->'''

        return snippet

    def _check_rich_features(
        self,
        schema: Dict[str, Any],
        business_type: LocalSchemaType
    ) -> List[str]:
        """Check which rich features the schema is eligible for"""
        features = []

        # Knowledge Panel eligibility
        if schema.get("name") and schema.get("address") and schema.get("telephone"):
            features.append("knowledge_panel")

        # Rich snippets (enhanced search results)
        if schema.get("aggregateRating"):
            features.append("star_ratings")

        if schema.get("priceRange"):
            features.append("price_range")

        if schema.get("openingHoursSpecification"):
            features.append("business_hours")

        # Map features
        if schema.get("geo"):
            features.append("map_pin")
            features.append("directions")

        # Type-specific features
        if business_type == LocalSchemaType.RESTAURANT:
            if schema.get("servesCuisine"):
                features.append("cuisine_type")
            if schema.get("acceptsReservations"):
                features.append("reservation_action")

        if business_type in [LocalSchemaType.DENTIST, LocalSchemaType.PHYSICIAN]:
            features.append("appointment_action")

        # Service area
        if schema.get("areaServed"):
            features.append("service_area")

        return features

    def _generate_implementation_guide(
        self,
        business_type: LocalSchemaType,
        validation_status: str,
        rich_features: List[str]
    ) -> str:
        """Generate implementation guide"""
        guide = f"""# Local Business Schema Implementation Guide

## Schema Type: {business_type.value}
## Validation Status: {validation_status.upper()}

### Step 1: Copy and Paste
1. Copy the HTML snippet provided above
2. Paste it in the <head> section of your homepage
3. Also add to location-specific pages if you have multiple locations

### Step 2: Customize (if needed)
- Update business name, address, phone to match your actual business
- Add/update business hours for accuracy
- Include aggregate rating if you have reviews
- Add geographic coordinates for better map features

### Step 3: Test Your Implementation
1. Visit: https://search.google.com/test/rich-results
2. Enter your page URL or paste the schema code
3. Fix any errors or warnings
4. Retest until validation is clean

### Step 4: Monitor in Google Search Console
1. Go to Search Console > Enhancements
2. Check "Unparsable structured data" for errors
3. Monitor "Valid items" to confirm Google is reading your schema

### Rich Results You're Eligible For:
"""

        if rich_features:
            for feature in rich_features:
                feature_name = feature.replace("_", " ").title()
                guide += f"- ✓ {feature_name}\n"
        else:
            guide += "- Add more schema fields to unlock rich results\n"

        guide += f"""
### Best Practices:
- Keep schema data synchronized with visible website content
- Update hours for holidays and special events
- Add schema to all location pages if multi-location business
- Monitor Google Search Console for schema errors
- Update aggregate ratings as you receive new reviews

### Next Steps:
"""

        if validation_status == "error":
            guide += "- ⚠️ Fix required field errors before implementation\n"
        elif validation_status == "warning":
            guide += "- Add recommended fields to improve rich results eligibility\n"
        else:
            guide += "- ✓ Schema is ready! Implement and test.\n"

        guide += f"""- Consider adding Organization schema for brand information
- Add FAQ schema if you have frequently asked questions
- Include Review schema for individual customer reviews
- Use breadcrumb schema for site navigation

For more information: https://schema.org/{business_type.value}
"""

        return guide
