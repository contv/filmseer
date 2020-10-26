from fastapi import APIRouter, Request
from tortoise.exceptions import OperationalError

from app.utils.wrapper import wrap, ApiException
from app.models.db.wishlists import Wishlists

router = APIRouter()
override_prefix = None
override_prefix_all = None


@router.get("/")
async def get_wishlist(request: Request):
    user_id = request.session.get("user_id")

    if not user_id:
        return ApiException(
            401, 2500, "You must be logged in to see your wishlist."
        )

    items = await Wishlists.filter(
        user_id=user_id
    ).prefetch_related("movie")
    return wrap({"items": items})


@router.get("/{movie_id}")
async def is_movie_wishlist(request: Request, movie_id: str):
    user_id = request.session.get("user_id")

    if not user_id:
        return ApiException(
            401, 2500, "You must be logged in to see your wishlist."
        )
    added = await Wishlists.filter(
        movie_id=movie_id, user_id=user_id
    ).first() is not None

    return wrap({"added": added})


@router.put("/{movie_id}")
async def add_to_wishlist(request: Request, movie_id: str):
    user_id = request.session.get("user_id")

    if not user_id:
        return ApiException(
            401, 2500, "You must be logged in to add to wishlist."
        )

    try:
        await Wishlists(movie_id=movie_id, user_id=user_id).save()
    except OperationalError:
        return ApiException(
            401, 2501, "You cannot do that."
        )

    return wrap({})


@router.delete("/{movie_id}")
async def delete_from_wishlist(request: Request, movie_id: str):
    user_id = request.session.get("user_id")

    if not user_id:
        return ApiException(
            401, 2500, "You must be logged in to add to wishlist."
        )

    try:
        await Wishlists.filter(movie_id=movie_id, user_id=user_id).delete()
        return wrap({})
    except OperationalError:
        return ApiException(
            401, 2501, "You cannot do that."
        )
    return wrap({})
