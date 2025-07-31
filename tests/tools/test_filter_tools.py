"""
Unit tests for the filter tools module.
"""

from unittest.mock import patch, MagicMock
import pytest
from datetime import datetime, timedelta

from ticktick_mcp.tools.filter_tools import (
    filter_tasks_by_status,
    filter_tasks_by_priority,
    filter_tasks_by_due_date,
    filter_tasks_by_project,
    filter_tasks_by_tags,
    get_overdue_tasks,
    get_today_tasks,
    get_upcoming_tasks,
)


class TestFilterTasksByStatus:
    """Test the filter_tasks_by_status function."""

    @pytest.mark.asyncio
    async def test_filter_completed_tasks(self, fake_ticktick_client):
        """Test filtering for completed tasks."""
        mock_tasks = [
            {"id": "1", "title": "Task 1", "status": 2},  # completed
            {"id": "2", "title": "Task 2", "status": 0},  # incomplete
            {"id": "3", "title": "Task 3", "status": 2},  # completed
        ]
        fake_ticktick_client.task.get.return_value = mock_tasks

        with patch(
            "ticktick_mcp.tools.filter_tools.get_client",
            return_value=fake_ticktick_client,
        ):
            result = await filter_tasks_by_status("completed")

        assert len(result) == 2
        assert all(task["status"] == 2 for task in result)

    @pytest.mark.asyncio
    async def test_filter_incomplete_tasks(self, fake_ticktick_client):
        """Test filtering for incomplete tasks."""
        mock_tasks = [
            {"id": "1", "title": "Task 1", "status": 0},  # incomplete
            {"id": "2", "title": "Task 2", "status": 2},  # completed
            {"id": "3", "title": "Task 3", "status": 0},  # incomplete
        ]
        fake_ticktick_client.task.get.return_value = mock_tasks

        with patch(
            "ticktick_mcp.tools.filter_tools.get_client",
            return_value=fake_ticktick_client,
        ):
            result = await filter_tasks_by_status("incomplete")

        assert len(result) == 2
        assert all(task["status"] == 0 for task in result)

    @pytest.mark.asyncio
    async def test_filter_invalid_status(self, fake_ticktick_client):
        """Test filtering with invalid status."""
        with patch(
            "ticktick_mcp.tools.filter_tools.get_client",
            return_value=fake_ticktick_client,
        ):
            with pytest.raises(ValueError, match="Invalid status"):
                await filter_tasks_by_status("invalid")


class TestFilterTasksByPriority:
    """Test the filter_tasks_by_priority function."""

    @pytest.mark.asyncio
    async def test_filter_high_priority_tasks(self, fake_ticktick_client):
        """Test filtering for high priority tasks."""
        mock_tasks = [
            {"id": "1", "title": "Task 1", "priority": 1},  # high
            {"id": "2", "title": "Task 2", "priority": 0},  # none
            {"id": "3", "title": "Task 3", "priority": 1},  # high
        ]
        fake_ticktick_client.task.get.return_value = mock_tasks

        with patch(
            "ticktick_mcp.tools.filter_tools.get_client",
            return_value=fake_ticktick_client,
        ):
            result = await filter_tasks_by_priority("high")

        assert len(result) == 2
        assert all(task["priority"] == 1 for task in result)

    @pytest.mark.asyncio
    async def test_filter_medium_priority_tasks(self, fake_ticktick_client):
        """Test filtering for medium priority tasks."""
        mock_tasks = [
            {"id": "1", "title": "Task 1", "priority": 3},  # medium
            {"id": "2", "title": "Task 2", "priority": 1},  # high
            {"id": "3", "title": "Task 3", "priority": 3},  # medium
        ]
        fake_ticktick_client.task.get.return_value = mock_tasks

        with patch(
            "ticktick_mcp.tools.filter_tools.get_client",
            return_value=fake_ticktick_client,
        ):
            result = await filter_tasks_by_priority("medium")

        assert len(result) == 2
        assert all(task["priority"] == 3 for task in result)

    @pytest.mark.asyncio
    async def test_filter_low_priority_tasks(self, fake_ticktick_client):
        """Test filtering for low priority tasks."""
        mock_tasks = [
            {"id": "1", "title": "Task 1", "priority": 5},  # low
            {"id": "2", "title": "Task 2", "priority": 1},  # high
            {"id": "3", "title": "Task 3", "priority": 5},  # low
        ]
        fake_ticktick_client.task.get.return_value = mock_tasks

        with patch(
            "ticktick_mcp.tools.filter_tools.get_client",
            return_value=fake_ticktick_client,
        ):
            result = await filter_tasks_by_priority("low")

        assert len(result) == 2
        assert all(task["priority"] == 5 for task in result)

    @pytest.mark.asyncio
    async def test_filter_no_priority_tasks(self, fake_ticktick_client):
        """Test filtering for tasks with no priority."""
        mock_tasks = [
            {"id": "1", "title": "Task 1", "priority": 0},  # none
            {"id": "2", "title": "Task 2", "priority": 1},  # high
            {"id": "3", "title": "Task 3", "priority": 0},  # none
        ]
        fake_ticktick_client.task.get.return_value = mock_tasks

        with patch(
            "ticktick_mcp.tools.filter_tools.get_client",
            return_value=fake_ticktick_client,
        ):
            result = await filter_tasks_by_priority("none")

        assert len(result) == 2
        assert all(task["priority"] == 0 for task in result)


