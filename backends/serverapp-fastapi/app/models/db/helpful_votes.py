from tortoise import fields
from tortoise.models import Model

from app.utils.unique_id import id, to_uuid


def _new_uuid():
    return to_uuid(id())


class HelpfulVotes(Model):
    helpful_vote_id = fields.UUIDField(pk=True, default=_new_uuid)
    user = fields.ForeignKeyField("models.Users")
    review = fields.ForeignKeyField("models.Reviews", related_name="helpful_votes")
    create_date = fields.DatetimeField(auto_now_add=True)
    delete_date = fields.DatetimeField(null=True)

    class Meta:
        table = "helpful_votes"
        unique_together = ("user", "review")


__all__ = ["HelpfulVotes"]
