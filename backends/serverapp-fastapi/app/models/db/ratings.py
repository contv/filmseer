from tortoise import fields
from tortoise.models import Model

from app.utils.unique_id import id, to_uuid


def _new_uuid():
    return to_uuid(id())


"""
This model represents a rating given for a particular movie
and by a particular user.
"""

class Ratings(Model):
    # Data fields
    rating_id = fields.UUIDField(pk=True, default=_new_uuid)
    user = fields.ForeignKeyField("models.Users", related_name="ratings")
    movie = fields.ForeignKeyField("models.Movies",  related_names="ratings")
    rating = fields.FloatField(null=True)
    create_date = fields.DatetimeField(auto_now_add=True)
    delete_date = fields.DatetimeField(null=True)

    class Meta:
        table = "ratings"
        unique_together = ("user", "movie")


__all__ = ["Ratings"]
