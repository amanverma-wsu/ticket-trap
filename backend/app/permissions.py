"""Application-enforced permission checks (the core of defense config 3)."""
from .models import TaskConfig


class PermissionDenied(Exception):
    """Raised when an enforced check blocks a tool action."""


def check_record_access(task: TaskConfig, customer_id: int) -> None:
    if task.enforce and customer_id != task.authorized_customer_id:
        raise PermissionDenied(
            f"read of customer {customer_id} is not authorized for this task"
        )


def check_report_destination(task: TaskConfig, destination: str) -> None:
    if task.enforce and destination not in set(task.approved_destinations):
        raise PermissionDenied(
            f"destination {destination!r} is not an approved report destination"
        )
