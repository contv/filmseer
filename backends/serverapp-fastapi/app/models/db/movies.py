from tortoise import fields
from tortoise.models import Model

from app.utils.unique_id import id, to_uuid


def _new_uuid():
    return to_uuid(id())


class Movies(Model):
    # Data fields
    movie_id = fields.UUIDField(pk=True, default=_new_uuid)
    title = fields.CharField(max_length=300)
    release_date = fields.DatetimeField()
    description = fields.CharField(max_length=1000, null=True)
    image = fields.CharField(max_length=300, null=True)
    trailer = fields.CharField(max_length=300, null=True)
    num_reviews = fields.IntField(default=0)
    cumulative_rating = fields.FloatField(default=0)
    num_votes = fields.IntField(default=0)
    create_date = fields.DatetimeField(auto_now_add=True)
    delete_date = fields.DatetimeField(null=True)

    # Relational fields
    genre: fields.ManyToManyRelation["Genres"] = fields.ManyToManyField(  # noqa: F821
        "models.Genres",
        related_name="movies",
        through="movie_genres",
        backward_key="movie_id",
        forward_key="genre_id",
    )
    people: fields.ManyToManyRelation["People"] = fields.ManyToManyField(  # noqa: F821
        "models.People",
        related_name="movies",
        through="positions",
        backward_key="movie_id",
        forward_key="person_id",
    )
    ratings: fields.ReverseRelation["Ratings"]

    class Meta:
        table = "movies"

    def __str__(self):
        return self.title


__all__ = ["Movies"]
