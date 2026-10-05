"""Pydantic models. Ticket.body is ATTACKER-CONTROLLED free text; what the agent is
allowed to do comes from TaskConfig, set only via the trusted control channel."""
from pydantic import BaseModel, Field


class CustomerRecord(BaseModel):
    id: int
    name: str
    email: str
    secret_canary: str


class Ticket(BaseModel):
    id: int
    customer_id: int
    body: str


class ReportRequest(BaseModel):
    ticket_id: int
    destination: str
    content: str


class TaskConfig(BaseModel):
    ticket_id: int
    authorized_customer_id: int
    approved_destinations: list[str] = Field(default_factory=list)
    enforce: bool = False


class ConfigureRequest(BaseModel):
    task: TaskConfig
    customers: list[CustomerRecord]
    ticket: Ticket
