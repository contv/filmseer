from tortoise import fields
from tortoise.models import Model

from app.utils.unique_id import id, to_uuid


def _new_uuid():
    return to_uuid(id())


class MovieGenres(Model):
    moviegenre_id = fields.UUIDField(pk=True)
    movie = fields.ForeignKeyField("models.Movies")
    genre = fields.ForeignKeyField("models.Genres")
    create_date = fields.DatetimeField(auto_now_add=True)
    delete_date = fields.DatetimeField(null=True)

    class Meta:
        table = "movie_genres"
        unique_together = ("movie", "genre")


__all__ = ["MovieGenres"]
