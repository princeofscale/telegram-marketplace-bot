from __future__ import annotations
from typing import TYPE_CHECKING

from bot.database.models import AuditLogModel

if TYPE_CHECKING:
    from bot.modules.audit.events import AuditEvent


def add_audit_log(session, event: AuditEvent) -> AuditLogModel:  # noqa: ANN001
    log = AuditLogModel(
        actor_id=event.actor_id,
        action=event.action.value,
        target_id=event.target_id,
        payload=event.payload,
    )
    session.add(log)
    return log
