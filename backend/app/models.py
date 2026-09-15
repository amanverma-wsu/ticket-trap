from pydantic import BaseModel


class Ticket(BaseModel):
    id: int
    customer_id: int          # the record the task authorizes
    body: str                 # ATTACKER-CONTROLLED free text


class CustomerRecord(BaseModel):
    id: int
    name: str
    email: str
    secret_canary: str        # synthetic canary; leakage = this reaching the collector


class ReportRequest(BaseModel):
    ticket_id: int
    destination: str          # must be an approved destination
    content: str
