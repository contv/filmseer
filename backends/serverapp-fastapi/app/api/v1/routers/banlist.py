from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request
from humps import camelize
from pydantic import BaseModel
from tortoise.exceptions import OperationalError

from app.models.common import ListResponse
from app.models.db.banlists import Banlists
from app.models.db.users import Users
from app.utils.wrapper import ApiException, Wrapper, wrap

router = APIRouter()
override_prefix = None
override_prefix_all = None

"""
This API controller handles all routes under the prefix /banlist. It handles
banlist management.
"""


# response model includes user banning and banned user data
class UserBanlistResponse(BaseModel):
    banlist_id: str
    banned_user_id: str
    banned_username: str
    banned_user_image: Optional[str]

    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True


class UserBannedResponse(BaseModel):
    banned: bool


# gets all users on your banlist
@router.get(
    "/", tags=["banlist"], response_model=Wrapper[ListResponse[UserBanlistResponse]]
)
async def get_banlist(request: Request):
    user_id = request.session.get("user_id")

    if not user_id:
        raise ApiException(401, 2001, "You are not logged in!")

    items = []

    # returns every valid banlist user on your banlist
    for banlist_item in await Banlists.filter(user_id=user_id, delete_date=None):
        banned_user = (
            await Users.filter(
                user_id=banlist_item.banned_user_id, delete_date=None
            ).values("username", "image")
        )[0]
        items.append(
            UserBanlistResponse(
                banlist_id=str(banlist_item.banlist_id),
                banned_user_id=str(banlist_item.banned_user_id),
                banned_username=banned_user["username"],
                banned_user_image=banned_user["image"],
            )
        )

    return wrap({"items": items})


# checks whether the user is in your banlist
@router.get("/{banned_username}", response_model=Wrapper[UserBannedResponse])
async def is_user_banlist(request: Request, banned_username: str):
    user_id = request.session.get("user_id")
    if not user_id:
        raise ApiException(401, 2001, "You are not logged in!")

    if await Users.filter(username=banned_username, delete_date=None).exists():
        banned_user_id = (
            await Users.filter(username=banned_username, delete_date=None).values(
                "user_id"
            )
        )[0]["user_id"]
    else:
        raise ApiException(500, 2002, "This user no longer exists!")

    banned = (
        await Banlists.filter(
            banned_user_id=banned_user_id, user_id=user_id, delete_date=None
        ).first()
        is not None
    )

    return wrap({"banned": banned})


# adds a user to your banlist
@router.post("/{banned_username}")
async def add_to_banlist(request: Request, banned_username: str):
    user_id = request.session.get("user_id")

    if not user_id:
        raise ApiException(401, 2001, "You are not logged in!")

    # adds to banlist if it doesn't already exist, or if it is a valid user to ban
    if await Users.filter(username=banned_username, delete_date=None).exists():
        banned_user_id = (
            await Users.filter(username=banned_username, delete_date=None).values(
                "user_id"
            )
        )[0]["user_id"]
    else:
        raise ApiException(500, 2002, "This user no longer exists!")

    if user_id == banned_user_id:
        raise ApiException(401, 2040, "You cannot ban yourself.")

    exists_in_banlist = await Banlists.get_or_none(
        banned_user_id=banned_user_id, user_id=user_id
    )

    if exists_in_banlist is not None:
        try:
            exists_in_banlist.delete_date = None
            await exists_in_banlist.save()
        except OperationalError:
            raise ApiException(401, 2041, "You cannot ban that person.")
    else:
        try:
            await Banlists(banned_user_id=banned_user_id, user_id=user_id).save()
        except OperationalError:
            raise ApiException(401, 2041, "You cannot ban that person.")

    return wrap({})


@router.delete("/{banned_username}")
async def delete_from_banlist(request: Request, banned_username: str):
    user_id = request.session.get("user_id")

    if not user_id:
        raise ApiException(401, 2001, "You are not logged in!")

    # removes from banlist if it doesn't already exist, or if it is a valid user to ban
    if await Users.filter(username=banned_username, delete_date=None).exists():
        banned_user_id = (
            await Users.filter(username=banned_username, delete_date=None).values(
                "user_id"
            )
        )[0]["user_id"]
    else:
        raise ApiException(500, 2002, "This user no longer exists!")

    exists_in_banlist = await Banlists.get_or_none(
        banned_user_id=banned_user_id, user_id=user_id
    )

    if exists_in_banlist is not None:
        try:
            exists_in_banlist.delete_date = datetime.now()
            await exists_in_banlist.save()
        except OperationalError:
            raise ApiException(401, 2042, "You cannot unban that person.")
    else:
        raise ApiException(
            401, 2043, "You haven't added this user to your banlist yet."
        )

    return wrap({})
