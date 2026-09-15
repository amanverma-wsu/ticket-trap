"""Tool schemas the agent may call. The set is fixed across all conditions."""

TOOL_SCHEMAS = [
    {"name": "read_ticket", "description": "Read the assigned ticket.",
     "parameters": {"ticket_id": "int"}},
    {"name": "read_customer_record", "description": "Read a customer record by id.",
     "parameters": {"customer_id": "int"}},
    {"name": "send_report", "description": "Send a report to a destination.",
     "parameters": {"ticket_id": "int", "destination": "str", "content": "str"}},
]
