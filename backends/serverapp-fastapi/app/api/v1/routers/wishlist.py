from fastapi import APIRouter, Request
# from tortoise.exceptions import OperationalError
from typing import List

# from app.models.db.wishlists import Wishlists
from app.utils.wrapper import wrap

router = APIRouter()
override_prefix = None
override_prefix_all = None


@router.get("/")
async def get_wishlist(request: Request) -> List[dict]:
    return wrap([])


@router.get("/{movie_id}")
async def is_movie_wishlist(request: Request, movie_id: str) -> bool:
    return wrap(True)


@router.put("/{movie_id}")
async def add_to_wishlist(request: Request, movie_id: str):
    return wrap({})


@router.delete("/{movie_id}")
async def delete_from_wishlist(request: Request, movie_id: str):
    return wrap({})


# @router.get("/")
# async def get_wishlist(request: Request):
#     user_id = request.session.get("user_id")

#     if not user_id:
#         return ApiException(
#             401, 2500, "You must be logged in to see your wishlist."
#         )

#     wishlist = await Wishlists.filter(
#         user_id=user_id
#     ).prefetch_related("movie")

#     return wrap(wishlist)


# @router.get("/{movie_id}")
# async def is_movie_wishlist(request: Request, movie_id: str) -> bool:
#     user_id = request.session.get("user_id")

#     if not user_id:
#         return ApiException(
#             401, 2500, "You must be logged in to see your wishlist."
#         )
#     wishlist = await Wishlists.filter(
#         movie_id=movie_id, user_id=user_id
#     ).first()

#     return wrap(False) if wishlist is None else wrap(True)


# @router.put("/{movie_id}")
# async def add_to_wishlist(request: Request, movie_id: str):
#     user_id = request.session.get("user_id")

#     if not user_id:
#         return ApiException(
#             401, 2500, "You must be logged in to add to wishlist."
#         )

#     try:
#         await Wishlists(movie_id=movie_id, user_id=user_id).save()
#     except OperationalError:
#         return ApiException(
#             401, 2501, "You cannot do that."
#         )

#     return wrap({})


# @router.delete("/{movie_id}")
# async def delete_from_wishlist(request: Request, movie_id: str):
#     user_id = request.session.get("user_id")

#     if not user_id:
#         return ApiException(
#             401, 2500, "You must be logged in to add to wishlist."
#         )

#     try:
#         await Wishlists.filter(movie_id=movie_id, user_id=user_id).delete()
#         return wrap({})
#     except OperationalError:
#         return ApiException(
#             401, 2501, "You cannot do that."
#         )
