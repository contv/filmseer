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

class UserInBanlistResponse(BaseModel):
    inbanlist: bool



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
        )
    ]

    return wrap({"items": items})

@router.get("/{banned_user_id}", response_model=Wrapper[UserInBanlistResponse])
async def is_user_banlist(request: Request, banned_user_id: str):
    user_id = request.session.get("user_id")

    if not user_id:
        return ApiException(401, 2500, "You must be logged in to see your wishlist.")
    inbanlist = (
        await Banlists.filter(
            banned_user_id=banned_user_id, user_id=user_id, delete_date=None
        ).first()
        is not None
    )

    return wrap({"inbanlist": inbanlist})

@router.put("/{banned_user_id}")
async def add_to_banlist(request: Request, banned_user_id: str):
    user_id = request.session.get("user_id")

    if not user_id:
        return ApiException(401, 2500, "You must be logged in to add to wishlist.")

    exists_in_banlist = await Banlists.get_or_none(
        banned_user_id=banned_user_id, user_id=user_id
    )

    if exists_in_banlist is not None:
        try:
            exists_in_banlist.delete_date = None
            await exists_in_banlist.save()
        except OperationalError:
            return ApiException(401, 2501, "You cannot do that.")
    else:
        try:
            await Banlists(banned_user_id=banned_user_id, user_id=user_id).save()
        except OperationalError:
            return ApiException(401, 2501, "You cannot do that.")

    return wrap({})

@router.delete("/{banned_user_id}")
async def delete_from_banlist(request: Request, banned_user_id: str):
    user_id = request.session.get("user_id")

    if not user_id:
        return ApiException(401, 2500, "You must be logged in to delete from banlist.")
    exists_in_banlist = await Banlists.get_or_none(
        banned_user_id=banned_user_id, user_id=user_id
    )

    if exists_in_banlist is not None:
        try:
            exists_in_banlist.delete_date = datetime.now()
            await exists_in_banlist.save()
        except OperationalError:
            return ApiException(401, 2501, "You cannot do that.")
    else:
        return ApiException(401, 2800, "You haven't added this user to banlist yet.")

    return wrap({})
