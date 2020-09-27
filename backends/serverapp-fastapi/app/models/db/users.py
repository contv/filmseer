from tortoise import fields
from tortoise.models import Model

from app.utils.unique_id import id, to_uuid


def _new_uuid():
    return to_uuid(id())


class User(Model):
    id = fields.UUIDField(pk=True, default=_new_uuid)
    username = fields.CharField(max_length=32)
    password = fields.CharField(max_length=255)
