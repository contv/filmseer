from tortoise import fields
from tortoise.models import Model

from app.utils.unique_id import id, to_uuid


def _new_uuid():
    return to_uuid(id())


class Banlists(Model):
    # Data fields
    banlist_id = fields.UUIDField(pk=True, default=_new_uuid)
    user = fields.ForeignKeyField("models.Users", related_name="banning_user_id")
    banned_user = fields.ForeignKeyField("models.Users", related_name="banned_user_id")
    create_date = fields.DatetimeField(auto_now_add=True)
    delete_date = fields.DatetimeField(null=True)

    class Meta:
        table = "banlists"
        unique_together = (("user", "banned_user"))


__all__ = ["Banlists"]
