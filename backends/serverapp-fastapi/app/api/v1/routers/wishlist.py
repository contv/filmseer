from fastapi import APIRouter, Request

# from app.models.db.wishlists import Wishlists
from app.utils.wrapper import wrap

router = APIRouter()
override_prefix = None
override_prefix_all = None


@router.get("/{movie_id}")
async def is_movie_wishlist(request: Request, movie_id: str) -> bool:
    wishlist = True
    return wrap(False) if wishlist is None else wrap(True)


@router.put("/{movie_id}")
async def add_to_wishlist(request: Request, movie_id: str):

    return wrap({})


# @router.get("/{movie_id}")
# async def is_movie_wishlist(request: Request, movie_id: str) -> bool:
#     user_id = request.session.get("user_id")

#     if not user_id:
#         return ApiException(
#             401, 2100, "You must be logged in to see your wishlist."
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
#             401, 2100, "You must be logged in to add to wishlist."
#         )

#      await Wishlists(
#         movie_id=movie_id,
#         user_id=user_id
#     ).save()

#     return wrap({})
