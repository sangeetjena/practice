"""Reserve external effects durably; uncertain outcomes require reconciliation.

Example: if SMTP accepted mail and the process died before saving the result,
a replay returns a failed/uncertain result instead of blindly sending it again.
"""

from sqlalchemy.exc import IntegrityError

from ..actions import ActionExecutor
from ..models import ActionResult, ActionStatus
from .database import records


class DurableActionExecutor(ActionExecutor):
    def execute(self, action):
        existing = self.store.get_action_result(action.id)
        if existing:
            return existing
        try:
            with self.store.db.engine.begin() as conn:
                conn.execute(
                    records.insert().values(
                        tenant_id=self.store.tenant_id,
                        kind="effect_reservation",
                        id=action.id,
                        payload={"state": "started"},
                    )
                )
        except IntegrityError:
            return ActionResult(
                action_id=action.id,
                status=ActionStatus.FAILED,
                message="Outcome uncertain: reconcile the external system before retrying this action.",
            )
        return super().execute(action)
