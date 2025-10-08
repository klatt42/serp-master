"""
Automated Content Calendar Builder
Generate publishing schedules based on platform best practices
"""

from typing import List, Dict
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class PublishingFrequency(str, Enum):
    """Content publishing frequencies"""
    DAILY = "daily"
    TWICE_WEEKLY = "twice_weekly"
    WEEKLY = "weekly"
    BI_WEEKLY = "biweekly"
    MONTHLY = "monthly"


class CalendarBuilder:
    """Build automated content calendars"""

    # Best publishing times by platform (UTC)
    BEST_TIMES = {
        "youtube": [
            {"day": "mon", "time": "14:00", "reason": "Lunch hour engagement"},
            {"day": "wed", "time": "15:00", "reason": "Mid-week peak"},
            {"day": "sat", "time": "10:00", "reason": "Weekend morning"}
        ],
        "tiktok": [
            {"day": "tue", "time": "18:00", "reason": "Evening scroll"},
            {"day": "thu", "time": "19:00", "reason": "Peak engagement"},
            {"day": "sun", "time": "16:00", "reason": "Weekend activity"}
        ],
        "blog": [
            {"day": "tue", "time": "09:00", "reason": "Weekday morning"},
            {"day": "thu", "time": "10:00", "reason": "Mid-week traffic"}
        ],
        "instagram": [
            {"day": "wed", "time": "11:00", "reason": "Mid-morning"},
            {"day": "fri", "time": "13:00", "reason": "Lunch break"}
        ],
        "reddit": [
            {"day": "mon", "time": "08:00", "reason": "Weekday morning"},
            {"day": "wed", "time": "20:00", "reason": "Evening discussion"}
        ]
    }

    def generate_calendar(
        self,
        content_items: List[Dict],
        start_date: datetime,
        duration_weeks: int = 12,
        frequency: str = "weekly"
    ) -> Dict:
        """
        Generate content calendar with optimal posting times

        Returns complete calendar with scheduling recommendations
        """
        try:
            calendar = {
                "start_date": start_date.isoformat(),
                "end_date": (start_date + timedelta(weeks=duration_weeks)).isoformat(),
                "duration_weeks": duration_weeks,
                "frequency": frequency,
                "scheduled_content": [],
                "summary": {
                    "total_items": 0,
                    "by_platform": {},
                    "by_week": {}
                }
            }

            # Group content by platform
            platform_content = {}
            for item in content_items:
                platform = item.get("platform", "blog")
                if platform not in platform_content:
                    platform_content[platform] = []
                platform_content[platform].append(item)

            # Schedule content week by week
            current_date = start_date
            week_number = 1

            while week_number <= duration_weeks and any(platform_content.values()):
                week_start = current_date
                week_end = current_date + timedelta(days=6)
                week_content = []

                for platform, content_list in list(platform_content.items()):
                    if not content_list:
                        continue

                    # Determine posts per week
                    posts_per_week = self._get_posts_per_week(platform, frequency)
                    best_times = self.BEST_TIMES.get(platform, [
                        {"day": "mon", "time": "12:00", "reason": "Default"}
                    ])

                    # Schedule posts
                    for i in range(posts_per_week):
                        if not content_list:
                            break

                        content_item = content_list.pop(0)
                        time_slot = best_times[i % len(best_times)]

                        publish_date = self._calculate_publish_datetime(
                            week_start, time_slot["day"], time_slot["time"]
                        )

                        scheduled_item = {
                            **content_item,
                            "scheduled_date": publish_date.isoformat(),
                            "week_number": week_number,
                            "time_slot_reason": time_slot["reason"]
                        }

                        week_content.append(scheduled_item)
                        calendar["scheduled_content"].append(scheduled_item)

                # Update summary
                calendar["summary"]["by_week"][f"week_{week_number}"] = {
                    "date_range": f"{week_start.date()} to {week_end.date()}",
                    "content_count": len(week_content),
                    "platforms": list(set(item["platform"] for item in week_content))
                }

                current_date += timedelta(days=7)
                week_number += 1

            # Final summary
            calendar["summary"]["total_items"] = len(calendar["scheduled_content"])

            for item in calendar["scheduled_content"]:
                platform = item["platform"]
                calendar["summary"]["by_platform"][platform] = \
                    calendar["summary"]["by_platform"].get(platform, 0) + 1

            return calendar

        except Exception as e:
            logger.error(f"Calendar generation error: {str(e)}")
            raise

    def _get_posts_per_week(self, platform: str, frequency: str) -> int:
        """Determine posts per week based on platform and frequency"""

        platform_defaults = {
            "youtube": 2,
            "tiktok": 7,
            "blog": 2,
            "instagram": 5,
            "reddit": 3
        }

        base_posts = platform_defaults.get(platform, 2)

        if frequency == "daily":
            return min(base_posts * 2, 7)
        elif frequency == "twice_weekly":
            return 2
        elif frequency == "weekly":
            return 1
        elif frequency == "biweekly":
            return 1 if base_posts % 2 == 0 else 0
        elif frequency == "monthly":
            return 1 if base_posts == 1 else 0

        return base_posts

    def _calculate_publish_datetime(
        self,
        week_start: datetime,
        day: str,
        time: str
    ) -> datetime:
        """Calculate exact publish datetime"""

        day_offsets = {
            "mon": 0, "tue": 1, "wed": 2, "thu": 3,
            "fri": 4, "sat": 5, "sun": 6
        }

        day_offset = day_offsets.get(day, 0)
        publish_date = week_start + timedelta(days=day_offset)

        # Parse time
        hour, minute = map(int, time.split(':'))
        publish_datetime = publish_date.replace(hour=hour, minute=minute)

        return publish_datetime

    def export_to_google_calendar(self, calendar: Dict) -> Dict:
        """Format calendar for Google Calendar import (CSV format)"""

        export_items = []

        for item in calendar["scheduled_content"]:
            export_items.append({
                "Subject": item.get("title", f"{item['keyword']} - {item['platform']}"),
                "Start Date": item["scheduled_date"][:10],
                "Start Time": item["scheduled_date"][11:16],
                "End Date": item["scheduled_date"][:10],
                "End Time": item["scheduled_date"][11:16],
                "Description": f"Platform: {item['platform']}\nKeyword: {item['keyword']}",
                "Location": item["platform"]
            })

        return {
            "format": "google_calendar_csv",
            "items": export_items,
            "instructions": "Import this CSV into Google Calendar"
        }
