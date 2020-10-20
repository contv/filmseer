from tortoise import fields
from tortoise.models import Model

from app.utils.unique_id import id, to_uuid


def _new_uuid():
    return to_uuid(id())


class Wishlists(Model):
    # Data fields
    wishlist_id = fields.UUIDField(pk=True, default=_new_uuid)
    user = fields.ForeignKeyField("models.Users")
    movie = fields.ForeignKeyField("models.Movies")
    create_date = fields.DatetimeField(auto_now_add=True)
    delete_date = fields.DatetimeField(null=True)

    class Meta:
        table = "wishlists"
        unique_together = (("movie", "user"))


__all__ = ["Wishlists"]
