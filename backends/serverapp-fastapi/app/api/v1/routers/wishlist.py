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

"""
This API controller handles all wishlist related data and wishlist
management.
"""

# a brief summary of a movie as seen in a wishlist
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

# gets all movies on your wishlist
@router.get(
    "/", tags=["wishlist"], response_model=Wrapper[ListResponse[MovieWishlistResponse]]
)
async def get_wishlist(request: Request):
    user_id = request.session.get("user_id")

    if not user_id:
        raise ApiException(401, 2001, "You are not logged in!")

    
    items = []
    for wishlist_item in await Wishlists.filter(
        user_id=user_id, delete_date=None
    ).prefetch_related("movie"):
        # gets the banlist-adjusted ratings before creating
        # the wishlist response object
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

# checks whether that movie is already on your wishlist
@router.get("/{movie_id}", response_model=Wrapper[MovieInWishlistResponse])
async def is_movie_wishlist(request: Request, movie_id: str):
    user_id = request.session.get("user_id")

    if not user_id:
        raise ApiException(401, 2001, "You are not logged in!")
    added = (
        await Wishlists.filter(
            movie_id=movie_id, user_id=user_id, delete_date=None
        ).first()
        is not None
    )

    return wrap({"added": added})

# adds a movie to wishlist
@router.put("/{movie_id}")
async def add_to_wishlist(request: Request, movie_id: str):
    user_id = request.session.get("user_id")

    if not user_id:
        raise ApiException(401, 2001, "You are not logged in!")
    
    # if it was previously wishlisted (including soft deletion),
    # idempotently add to wishlist.

    previously_wishlisted = await Wishlists.get_or_none(
        movie_id=movie_id, user_id=user_id
    )

    if previously_wishlisted is not None:
        try:
            previously_wishlisted.delete_date = None
            await previously_wishlisted.save()
        except OperationalError:
            raise ApiException(401, 2030, "You cannot add that wishlist item.")
    else:
        try:
            await Wishlists(movie_id=movie_id, user_id=user_id).save()
        except OperationalError:
            raise ApiException(500, 2030, "You cannot add that wishlist item.")

    return wrap({})

# deletes a movie from wishlist
@router.delete("/{movie_id}")
async def delete_from_wishlist(request: Request, movie_id: str):
    user_id = request.session.get("user_id")

    if not user_id:
        raise ApiException(401, 2001, "You are not logged in!")
    
    # if previously wishlisted, delete it
    previously_wishlisted = await Wishlists.get_or_none(
        movie_id=movie_id, user_id=user_id
    )

    if previously_wishlisted is not None:
        try:
            previously_wishlisted.delete_date = datetime.now()
            await previously_wishlisted.save()
        except OperationalError:
            raise ApiException(500, 2031, "You cannot delete that wishlist item.")
    else:
        raise ApiException(500, 2031, "You cannot delete that wishlist item.")

    return wrap({})
