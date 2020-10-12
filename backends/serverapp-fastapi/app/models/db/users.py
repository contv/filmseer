from tortoise import fields
from tortoise.models import Model

from app.utils.unique_id import id, to_uuid


def _new_uuid():
    return to_uuid(id())


class User(Model):
    userid = fields.UUIDField(pk=True, default=_new_uuid, source_field="userID")
    username = fields.CharField(max_length=32)
    password_hash = fields.CharField(max_length=255, source_field="passwordHash")
    create_date = fields.DatetimeField(auto_now_add=True, source_field="createDate")


__all__ = ["User"]  # This is optional
