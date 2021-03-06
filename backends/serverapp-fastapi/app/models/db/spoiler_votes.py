from tortoise import fields
from tortoise.models import Model

from app.utils.unique_id import id, to_uuid


def _new_uuid():
    return to_uuid(id())


"""
This model represents a spoiler vote given to a particular review, 
associated with a user.
"""

class SpoilerVotes(Model):
    spoiler_vote_id = fields.UUIDField(pk=True, default=_new_uuid)
    user = fields.ForeignKeyField("models.Users")
    review = fields.ForeignKeyField("models.Reviews", related_name="spoiler_votes")
    create_date = fields.DatetimeField(auto_now_add=True)
    delete_date = fields.DatetimeField(null=True)

    class Meta:
        table = "spoiler_votes"
        unique_together = ("user", "review")


__all__ = ["SpoilerVotes"]
