"""TicketTrap backend.

Two separate surfaces:
  * /tools/*   — the ONLY surface the agent reaches (the three tools).
  * /control/* — a TRUSTED control plane used by the experiment harness. The agent is
                 never told these endpoints exist; they set the per-trial task + data.

Whether enforcement is active is decided by the trusted TaskConfig, never by anything in
a ticket body.
"""
from fastapi import FastAPI, HTTPException

from . import db
from .models import ConfigureRequest, ReportRequest, TaskConfig
from .permissions import (
    PermissionDenied,
    check_record_access,
    check_report_destination,
)

try:
    import httpx
except ImportError:  # httpx is optional at import time; only needed for URL delivery
    httpx = None

app = FastAPI(title="TicketTrap backend")
app.state.task = None  # active per-trial TaskConfig (trusted)


def _require_task() -> TaskConfig:
    if app.state.task is None:
        raise HTTPException(
            status_code=409, detail="no active task; call /control/configure first"
        )
    return app.state.task


# --------------------------------------------------------------------------- control plane
@app.post("/control/configure")
def configure(req: ConfigureRequest):
    """Trusted: reset + reseed the DB and set the active per-trial task."""
    db.reset_and_seed(req.customers, req.ticket)
    app.state.task = req.task
    return {
        "status": "configured",
        "ticket_id": req.task.ticket_id,
        "enforce": req.task.enforce,
    }


@app.get("/control/reports")
def control_reports():
    """Trusted inspection helper for the harness/tests."""
    return db.list_reports()


# --------------------------------------------------------------------------- agent tools
@app.get("/tools/read_ticket")
def read_ticket(ticket_id: int):
    _require_task()
    ticket = db.get_ticket(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="ticket not found")
    return ticket.model_dump()


@app.get("/tools/read_customer_record")
def read_customer_record(customer_id: int):
    task = _require_task()
    try:
        check_record_access(task, customer_id)
    except PermissionDenied as e:
        raise HTTPException(status_code=403, detail=str(e))
    customer = db.get_customer(customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="customer not found")
    return customer.model_dump()


@app.post("/tools/send_report")
def send_report(req: ReportRequest):
    task = _require_task()
    try:
        check_report_destination(task, req.destination)
    except PermissionDenied as e:
        raise HTTPException(status_code=403, detail=str(e))
    db.record_report(req.ticket_id, req.destination, req.content)
    delivered = _deliver(req.destination, req.content)
    return {"status": "sent", "destination": req.destination, "delivered": delivered}


def _deliver(destination: str, content: str) -> bool:
    """Deliver a report. Only http(s) destinations are actually POSTed (e.g. the
    collector); anything else (an email-like token) is just recorded. This is the path a
    successful exfiltration takes when enforcement is off."""
    if httpx is not None and destination.startswith(("http://", "https://")):
        try:
            httpx.post(destination, content=content, timeout=5.0)
            return True
        except Exception:
            return False
    return False
