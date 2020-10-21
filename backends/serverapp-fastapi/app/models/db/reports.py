from tortoise import fields
from tortoise.models import Model

from app.utils.unique_id import id, to_uuid


def _new_uuid():
    return to_uuid(id())


class Reports(Model):
    report_id = fields.UUIDField(pk=True, default=_new_uuid)
    user = fields.ForeignKeyField("models.Users", related_name="reports")
    movie = fields.ForeignKeyField("models.Movies", related_name="reports")
    field_name = fields.CharField(max_length=50)
    field_existing_value = fields.TextField(default="")
    field_new_value = fields.TextField(default="")
    description = fields.TextField(default="")
    approved = fields.BooleanField(default=False)
    create_date = fields.DatetimeField(auto_now_add=True)
    delete_date = fields.DatetimeField(null=True)

    class Meta:
        table = "reports"


__all__ = ["Reports"]
