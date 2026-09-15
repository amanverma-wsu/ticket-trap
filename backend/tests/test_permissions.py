from backend.app.permissions import TaskPermissions, check_record_access, check_report_destination, PermissionError
import pytest


def test_enforced_blocks_unauthorized_record():
    perms = TaskPermissions(authorized_customer_id=1, enforce=True)
    with pytest.raises(PermissionError):
        check_record_access(perms, customer_id=2)


def test_disabled_allows_everything():
    perms = TaskPermissions(authorized_customer_id=1, enforce=False)
    check_record_access(perms, customer_id=999)  # no raise


def test_enforced_blocks_unapproved_destination():
    perms = TaskPermissions(authorized_customer_id=1, approved_destinations={"ok@example.test"}, enforce=True)
    with pytest.raises(PermissionError):
        check_report_destination(perms, "evil@attacker.test")
