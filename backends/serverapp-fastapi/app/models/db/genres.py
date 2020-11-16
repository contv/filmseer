from tortoise import fields
from tortoise.models import Model

from app.utils.unique_id import id, to_uuid

from .movies import Movies


def _new_uuid():
    return to_uuid(id())


"""
This model represents a genre. There is a 1:* relationship
from movie:genre.
"""

class Genres(Model):
    # Data fields
    genre_id = fields.UUIDField(pk=True, default=_new_uuid)
    name = fields.CharField(max_length=50, unique=True)
    create_date = fields.DatetimeField(auto_now_add=True)
    delete_date = fields.DatetimeField(null=True)

    # Relational fields
    movies: fields.ManyToManyRelation[Movies]

    class Meta:
        table = "genres"


__all__ = ["Genres"]
