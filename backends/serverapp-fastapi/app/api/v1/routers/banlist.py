from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request
from humps import camelize
from pydantic import BaseModel
from tortoise.exceptions import OperationalError

from app.models.common import ListResponse
from app.models.db.banlists import Banlists
from app.utils.wrapper import ApiException, Wrapper, wrap

router = APIRouter()
override_prefix = None
override_prefix_all = None


class UserBanlistResponse(BaseModel):
    banlist_id: str
    banned_user_id: str

    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True


@router.get(
    "/", tags=["banlist"], response_model=Wrapper[ListResponse[UserBanlistResponse]]
)
async def get_banlist(request: Request):
    user_id = request.session.get("user_id")

    if not user_id:
        return ApiException(401, 2500, "You must be logged in to see your banlist.")

    items = [
        UserBanlistResponse(
            banlist_id=str(banlist_item.banlist_id),
            banned_user_id=str(banlist_item.banned_user_id),
        )
        for banlist_item in await Banlists.filter(
            user_id=user_id, delete_date=None
        ).prefetch_related("banning_user_id", "banned_user_id")
    ]

    return wrap({"items": items})