from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request
from humps import camelize
from pydantic import BaseModel
from tortoise.exceptions import OperationalError

from app.models.common import ListResponse
from app.models.db.wishlists import Wishlists
from app.utils.ratings import calc_average_rating
from app.utils.wrapper import ApiException, Wrapper, wrap

router = APIRouter()
override_prefix = None
override_prefix_all = None


class MovieWishlistResponse(BaseModel):
    wishlist_id: str
    movie_id: str
    title: str
    release_year: str
    image_url: Optional[str]
    cumulative_rating: float
    num_votes: int

    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True


class MovieInWishlistResponse(BaseModel):
    added: bool


@router.get(
    "/", tags=["wishlist"], response_model=Wrapper[ListResponse[MovieWishlistResponse]]
)
async def get_wishlist(request: Request):
    user_id = request.session.get("user_id")

    if not user_id:
        return ApiException(401, 2500, "You must be logged in to see your wishlist.")

    items = []
    for wishlist_item in await Wishlists.filter(
        user_id=user_id, delete_date=None
    ).prefetch_related("movie"):

        rating = await calc_average_rating(
            wishlist_item.movie.cumulative_rating,
            wishlist_item.movie.num_votes,
            user_id,
            wishlist_item.movie_id,
        )
        items.append(
            MovieWishlistResponse(
                wishlist_id=str(wishlist_item.wishlist_id),
                movie_id=str(wishlist_item.movie_id),
                title=wishlist_item.movie.title,
                image_url=wishlist_item.movie.image,
                release_year=wishlist_item.movie.release_date.year,
                cumulative_rating=rating["cumulative_rating"],
                num_votes=rating["num_votes"],
            )
        )

    return wrap({"items": items})


@router.get("/{movie_id}", response_model=Wrapper[MovieInWishlistResponse])
async def is_movie_wishlist(request: Request, movie_id: str):
    user_id = request.session.get("user_id")

    if not user_id:
        return ApiException(401, 2500, "You must be logged in to see your wishlist.")
    added = (
        await Wishlists.filter(
            movie_id=movie_id, user_id=user_id, delete_date=None
        ).first()
        is not None
    )

    return wrap({"added": added})


@router.put("/{movie_id}")
async def add_to_wishlist(request: Request, movie_id: str):
    user_id = request.session.get("user_id")

    if not user_id:
        return ApiException(401, 2500, "You must be logged in to add to wishlist.")

    previously_wishlisted = await Wishlists.get_or_none(
        movie_id=movie_id, user_id=user_id
    )

    if previously_wishlisted is not None:
        try:
            previously_wishlisted.delete_date = None
            await previously_wishlisted.save()
        except OperationalError:
            return ApiException(401, 2501, "You cannot do that.")
    else:
        try:
            await Wishlists(movie_id=movie_id, user_id=user_id).save()
        except OperationalError:
            return ApiException(401, 2501, "You cannot do that.")

    return wrap({})


@router.delete("/{movie_id}")
async def delete_from_wishlist(request: Request, movie_id: str):
    user_id = request.session.get("user_id")

    if not user_id:
        return ApiException(401, 2500, "You must be logged in to add to wishlist.")
    previously_wishlisted = await Wishlists.get_or_none(
        movie_id=movie_id, user_id=user_id
    )

    if previously_wishlisted is not None:
        try:
            previously_wishlisted.delete_date = datetime.now()
            await previously_wishlisted.save()
        except OperationalError:
            return ApiException(401, 2501, "You cannot do that.")
    else:
        return ApiException(401, 2501, "You haven't wishlisted this movie yet.")

    return wrap({})
