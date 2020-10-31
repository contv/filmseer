from tortoise import fields
from tortoise.models import Model

from app.utils.unique_id import id, to_uuid


def _new_uuid():
    return to_uuid(id())


class Positions(Model):
    position_id = fields.UUIDField(pk=True)
    movie = fields.ForeignKeyField("models.Movies")
    person = fields.ForeignKeyField("models.People")
    position = fields.CharField(max_length=300, null=True)
    char_name = fields.CharField(max_length=300, null=True)
    create_date = fields.DatetimeField(auto_now_add=True)
    delete_date = fields.DatetimeField(null=True)

    class Meta:
        table = "positions"
        unique_together = ("movie", "person", "position")


__all__ = ["Positions"]
