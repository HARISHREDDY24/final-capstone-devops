from datetime import date
from time import perf_counter
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from sqlalchemy import func, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from . import models
from .database import get_db
from .schemas import TaskCreate, TaskRead, TaskStats, TaskUpdate

app = FastAPI(
    title="TaskBoard API",
    description="REST API for the TaskBoard DevOps capstone.",
    version="1.0.0",
)

HTTP_REQUESTS = Counter(
    "taskboard_http_requests_total",
    "Total HTTP requests handled by TaskBoard",
    ["method", "path", "status_code"],
)
HTTP_DURATION = Histogram(
    "taskboard_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
)


@app.middleware("http")
async def collect_http_metrics(request, call_next):
    start = perf_counter()
    code = 500
    try:
        response = await call_next(request)
        code = response.status_code
        return response
    finally:
        route = request.scope.get("route")
        path = getattr(route, "path", "unmatched")
        HTTP_REQUESTS.labels(request.method, path, str(code)).inc()
        HTTP_DURATION.labels(request.method, path).observe(perf_counter() - start)


@app.get("/", tags=["service"])
def service_info():
    return {"service": "taskboard-api", "version": "1.0.0", "docs": "/docs"}


@app.get("/health", tags=["health"])
def health():
    """Liveness: process is running; does not require the database."""
    return {"status": "ok"}


@app.get("/ready", tags=["health"])
def ready(db: Annotated[Session, Depends(get_db)]):
    """Readiness: this instance can reach PostgreSQL."""
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return Response(
            content='{"status":"not_ready","database":"unavailable"}',
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            media_type="application/json",
        )
    return {"status": "ready", "database": "ok"}


@app.get("/metrics", tags=["monitoring"], include_in_schema=False)
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/api/tasks/stats", response_model=TaskStats, tags=["tasks"])
def task_stats(db: Annotated[Session, Depends(get_db)]):
    today = date.today()
    total = db.scalar(select(func.count()).select_from(models.Task)) or 0
    todo = db.scalar(select(func.count()).select_from(models.Task).where(models.Task.status == "Todo")) or 0
    in_progress = db.scalar(
        select(func.count()).select_from(models.Task).where(models.Task.status == "In Progress")
    ) or 0
    completed = db.scalar(select(func.count()).select_from(models.Task).where(models.Task.status == "Done")) or 0
    overdue = db.scalar(
        select(func.count()).select_from(models.Task).where(
            models.Task.due_date < today, models.Task.status != "Done"
        )
    ) or 0
    return TaskStats(
        total=total, todo=todo, in_progress=in_progress, completed=completed, overdue=overdue
    )


@app.get("/api/tasks", response_model=list[TaskRead], tags=["tasks"])
def list_tasks(
    db: Annotated[Session, Depends(get_db)],
    status_filter: Annotated[str | None, Query(alias="status", pattern="^(Todo|In Progress|Done)$")] = None,
    q: Annotated[str | None, Query(max_length=160)] = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
):
    statement = select(models.Task)
    if status_filter:
        statement = statement.where(models.Task.status == status_filter)
    if q and q.strip():
        term = f"%{q.strip()}%"
        statement = statement.where(
            models.Task.title.ilike(term) | models.Task.description.ilike(term)
        )
    statement = statement.order_by(models.Task.created_at.desc(), models.Task.id.desc())
    return list(db.scalars(statement.offset(skip).limit(limit)).all())


@app.post("/api/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED, tags=["tasks"])
def create_task(payload: TaskCreate, db: Annotated[Session, Depends(get_db)]):
    task = models.Task(**payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@app.get("/api/tasks/{task_id}", response_model=TaskRead, tags=["tasks"])
def get_task(task_id: int, db: Annotated[Session, Depends(get_db)]):
    task = db.get(models.Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.put("/api/tasks/{task_id}", response_model=TaskRead, tags=["tasks"])
def update_task(task_id: int, payload: TaskUpdate, db: Annotated[Session, Depends(get_db)]):
    task = db.get(models.Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


@app.delete("/api/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tasks"])
def delete_task(task_id: int, db: Annotated[Session, Depends(get_db)]):
    task = db.get(models.Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