class TestFilterTasksByDueDate:
    """Test the filter_tasks_by_due_date function."""

    @pytest.mark.asyncio
    async def test_filter_tasks_due_today(self, fake_ticktick_client):
        """Test filtering tasks due today."""
        today = datetime.now().strftime("%Y-%m-%d")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        mock_tasks = [
            {"id": "1", "title": "Task 1", "dueDate": f"{today}T23:59:59Z"},
            {"id": "2", "title": "Task 2", "dueDate": f"{tomorrow}T23:59:59Z"},
            {"id": "3", "title": "Task 3", "dueDate": f"{today}T12:00:00Z"},
        ]
        fake_ticktick_client.task.get.return_value = mock_tasks

        with patch(
            "ticktick_mcp.tools.filter_tools.get_client",
            return_value=fake_ticktick_client,
        ):
            result = await filter_tasks_by_due_date(today)

        assert len(result) == 2
        assert all(today in task["dueDate"] for task in result)

    @pytest.mark.asyncio
    async def test_filter_tasks_due_range(self, fake_ticktick_client):
        """Test filtering tasks within date range."""
        start_date = "2024-01-01"
        end_date = "2024-01-03"

        mock_tasks = [
            {"id": "1", "title": "Task 1", "dueDate": "2024-01-01T23:59:59Z"},
            {"id": "2", "title": "Task 2", "dueDate": "2024-01-05T23:59:59Z"},
            {"id": "3", "title": "Task 3", "dueDate": "2024-01-02T23:59:59Z"},
        ]
        fake_ticktick_client.task.get.return_value = mock_tasks

        with patch(
            "ticktick_mcp.tools.filter_tools.get_client",
            return_value=fake_ticktick_client,
        ):
            result = await filter_tasks_by_due_date(start_date, end_date)

        assert len(result) == 2  # Tasks on 01-01 and 01-02


class TestFilterTasksByProject:
    """Test the filter_tasks_by_project function."""

    @pytest.mark.asyncio
    async def test_filter_tasks_by_project_id(self, fake_ticktick_client):
        """Test filtering tasks by project ID."""
        mock_tasks = [
            {"id": "1", "title": "Task 1", "projectId": "proj123"},
            {"id": "2", "title": "Task 2", "projectId": "proj456"},
            {"id": "3", "title": "Task 3", "projectId": "proj123"},
        ]
        fake_ticktick_client.task.get.return_value = mock_tasks

        with patch(
            "ticktick_mcp.tools.filter_tools.get_client",
            return_value=fake_ticktick_client,
        ):
            result = await filter_tasks_by_project("proj123")

        assert len(result) == 2
        assert all(task["projectId"] == "proj123" for task in result)

    @pytest.mark.asyncio
    async def test_filter_tasks_no_project_match(self, fake_ticktick_client):
        """Test filtering with no matching projects."""
        mock_tasks = [
            {"id": "1", "title": "Task 1", "projectId": "proj123"},
            {"id": "2", "title": "Task 2", "projectId": "proj456"},
        ]
        fake_ticktick_client.task.get.return_value = mock_tasks

        with patch(
            "ticktick_mcp.tools.filter_tools.get_client",
            return_value=fake_ticktick_client,
        ):
            result = await filter_tasks_by_project("proj999")

        assert len(result) == 0


