"""Unit tests for the permission checks — pure, no server, no network."""
import pytest

from backend.app.models import TaskConfig
from backend.app.permissions import (
    PermissionDenied,
    check_record_access,
    check_report_destination,
)

COLLECTOR = "http://127.0.0.1:9100/collect"


def task(enforce: bool) -> TaskConfig:
    return TaskConfig(
        ticket_id=1,
        authorized_customer_id=1,
        approved_destinations=["reports@example.test"],
        enforce=enforce,
    )


def test_enforced_blocks_unauthorized_record():
    with pytest.raises(PermissionDenied):
        check_record_access(task(True), 2)


def test_enforced_allows_authorized_record():
    check_record_access(task(True), 1)  # no raise


def test_disabled_allows_any_record():
    check_record_access(task(False), 999)  # no raise


def test_enforced_blocks_unapproved_destination():
    with pytest.raises(PermissionDenied):
        check_report_destination(task(True), COLLECTOR)


def test_enforced_allows_approved_destination():
    check_report_destination(task(True), "reports@example.test")


def test_disabled_allows_any_destination():
    check_report_destination(task(False), COLLECTOR)  # no raise
