from tortoise import fields
from tortoise.models import Model

from app.utils.unique_id import id, to_uuid

from .genres import Genres
from .movies import Movies


def _new_uuid():
    return to_uuid(id())


class MovieGenres(Model):
    moviegenre_id = fields.UUIDField(pk=True, default=_new_uuid)
    movie = fields.ForeignKeyField("models.Movies")
    genre = fields.ForeignKeyField("models.Genres")
    create_date = fields.DatetimeField(auto_now_add=True)
    delete_date = fields.DatetimeField(null=True)

    class Meta:
        table = "movie_genres"


__all__ = ["MovieGenres"]
