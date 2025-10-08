"""
Supabase Client for Week 4: Competitor Comparisons
Provides database storage for comparison results
"""

import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from supabase import create_client, Client

logger = logging.getLogger(__name__)


class SupabaseComparisonStore:
    """
    Manages Supabase storage for competitor comparisons
    Falls back to in-memory if Supabase not configured
    """

    def __init__(self):
        """Initialize Supabase client"""
        self.enabled = False
        self.client: Optional[Client] = None

        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")

        if supabase_url and supabase_key:
            try:
                self.client = create_client(supabase_url, supabase_key)
                self.enabled = True
                logger.info("Supabase client initialized for comparisons")
            except Exception as e:
                logger.warning(f"Failed to initialize Supabase: {e}. Using in-memory storage.")
                self.enabled = False
        else:
            logger.info("Supabase not configured. Using in-memory storage.")

    async def save_comparison(
        self,
        comparison_id: str,
        user_url: str,
        competitor_urls: List[str],
        max_pages: int,
        status: str = "crawling",
        progress: int = 0,
        results: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Save or update a comparison in Supabase

        Args:
            comparison_id: Unique comparison ID
            user_url: User's website URL
            competitor_urls: List of competitor URLs
            max_pages: Max pages crawled per site
            status: Current status (crawling, analyzing, complete, failed)
            progress: Progress percentage (0-100)
            results: Complete results dict (when status=complete)

        Returns:
            True if saved successfully, False otherwise
        """
        if not self.enabled:
            return False

        try:
            data = {
                "comparison_id": comparison_id,
                "user_url": user_url,
                "competitor_urls": competitor_urls,
                "max_pages": max_pages,
                "status": status,
                "progress": progress,
                "sites_total": 1 + len(competitor_urls),
                "sites_completed": 0 if status != "complete" else 1 + len(competitor_urls),
            }

            # Add results if provided
            if results:
                data.update({
                    "user_site": results.get("user_site"),
                    "competitors": results.get("competitors"),
                    "comparison_data": results.get("comparison"),
                    "gaps": results.get("gaps"),
                    "competitive_strategy": results.get("competitive_strategy"),
                    "quick_wins": results.get("quick_wins"),
                    "completed_at": datetime.utcnow().isoformat() if status == "complete" else None
                })

            # Upsert (insert or update)
            response = self.client.table("competitor_comparisons").upsert(
                data,
                on_conflict="comparison_id"
            ).execute()

            logger.info(f"Saved comparison {comparison_id} to Supabase")
            return True

        except Exception as e:
            logger.error(f"Failed to save comparison to Supabase: {e}")
            return False

    async def get_comparison(self, comparison_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a comparison from Supabase

        Args:
            comparison_id: Comparison ID to retrieve

        Returns:
            Comparison data dict or None if not found
        """
        if not self.enabled:
            return None

        try:
            response = self.client.table("competitor_comparisons").select("*").eq(
                "comparison_id", comparison_id
            ).execute()

            if response.data and len(response.data) > 0:
                return response.data[0]

            return None

        except Exception as e:
            logger.error(f"Failed to get comparison from Supabase: {e}")
            return None

    async def get_recent_comparisons(
        self,
        user_url: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get recent comparisons, optionally filtered by user URL

        Args:
            user_url: Filter by user URL (optional)
            limit: Max number of results

        Returns:
            List of comparison summaries
        """
        if not self.enabled:
            return []

        try:
            query = self.client.table("competitor_comparisons").select(
                "comparison_id, user_url, competitor_urls, status, progress, created_at"
            ).order("created_at", desc=True).limit(limit)

            if user_url:
                query = query.eq("user_url", user_url)

            response = query.execute()
            return response.data if response.data else []

        except Exception as e:
            logger.error(f"Failed to get recent comparisons: {e}")
            return []
