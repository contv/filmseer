from tortoise import fields
from tortoise.models import Model

from app.utils.unique_id import id, to_uuid


def _new_uuid():
    return to_uuid(id())


class Users(Model):
    user_id = fields.UUIDField(pk=True, default=_new_uuid)
    username = fields.CharField(max_length=32)
    password_hash = fields.CharField(max_length=255)
    profile_image_id = fields.ForeignKeyField(model_name='models.ProfileImages', null=True)
    description = fields.CharField(max_length=140, null=True)
    role = fields.CharField(max_length=16, default='user') #may need changing, i.e. Do we want an enum field?
    last_login_date = fields.DatetimeField(auto_now_add=True)
    last_login_ip = fields.CharField(max_length=32, null=True)
    create_date = fields.DatetimeField(auto_now_add=True)
    delete_date = fields.DatetimeField()

__all__ = ["Users"]