class TestFilterTasksByTags:
    """Test the filter_tasks_by_tags function."""

    @pytest.mark.asyncio
    async def test_filter_tasks_single_tag(self, fake_ticktick_client):
        """Test filtering tasks by a single tag."""
        mock_tasks = [
            {"id": "1", "title": "Task 1", "tags": ["work", "urgent"]},
            {"id": "2", "title": "Task 2", "tags": ["personal"]},
            {"id": "3", "title": "Task 3", "tags": ["work", "meeting"]},
        ]
        fake_ticktick_client.task.get.return_value = mock_tasks

        with patch(
            "ticktick_mcp.tools.filter_tools.get_client",
            return_value=fake_ticktick_client,
        ):
            result = await filter_tasks_by_tags(["work"])

        assert len(result) == 2
        assert all("work" in task["tags"] for task in result)

    @pytest.mark.asyncio
    async def test_filter_tasks_multiple_tags(self, fake_ticktick_client):
        """Test filtering tasks by multiple tags."""
        mock_tasks = [
            {"id": "1", "title": "Task 1", "tags": ["work", "urgent"]},
            {"id": "2", "title": "Task 2", "tags": ["work", "meeting", "urgent"]},
            {"id": "3", "title": "Task 3", "tags": ["personal", "urgent"]},
        ]
        fake_ticktick_client.task.get.return_value = mock_tasks

        with patch(
            "ticktick_mcp.tools.filter_tools.get_client",
            return_value=fake_ticktick_client,
        ):
            result = await filter_tasks_by_tags(["work", "urgent"])

        assert len(result) == 2
        assert all(
            all(tag in task["tags"] for tag in ["work", "urgent"]) for task in result
        )


class TestGetOverdueTasks:
    """Test the get_overdue_tasks function."""

    @pytest.mark.asyncio
    async def test_get_overdue_tasks(self, fake_ticktick_client):
        """Test getting overdue tasks."""
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        mock_tasks = [
            {
                "id": "1",
                "title": "Overdue 1",
                "dueDate": f"{yesterday}T23:59:59Z",
                "status": 0,
            },
            {
                "id": "2",
                "title": "Future",
                "dueDate": f"{tomorrow}T23:59:59Z",
                "status": 0,
            },
            {
                "id": "3",
                "title": "Overdue 2",
                "dueDate": f"{yesterday}T12:00:00Z",
                "status": 0,
            },
            {
                "id": "4",
                "title": "Overdue Done",
                "dueDate": f"{yesterday}T12:00:00Z",
                "status": 2,
            },
        ]
        fake_ticktick_client.task.get.return_value = mock_tasks

        with patch(
            "ticktick_mcp.tools.filter_tools.get_client",
            return_value=fake_ticktick_client,
        ):
            result = await get_overdue_tasks()

        assert len(result) == 2  # Only incomplete overdue tasks
        assert all(task["status"] == 0 for task in result)
        assert all(yesterday in task["dueDate"] for task in result)


