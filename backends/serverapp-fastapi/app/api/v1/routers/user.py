from fastapi import APIRouter, Request
from pydantic import BaseModel
from humps import camelize
from typing import Optional, List, Union

from app.models.db.users import Users
from app.models.db.wishlists import Wishlists
from app.models.db.reviews import Reviews
from app.utils.password import hash
from app.utils.ratings import calc_average_rating
from app.utils.wrapper import ApiException, Wrapper, wrap
from fastapi import APIRouter, Request
from pydantic import BaseModel

from .review import ListReviewResponse, ReviewResponse
from .wishlist import MovieWishlistResponse

router = APIRouter()
override_prefix = None
override_prefix_all = None


class Register(BaseModel):
    username: str
    password: str


class UserProfileResponse(BaseModel):
    id: str
    username: str
    description: Optional[str]
    image: Optional[bytes]


@router.post("/", tags=["user"])
async def create_user(register: Register, request: Request) -> Wrapper[dict]:
    user = await Users.filter(username=register.username, delete_date=None).first()
    if user:
        raise ApiException(500, 2021, "This username already exists")
    # TODO: Validation
    await Users(
        username=register.username, password_hash=hash(register.password)
    ).save()
    return wrap({})


# REVIEW RELATED START


@router.get(
    "/{username}/reviews", tags=["user"], response_model=Wrapper[ListReviewResponse]
)
async def get_reviews_user(username: str, page: int = 0, per_page: int = 0):
    if per_page >= 42:
        return ApiException(400, 2700, "Please limit the numer of items per page")
    if (per_page < 0) or (page < 0):
        return ApiException(400, 2701, "Invalid page/per_page parameter")

    user = (
        await Users.filter(username=username, delete_date=None)
        .first()
        .values("user_id")
    )
    if not user:
        return ApiException(404, 2003, "Invalid user name.")

    user_id = user[0]["user_id"]

    reviews = [
        ReviewResponse(
            review_id=str(r.review_id),
            user_id=str(r.user_id),
            username=r.user.username,
            movie_id=str(r.movie_id),
            movie_name=str(r.movie.title),
            create_date=str(r.create_date),
            description=r.description,
            contains_spoiler=r.contains_spoiler,
            rating=r.rating.rating,
            num_helpful=r.num_helpful,
            num_funny=r.num_funny,
            num_spoiler=r.num_spoiler,
            flagged_helpful=await r.helpful_votes.filter(
                user_id=user_id, delete_date=None
            ).count(),
            flagged_funny=await r.funny_votes.filter(
                user_id=user_id, delete_date=None
            ).count(),
            flagged_spoiler=await r.spoiler_votes.filter(
                user_id=user_id, delete_date=None
            ).count(),
        )
        for r in await Reviews.filter(user_id=user_id, delete_date=None)
        .order_by("-create_date")
        .offset((page - 1) * per_page)
        .limit(per_page)
        .prefetch_related(
            "rating", "helpful_votes", "funny_votes", "spoiler_votes", "movie", "user"
        )
    ]

    return wrap({"items": reviews})


# REVIEW RELATED END

# WISHLIST RELATED START

@router.get(
    "/{username}/wishlist"
)
async def get_user_wishlist(username: str):
    user = await Users.filter(username=username).first()

    if not user:
        return ApiException(
            404, 2031, "That user doesn't exist."
        )

    items = [
        MovieWishlistResponse(
            wishlist_id=str(wishlist_item.wishlist_id),
            movie_id=str(wishlist_item.movie_id),
            title=wishlist_item.movie.title,
            image_url=wishlist_item.movie.image,
            release_year=wishlist_item.movie.release_date.year,
            average_rating=calc_average_rating(
                wishlist_item.movie.cumulative_rating, wishlist_item.movie.num_votes
            )
        )
        for wishlist_item in await Wishlists.filter(
            user_id=user.user_id, delete_date=None
        ).prefetch_related("movie")
    ]

    return wrap({"items": items})

# WISHLIST RELATED END

@router.get(
    "/", tags=["User"], response_model=Union[Wrapper[UserProfileResponse], Wrapper]
)
async def get_current_user(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return wrap(error=ApiException(500, 2001, "You are not logged in!"))

    user = await Users.get_or_none(user_id=user_id, delete_date=None).prefetch_related(
        "profile_image_id"
    )
    if not user:
        return wrap(
            error=ApiException(500, 2200, "That user's profile page was not found")
        )

    response = UserProfileResponse(
        id=str(user.user_id),
        username=user.username,
        description=user.description,
        image=user.profile_image_id.content if user.profile_image_id else None,
    )

    return wrap(response)


@router.get(
    "/{username}",
    tags=["User"],
    response_model=Union[Wrapper[UserProfileResponse], Wrapper],
)
async def get_user_profile(username: str):
    user = await Users.get_or_none(
        username=username, delete_date=None
    )
    if not user:
        return wrap(
            error=ApiException(500, 2200, "That user's profile page was not found")
        )

    response = UserProfileResponse(
        id=str(user.user_id),
        username=user.username,
        description=user.description,
        image=user.profile_image_id.content if user.profile_image_id else None,
    )

    return wrap(response)
