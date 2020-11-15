import base64
from typing import Optional, Union

from fastapi import APIRouter, Request
from humps import camelize
from pydantic import BaseModel

from app.models.common import ListResponse
from app.models.db.banlists import Banlists
from app.models.db.reviews import Reviews
from app.models.db.users import Users
from app.models.db.wishlists import Wishlists
from app.utils.password import hash, verify
from app.utils.ratings import calc_average_rating
from app.utils.wrapper import ApiException, Wrapper, wrap

from .banlist import UserBanlistResponse
from .review import ListReviewResponse, ReviewResponse
from .wishlist import MovieWishlistResponse

router = APIRouter()
override_prefix = None
override_prefix_all = None


class Register(BaseModel):
    username: str
    password: str


class UpdateUser(BaseModel):
    username: Optional[str]
    current_password: Optional[str]
    new_password: Optional[str]
    description: Optional[str]
    image: Optional[bytes]

    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True


class UserProfileResponse(BaseModel):
    id: str
    username: str
    description: Optional[str]
    image: Optional[str]


@router.post("/", tags=["user"])
async def create_user(register: Register, request: Request) -> Wrapper[dict]:
    user = await Users.filter(username=register.username, delete_date=None).first()
    if user:
        raise ApiException(500, 2020, "This username already exists")
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
        raise ApiException(400, 2700, "Please limit the numer of items per page")
    if (per_page < 0) or (page < 0):
        raise ApiException(400, 2701, "Invalid page/per_page parameter")

    user = (
        await Users.filter(username=username, delete_date=None)
        .first()
        .values("user_id")
    )
    if not user:
        raise ApiException(404, 2003, "Invalid user name.")

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


@router.get("/{username}/wishlist")
async def get_user_wishlist(username: str):
    user = await Users.filter(username=username, delete_date=None).first()

    if not user:
        raise ApiException(404, 2021, "That user's profile was not found.")

    items = []
    for wishlist_item in await Wishlists.filter(
        user_id=user.user_id, delete_date=None
    ).prefetch_related("movie"):
        rating = await calc_average_rating(
            wishlist_item.movie.cumulative_rating,
            wishlist_item.movie.num_votes,
            user.user_id,
            wishlist_item.movie_id,
        )
        items.append(
            MovieWishlistResponse(
                wishlist_id=str(wishlist_item.wishlist_id),
                movie_id=str(wishlist_item.movie_id),
                title=wishlist_item.movie.title,
                image_url=wishlist_item.movie.image,
                release_year=wishlist_item.movie.release_date.year,
                cumulativeRating=rating["cumulative_rating"],
                num_votes=rating["num_votes"],
            )
        )

    return wrap({"items": items})


# WISHLIST RELATED END


# BANLIST RELATED START


@router.get(
    "/{username}/banlist", response_model=Wrapper[ListResponse[UserBanlistResponse]]
)
async def get_user_banlist(username: str):
    user = await Users.filter(username=username, delete_date=None).first()

    if not user:
        raise ApiException(404, 2031, "That user doesn't exist.")

    items = []
    for banlist_item in await Banlists.filter(user_id=user.user_id, delete_date=None):
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


# BANLIST RELATED END


@router.get(
    "/", tags=["User"], response_model=Union[Wrapper[UserProfileResponse], Wrapper]
)
async def get_current_user(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        raise ApiException(500, 2001, "You are not logged in!")

    user = await Users.get_or_none(user_id=user_id, delete_date=None)
    if not user:
        raise ApiException(500, 2021, "That user's profile was not found")

    response = UserProfileResponse(
        id=str(user.user_id),
        username=user.username,
        description=user.description,
        image=user.image if user.image else None,
    )

    return wrap(response)


@router.get(
    "/{username}",
    tags=["User"],
    response_model=Union[Wrapper[UserProfileResponse], Wrapper],
)
async def get_user_profile(username: str):
    user = await Users.get_or_none(username=username, delete_date=None)
    if not user:
        raise ApiException(500, 2021, "That user's profile was not found")

    response = UserProfileResponse(
        id=str(user.user_id),
        username=user.username,
        description=user.description,
        image=user.image if user.image else None,
    )

    return wrap(response)


@router.put("/", tags=["User"], response_model=Wrapper)
async def modify_user(request: Request, form: UpdateUser):
    user_id = request.session.get("user_id")
    if not user_id:
        raise ApiException(500, 2001, "You are not logged in!")
    user = await Users.get_or_none(user_id=user_id, delete_date=None)
    if not user:
        raise ApiException(500, 2021, "That user's profile was not found")

    if form.username:
        existing_username = await Users.get_or_none(username__iexact=form.username)
        if existing_username and str(existing_username.user_id) != str(user_id):
            raise ApiException(500, 2020, "This username already exists")
        user.username = form.username
        await user.save(update_fields=["username"])

    if form.new_password:
        if not verify(user.password_hash, form.current_password):
            raise ApiException(500, 2010, "Incorrect username or password")
        user.password_hash = hash(form.new_password)
        await user.save(update_fields=["password_hash"])

    if form.image:
        image_url = "storages/images/users/" + user_id + ".png"
        with open("../../" + image_url, "wb") as f:
            f.write(base64.decodebytes(form.image))
        user.image = image_url
        await user.save(update_fields=["image"])

    if form.description is not None:
        if len(form.description) > 140:
            raise ApiException(
                500, 2022, "Your description must be 140 characters or less."
            )
        else:
            if len(form.description) == 0:
                user.description = None
            else:
                user.description = form.description
            await user.save(update_fields=["description"])

    return wrap({})
