"""Supabase client for SERP-Master database operations."""

from supabase import create_client, Client
from typing import Optional, Dict, List, Any
import os
from dotenv import load_dotenv

load_dotenv()

class SupabaseService:
    """Service for interacting with Supabase database."""

    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_ANON_KEY")
        self.client: Optional[Client] = None

        if self.url and self.key:
            self.client = create_client(self.url, self.key)

    def is_configured(self) -> bool:
        """Check if Supabase is properly configured."""
        return self.client is not None

    # ==================
    # USER OPERATIONS
    # ==================

    async def create_user_project(self, user_id: str, project_data: Dict[str, Any]) -> Dict:
        """Create a new SEO project for a user."""
        if not self.client:
            return {"error": "Supabase not configured"}

        try:
            data = {
                "user_id": user_id,
                "name": project_data.get("name"),
                "domain": project_data.get("domain"),
                "target_keywords": project_data.get("target_keywords", []),
                "created_at": "now()"
            }

            response = self.client.table("projects").insert(data).execute()
            return {"success": True, "data": response.data}
        except Exception as e:
            return {"error": str(e)}

    async def get_user_projects(self, user_id: str) -> List[Dict]:
        """Get all projects for a user."""
        if not self.client:
            return []

        try:
            response = self.client.table("projects").select("*").eq("user_id", user_id).execute()
            return response.data
        except Exception as e:
            print(f"Error fetching projects: {e}")
            return []

    # ==================
    # KEYWORD OPERATIONS
    # ==================

    async def save_keyword_research(
        self,
        project_id: str,
        keywords: List[Dict[str, Any]]
    ) -> Dict:
        """Save keyword research results."""
        if not self.client:
            return {"error": "Supabase not configured"}

        try:
            data = []
            for kw in keywords:
                data.append({
                    "project_id": project_id,
                    "keyword": kw.get("keyword"),
                    "search_volume": kw.get("volume", 0),
                    "competition": kw.get("competition", 0),
                    "cpc": kw.get("cpc", 0),
                    "difficulty": kw.get("difficulty", 0),
                    "researched_at": "now()"
                })

            response = self.client.table("keywords").insert(data).execute()
            return {"success": True, "data": response.data}
        except Exception as e:
            return {"error": str(e)}

    async def get_project_keywords(self, project_id: str) -> List[Dict]:
        """Get all keywords for a project."""
        if not self.client:
            return []

        try:
            response = self.client.table("keywords").select("*").eq("project_id", project_id).execute()
            return response.data
        except Exception as e:
            print(f"Error fetching keywords: {e}")
            return []

    # ==================
    # RANKING OPERATIONS
    # ==================

    async def save_ranking_data(
        self,
        project_id: str,
        keyword: str,
        position: int,
        url: str
    ) -> Dict:
        """Save keyword ranking data."""
        if not self.client:
            return {"error": "Supabase not configured"}

        try:
            data = {
                "project_id": project_id,
                "keyword": keyword,
                "position": position,
                "url": url,
                "checked_at": "now()"
            }

            response = self.client.table("rankings").insert(data).execute()
            return {"success": True, "data": response.data}
        except Exception as e:
            return {"error": str(e)}

    async def get_ranking_history(
        self,
        project_id: str,
        keyword: str,
        days: int = 30
    ) -> List[Dict]:
        """Get ranking history for a keyword."""
        if not self.client:
            return []

        try:
            response = (
                self.client.table("rankings")
                .select("*")
                .eq("project_id", project_id)
                .eq("keyword", keyword)
                .order("checked_at", desc=True)
                .limit(days)
                .execute()
            )
            return response.data
        except Exception as e:
            print(f"Error fetching ranking history: {e}")
            return []

    # ==================
    # AUDIT OPERATIONS
    # ==================

    async def save_audit_results(
        self,
        project_id: str,
        audit_data: Dict[str, Any]
    ) -> Dict:
        """Save technical SEO audit results."""
        if not self.client:
            return {"error": "Supabase not configured"}

        try:
            data = {
                "project_id": project_id,
                "page_speed_score": audit_data.get("page_speed_score"),
                "mobile_friendly": audit_data.get("mobile_friendly"),
                "core_web_vitals": audit_data.get("core_web_vitals"),
                "issues_found": audit_data.get("issues_found", []),
                "audited_at": "now()"
            }

            response = self.client.table("audits").insert(data).execute()
            return {"success": True, "data": response.data}
        except Exception as e:
            return {"error": str(e)}

    async def get_latest_audit(self, project_id: str) -> Optional[Dict]:
        """Get the most recent audit for a project."""
        if not self.client:
            return None

        try:
            response = (
                self.client.table("audits")
                .select("*")
                .eq("project_id", project_id)
                .order("audited_at", desc=True)
                .limit(1)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error fetching audit: {e}")
            return None


# Global instance
supabase_service = SupabaseService()
