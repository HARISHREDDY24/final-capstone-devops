"""Idempotently add sample tasks for the classroom demo."""
from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .database import get_engine
from .models import Task

SAMPLE_TASKS = [
    {
        "title": "Finalize API contract",
        "description": "Review CRUD endpoints and response schemas",
        "status": "Done",
        "priority": "High",
        "assignee": "Harish",
        "due_date": date.today() - timedelta(days=1),
    },
    {
        "title": "Build responsive dashboard",
        "description": "Polish task table, filters, and empty states",
        "status": "In Progress",
        "priority": "High",
        "assignee": "Aarav",
        "due_date": date.today() + timedelta(days=2),
    },
    {
        "title": "Add container health checks",
        "description": "Verify liveness and readiness endpoints",
        "status": "In Progress",
        "priority": "Medium",
        "assignee": "Harish",
        "due_date": date.today() + timedelta(days=1),
    },
    {
        "title": "Configure Trivy image scans",
        "description": "Block publishing for HIGH and CRITICAL findings",
        "status": "Todo",
        "priority": "High",
        "assignee": "Mira",
        "due_date": date.today() + timedelta(days=4),
    },
    {
        "title": "Prepare monitoring walkthrough",
        "description": "Show request rate, error rate, and p95 latency",
        "status": "Todo",
        "priority": "Low",
        "assignee": None,
        "due_date": date.today() + timedelta(days=6),
    },
]


def main() -> None:
    engine = get_engine()
    # Migrations should be applied first; this script intentionally does not call create_all().
    with Session(engine) as session:
        existing = session.scalar(select(func.count()).select_from(Task)) or 0
        if existing:
            print(f"Seed skipped: {existing} task(s) already exist.")
            return
        session.add_all(Task(**task) for task in SAMPLE_TASKS)
        session.commit()
        print(f"Inserted {len(SAMPLE_TASKS)} demo tasks.")


if __name__ == "__main__":
    main()
