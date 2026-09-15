"""Application-enforced permission checks (defense config 3).

Permissions come from TRUSTED per-task settings, never from ticket content.
This is the layer the attacker cannot reach.
"""
from dataclasses import dataclass, field


@dataclass
class TaskPermissions:
    authorized_customer_id: int
    approved_destinations: set[str] = field(default_factory=set)
    enforce: bool = False           # True only in the application-enforced config


class PermissionError(Exception):
    pass


def check_record_access(perms: TaskPermissions, customer_id: int) -> None:
    if perms.enforce and customer_id != perms.authorized_customer_id:
        raise PermissionError(f"read of customer {customer_id} not authorized")


def check_report_destination(perms: TaskPermissions, destination: str) -> None:
    if perms.enforce and destination not in perms.approved_destinations:
        raise PermissionError(f"destination {destination!r} not approved")
