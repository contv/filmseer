from tortoise import fields
from tortoise.models import Model

from app.utils.unique_id import id, to_uuid

from .movies import Movies


def _new_uuid():
    return to_uuid(id())


class People(Model):
    # Data fields
    person_id = fields.UUIDField(pk=True, default=_new_uuid)
    image = fields.CharField(max_length=300, null=True)
    name = fields.CharField(max_length=300)
    create_date = fields.DatetimeField(auto_now_add=True)
    delete_date = fields.DatetimeField(null=True)

    # Relational fields
    movies = fields.ManyToManyRelation[Movies]

    class Meta:
        table = "people"

    def __str__(self):
        return self.name


__all__ = ["People"]
