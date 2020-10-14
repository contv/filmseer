from tortoise import fields
from tortoise.models import Model

from app.utils.unique_id import id, to_uuid


def _new_uuid():
    return to_uuid(id())


class ProfileImages(Model):
    image_id = fields.UUIDField(pk=True, default=_new_uuid)
    content = fields.BinaryField()
    create_date = fields.DatetimeField(auto_now_add=True)
    delete_date = fields.DatetimeField(null=True)

__all__ = ["ProfileImages"]
