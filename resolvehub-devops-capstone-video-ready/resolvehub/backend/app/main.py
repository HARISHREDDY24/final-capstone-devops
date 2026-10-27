import os
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import func, text
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from . import models, schemas

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Alembic is used for managed deployments; create_all keeps a fresh local SQLite run convenient.
    if os.getenv("AUTO_CREATE_TABLES", "true").lower() == "true":
        Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="ResolveHub Support API", version="1.0.0", description="Support ticket management API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=os.getenv("CORS_ORIGINS", "*").split(","), allow_credentials=False, allow_methods=["*"], allow_headers=["*"])
Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=True)

@app.get("/")
def root():
    return {"name": "ResolveHub API", "docs": "/docs", "health": "/health"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/ready")
def ready(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc

@app.get("/api/tickets", response_model=list[schemas.TicketOut])
def list_tickets(status: str | None = None, priority: str | None = None, search: str | None = Query(default=None, max_length=160), limit: int = Query(default=100, ge=1, le=200), offset: int = Query(default=0, ge=0), db: Session = Depends(get_db)):
    query = db.query(models.Ticket)
    if status: query = query.filter(models.Ticket.status == status)
    if priority: query = query.filter(models.Ticket.priority == priority)
    if search: query = query.filter(models.Ticket.title.ilike(f"%{search}%"))
    return query.order_by(models.Ticket.created_at.desc(), models.Ticket.id.desc()).offset(offset).limit(limit).all()

@app.get("/api/tickets/stats")
def ticket_stats(db: Session = Depends(get_db)):
    total = db.query(func.count(models.Ticket.id)).scalar() or 0
    by_status = dict(db.query(models.Ticket.status, func.count(models.Ticket.id)).group_by(models.Ticket.status).all())
    by_priority = dict(db.query(models.Ticket.priority, func.count(models.Ticket.id)).group_by(models.Ticket.priority).all())
    return {"total": total, "open": by_status.get("Open", 0), "in_progress": by_status.get("In Progress", 0), "resolved": by_status.get("Resolved", 0), "urgent": by_priority.get("Urgent", 0), "by_status": by_status, "by_priority": by_priority}

@app.get("/api/tickets/{ticket_id}", response_model=schemas.TicketOut)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket: raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@app.post("/api/tickets", response_model=schemas.TicketOut, status_code=201)
def create_ticket(payload: schemas.TicketCreate, db: Session = Depends(get_db)):
    ticket = models.Ticket(**payload.model_dump())
    db.add(ticket); db.commit(); db.refresh(ticket)
    return ticket

@app.put("/api/tickets/{ticket_id}", response_model=schemas.TicketOut)
def update_ticket(ticket_id: int, payload: schemas.TicketUpdate, db: Session = Depends(get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket: raise HTTPException(status_code=404, detail="Ticket not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        if value is not None: setattr(ticket, key, value)
    db.commit(); db.refresh(ticket)
    return ticket

@app.delete("/api/tickets/{ticket_id}", status_code=204)
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket: raise HTTPException(status_code=404, detail="Ticket not found")
    db.delete(ticket); db.commit()
    return Response(status_code=204)