class TestGetTodayTasks:
    """Test the get_today_tasks function."""

    @pytest.mark.asyncio
    async def test_get_today_tasks(self, fake_ticktick_client):
        """Test getting tasks due today."""
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        mock_tasks = [
            {"id": "1", "title": "Today 1", "dueDate": f"{today}T09:00:00Z"},
            {"id": "2", "title": "Yesterday", "dueDate": f"{yesterday}T23:59:59Z"},
            {"id": "3", "title": "Today 2", "dueDate": f"{today}T18:00:00Z"},
        ]
        fake_ticktick_client.task.get.return_value = mock_tasks

        with patch(
            "ticktick_mcp.tools.filter_tools.get_client",
            return_value=fake_ticktick_client,
        ):
            result = await get_today_tasks()

        assert len(result) == 2
        assert all(today in task["dueDate"] for task in result)


class TestGetUpcomingTasks:
    """Test the get_upcoming_tasks function."""

    @pytest.mark.asyncio
    async def test_get_upcoming_tasks_default_days(self, fake_ticktick_client):
        """Test getting upcoming tasks with default 7 days."""
        today = datetime.now()
        future_dates = [
            (today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(1, 10)
        ]

        mock_tasks = [
            {"id": "1", "title": "Tomorrow", "dueDate": f"{future_dates[0]}T12:00:00Z"},
            {
                "id": "2",
                "title": "Next week",
                "dueDate": f"{future_dates[6]}T12:00:00Z",
            },
            {
                "id": "3",
                "title": "Far future",
                "dueDate": f"{future_dates[8]}T12:00:00Z",
            },
        ]
        fake_ticktick_client.task.get.return_value = mock_tasks

        with patch(
            "ticktick_mcp.tools.filter_tools.get_client",
            return_value=fake_ticktick_client,
        ):
            result = await get_upcoming_tasks()

        assert len(result) == 2  # Only tasks within 7 days

    @pytest.mark.asyncio
    async def test_get_upcoming_tasks_custom_days(self, fake_ticktick_client):
        """Test getting upcoming tasks with custom number of days."""
        today = datetime.now()
        future_dates = [
            (today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(1, 5)
        ]

        mock_tasks = [
            {"id": "1", "title": "Day 1", "dueDate": f"{future_dates[0]}T12:00:00Z"},
            {"id": "2", "title": "Day 2", "dueDate": f"{future_dates[1]}T12:00:00Z"},
            {"id": "3", "title": "Day 4", "dueDate": f"{future_dates[3]}T12:00:00Z"},
        ]
        fake_ticktick_client.task.get.return_value = mock_tasks

        with patch(
            "ticktick_mcp.tools.filter_tools.get_client",
            return_value=fake_ticktick_client,
        ):
            result = await get_upcoming_tasks(days=3)

        assert len(result) == 2  # Only tasks within 3 days


class TestFilterToolsErrorHandling:
    """Test error handling across filter tools."""

    @pytest.mark.asyncio
    async def test_invalid_date_format(self, fake_ticktick_client):
        """Test handling of invalid date formats."""
        with patch(
            "ticktick_mcp.tools.filter_tools.get_client",
            return_value=fake_ticktick_client,
        ):
            with pytest.raises(ValueError, match="Invalid date format"):
                await filter_tasks_by_due_date("invalid-date")

    @pytest.mark.asyncio
    async def test_client_error_propagation(self, fake_ticktick_client):
        """Test that client errors are properly propagated."""
        fake_ticktick_client.task.get.side_effect = Exception("Client error")

        with patch(
            "ticktick_mcp.tools.filter_tools.get_client",
            return_value=fake_ticktick_client,
        ):
            with pytest.raises(Exception, match="Client error"):
                await filter_tasks_by_status("completed")


class TestFilterToolsLogging:
    """Test logging behavior in filter tools."""

    @pytest.mark.asyncio
    async def test_filter_operations_log_appropriately(
        self, mock_logging, fake_ticktick_client
    ):
        """Test that filter operations generate appropriate log messages."""
        fake_ticktick_client.task.get.return_value = []

        with patch(
            "ticktick_mcp.tools.filter_tools.get_client",
            return_value=fake_ticktick_client,
        ):
            await filter_tasks_by_status("completed")

        # Check for expected log messages
        log_messages = [log["message"] for log in mock_logging]
        assert any("Filtering tasks by status" in msg for msg in log_messages)
