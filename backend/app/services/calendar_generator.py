"""
Content calendar generation and export
Supports Google Calendar, ICS, and CSV formats
"""

from typing import List, Dict
from datetime import datetime
from icalendar import Calendar, Event
import csv
from io import StringIO
from urllib.parse import quote

from app.models.content_strategy import ContentItem


class CalendarGenerator:
    """Generate editorial calendars in various formats"""

    @staticmethod
    def generate_ics(
        content_items: List[ContentItem],
        calendar_name: str = "Content Strategy Calendar"
    ) -> str:
        """
        Generate ICS (iCalendar) format for import to calendar apps

        Returns:
            ICS file content as string
        """
        cal = Calendar()
        cal.add('prodid', '-//SERP-Master Content Calendar//EN')
        cal.add('version', '2.0')
        cal.add('x-wr-calname', calendar_name)

        for item in content_items:
            event = Event()
            event.add('summary', f"📝 {item.title}")
            event.add('dtstart', item.scheduled_date.date())
            event.add('dtend', item.scheduled_date.date())

            # Add description with details
            description = f"""
Content Type: {item.content_type}
Target Keyword: {item.target_keyword}
Priority: {item.priority}
Estimated Time: {item.estimated_hours}h
Pillar: {item.pillar_name}

Optimization Tips:
{chr(10).join(f"• {tip}" for tip in item.optimization_tips)}
            """.strip()

            event.add('description', description)
            event.add('location', f"Content Pillar: {item.pillar_name}")
            event.add('status', 'TENTATIVE')
            event.add('priority', 5 if item.priority == 'high' else 3)

            cal.add_component(event)

        return cal.to_ical().decode('utf-8')

    @staticmethod
    def generate_csv(content_items: List[ContentItem]) -> str:
        """
        Generate CSV format for spreadsheet import

        Returns:
            CSV content as string
        """
        output = StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            'Date',
            'Title',
            'Content Type',
            'Target Keyword',
            'Supporting Keywords',
            'Priority',
            'Difficulty',
            'Est. Hours',
            'Pillar',
            'Status',
            'Optimization Tips'
        ])

        # Data rows
        for item in content_items:
            writer.writerow([
                item.scheduled_date.strftime('%Y-%m-%d'),
                item.title,
                item.content_type,
                item.target_keyword,
                ', '.join(item.supporting_keywords),
                item.priority,
                item.estimated_difficulty,
                item.estimated_hours,
                item.pillar_name,
                item.status,
                ' | '.join(item.optimization_tips)
            ])

        return output.getvalue()

    @staticmethod
    def generate_google_calendar_link(item: ContentItem) -> str:
        """Generate quick-add link for Google Calendar"""

        title = quote(f"📝 {item.title}")
        dates = item.scheduled_date.strftime('%Y%m%d')
        details = quote(f"Target: {item.target_keyword} | Type: {item.content_type} | Priority: {item.priority}")

        return f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={title}&dates={dates}/{dates}&details={details}"

    @staticmethod
    def group_by_week(content_items: List[ContentItem]) -> Dict[int, List[ContentItem]]:
        """Group content items by week number"""
        weeks = {}
        base_date = min(item.scheduled_date for item in content_items) if content_items else datetime.now()

        for item in content_items:
            week_number = ((item.scheduled_date - base_date).days // 7) + 1
            if week_number not in weeks:
                weeks[week_number] = []
            weeks[week_number].append(item)

        return weeks
