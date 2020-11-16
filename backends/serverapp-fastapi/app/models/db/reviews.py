from tortoise import fields
from tortoise.models import Model

from app.utils.unique_id import id, to_uuid


def _new_uuid():
    return to_uuid(id())


"""
This model represents a review given to a movie by a user.
It contains text, whether or not the author flagged it as containing
a spoiler and the metadata related to funny, helpful and spoiler votes.
"""

class Reviews(Model):
    # Data fields
    review_id = fields.UUIDField(pk=True, default=_new_uuid)
    user = fields.ForeignKeyField("models.Users", related_name="reviews")
    movie = fields.ForeignKeyField("models.Movies", related_name="reviews")
    rating = fields.ForeignKeyField("models.Ratings")
    description = fields.TextField(default="")
    contains_spoiler = fields.BooleanField(default=False)
    num_spoiler = fields.IntField(default=0)
    num_helpful = fields.IntField(default=0)
    num_funny = fields.IntField(default=0)
    create_date = fields.DatetimeField(auto_now_add=True)
    delete_date = fields.DatetimeField(null=True)

    # Relational fields
    helpful_votes = fields.ReverseRelation["HelpfulVotes"]
    funny_votes = fields.ReverseRelation["FunnyVotes"]
    spoiler_votes = fields.ReverseRelation["SpoilerVotes"]

    class Meta:
        table = "reviews"
        unique_together = ("user", "movie")


__all__ = ["Reviews"]
