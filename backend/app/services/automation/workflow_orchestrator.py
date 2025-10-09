"""
Workflow Orchestration System
Manages content creation workflow from idea to publish
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class WorkflowStage(str, Enum):
    """Content workflow stages"""
    IDEA = "idea"
    RESEARCH = "research"
    OUTLINE = "outline"
    DRAFT = "draft"
    REVIEW = "review"
    REVISE = "revise"
    PUBLISH = "publish"
    TRACK = "track"


class TaskPriority(str, Enum):
    """Task priority levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class WorkflowOrchestrator:
    """Orchestrate content workflow and task management"""

    def __init__(self):
        """Initialize workflow orchestrator"""
        self.stage_order = [stage.value for stage in WorkflowStage]

    async def create_task(
        self,
        title: str,
        description: str,
        project_id: Optional[str] = None,
        assigned_to: Optional[str] = None,
        priority: str = TaskPriority.MEDIUM.value,
        due_date: Optional[str] = None
    ) -> Dict:
        """
        Create new workflow task

        Args:
            title: Task title
            description: Task description
            project_id: Associated project
            assigned_to: User ID assignment
            priority: Task priority
            due_date: Due date (ISO format)

        Returns:
            Created task
        """
        try:
            task = {
                "id": f"task_{datetime.now().timestamp()}",
                "title": title,
                "description": description,
                "project_id": project_id,
                "stage": WorkflowStage.IDEA.value,
                "priority": priority,
                "assigned_to": assigned_to,
                "due_date": due_date,
                "dependencies": [],
                "metadata": {},
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }

            logger.info(f"Created task: {title}")
            return task

        except Exception as e:
            logger.error(f"Error creating task: {str(e)}")
            raise

    async def update_task_stage(
        self,
        task_id: str,
        new_stage: str,
        current_stage: str
    ) -> Dict:
        """
        Move task to new workflow stage

        Args:
            task_id: Task identifier
            new_stage: Target stage
            current_stage: Current stage for validation

        Returns:
            Updated task data
        """
        try:
            # Validate stage transition
            if not self._is_valid_transition(current_stage, new_stage):
                raise ValueError(f"Invalid stage transition: {current_stage} -> {new_stage}")

            update = {
                "id": task_id,
                "stage": new_stage,
                "previous_stage": current_stage,
                "stage_changed_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }

            logger.info(f"Moved task {task_id} from {current_stage} to {new_stage}")
            return update

        except Exception as e:
            logger.error(f"Error updating task stage: {str(e)}")
            raise

    def _is_valid_transition(self, from_stage: str, to_stage: str) -> bool:
        """Validate stage transition is allowed"""
        try:
            if from_stage not in self.stage_order or to_stage not in self.stage_order:
                return False

            # Allow moving to any stage (flexible workflow)
            # In stricter workflows, you might only allow sequential or adjacent moves
            return True

        except Exception as e:
            logger.error(f"Error validating transition: {str(e)}")
            return False

    async def assign_task(
        self,
        task_id: str,
        user_id: str
    ) -> Dict:
        """Assign task to user"""
        try:
            assignment = {
                "task_id": task_id,
                "assigned_to": user_id,
                "assigned_at": datetime.now().isoformat()
            }

            logger.info(f"Assigned task {task_id} to user {user_id}")
            return assignment

        except Exception as e:
            logger.error(f"Error assigning task: {str(e)}")
            raise

    async def set_dependencies(
        self,
        task_id: str,
        dependency_ids: List[str]
    ) -> Dict:
        """Set task dependencies"""
        try:
            dependencies = {
                "task_id": task_id,
                "dependencies": dependency_ids,
                "updated_at": datetime.now().isoformat()
            }

            logger.info(f"Set {len(dependency_ids)} dependencies for task {task_id}")
            return dependencies

        except Exception as e:
            logger.error(f"Error setting dependencies: {str(e)}")
            raise

    async def get_workflow_board(
        self,
        project_id: Optional[str] = None,
        assigned_to: Optional[str] = None
    ) -> Dict:
        """
        Get complete workflow board view

        Args:
            project_id: Filter by project
            assigned_to: Filter by assignee

        Returns:
            Workflow board with tasks by stage
        """
        try:
            # In production, this would query database
            # Placeholder structure
            board = {
                "stages": {},
                "filters": {
                    "project_id": project_id,
                    "assigned_to": assigned_to
                }
            }

            for stage in WorkflowStage:
                board["stages"][stage.value] = {
                    "name": stage.value.title(),
                    "tasks": [],
                    "count": 0
                }

            return board

        except Exception as e:
            logger.error(f"Error getting workflow board: {str(e)}")
            raise

    async def get_task_metrics(
        self,
        project_id: Optional[str] = None,
        date_range_days: int = 30
    ) -> Dict:
        """
        Get workflow metrics

        Args:
            project_id: Filter by project
            date_range_days: Date range for metrics

        Returns:
            Workflow performance metrics
        """
        try:
            metrics = {
                "total_tasks": 0,
                "completed_tasks": 0,
                "in_progress_tasks": 0,
                "overdue_tasks": 0,
                "avg_completion_time_days": 0,
                "tasks_by_stage": {},
                "tasks_by_priority": {
                    "high": 0,
                    "medium": 0,
                    "low": 0
                },
                "calculated_at": datetime.now().isoformat()
            }

            return metrics

        except Exception as e:
            logger.error(f"Error getting task metrics: {str(e)}")
            raise

    async def auto_progress_task(
        self,
        task_id: str,
        current_stage: str,
        completion_criteria: Dict
    ) -> Dict:
        """
        Automatically progress task if criteria met

        Args:
            task_id: Task identifier
            current_stage: Current workflow stage
            completion_criteria: Criteria for auto-progression

        Returns:
            Updated task or None if criteria not met
        """
        try:
            # Check if current stage can auto-progress
            auto_progress_rules = {
                WorkflowStage.RESEARCH.value: {
                    "next_stage": WorkflowStage.OUTLINE.value,
                    "criteria": "research_complete"
                },
                WorkflowStage.DRAFT.value: {
                    "next_stage": WorkflowStage.REVIEW.value,
                    "criteria": "draft_complete"
                }
            }

            rule = auto_progress_rules.get(current_stage)
            if not rule:
                return {"auto_progressed": False, "reason": "No auto-progress rule"}

            # Check criteria (simplified)
            criteria_met = completion_criteria.get(rule["criteria"], False)

            if criteria_met:
                return await self.update_task_stage(
                    task_id,
                    rule["next_stage"],
                    current_stage
                )
            else:
                return {"auto_progressed": False, "reason": "Criteria not met"}

        except Exception as e:
            logger.error(f"Error auto-progressing task: {str(e)}")
            raise

    async def generate_task_from_suggestion(
        self,
        topic_suggestion: Dict,
        project_id: Optional[str] = None
    ) -> Dict:
        """
        Create workflow task from topic suggestion

        Args:
            topic_suggestion: Topic suggestion from intelligence engine
            project_id: Target project

        Returns:
            Created task
        """
        try:
            topic = topic_suggestion.get("topic", "Untitled")
            angle = topic_suggestion.get("angle", "")
            effort = topic_suggestion.get("estimated_effort_hours", 3)

            # Calculate due date based on effort
            due_date = (datetime.now() + timedelta(days=int(effort * 2))).isoformat()

            task = await self.create_task(
                title=angle or f"Create content: {topic}",
                description=f"Topic: {topic}\n\nReasoning: {topic_suggestion.get('reasoning', '')}\n\nTraffic Potential: {topic_suggestion.get('traffic_potential', 0)} monthly visitors",
                project_id=project_id,
                priority=topic_suggestion.get("priority", TaskPriority.MEDIUM.value),
                due_date=due_date
            )

            # Add suggestion metadata
            task["metadata"] = {
                "source": "topic_suggestion",
                "suggestion_id": topic_suggestion.get("id"),
                "confidence_score": topic_suggestion.get("confidence_score"),
                "traffic_potential": topic_suggestion.get("traffic_potential")
            }

            logger.info(f"Generated task from topic suggestion: {topic}")
            return task

        except Exception as e:
            logger.error(f"Error generating task from suggestion: {str(e)}")
            raise

    async def generate_task_from_refresh(
        self,
        refresh_item: Dict,
        project_id: Optional[str] = None
    ) -> Dict:
        """
        Create workflow task from refresh recommendation

        Args:
            refresh_item: Refresh queue item
            project_id: Target project

        Returns:
            Created task
        """
        try:
            content_title = refresh_item.get("content_title", "Untitled Content")
            recommendations = refresh_item.get("recommendations", [])
            effort = refresh_item.get("estimated_effort", 2)

            # Build description from recommendations
            rec_text = "\n".join([
                f"- {rec.get('action', '')}"
                for rec in recommendations
            ])

            task = await self.create_task(
                title=f"Refresh: {content_title}",
                description=f"Content needs refresh\n\nRecommendations:\n{rec_text}",
                project_id=project_id,
                priority=refresh_item.get("priority", TaskPriority.MEDIUM.value),
                due_date=(datetime.now() + timedelta(days=int(effort * 3))).isoformat()
            )

            # Start at REVISE stage since content already exists
            task["stage"] = WorkflowStage.REVISE.value

            task["metadata"] = {
                "source": "content_refresh",
                "content_id": refresh_item.get("content_id"),
                "staleness_score": refresh_item.get("staleness_score")
            }

            logger.info(f"Generated refresh task: {content_title}")
            return task

        except Exception as e:
            logger.error(f"Error generating refresh task: {str(e)}")
            raise
