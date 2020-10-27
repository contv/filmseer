from fastapi import APIRouter, Request
from typing import List
from pydantic import BaseModel

from app.models.db.users import Users
from app.models.db.reviews import Reviews
from app.utils.password import hash
from app.utils.wrapper import ApiException, Wrapper, wrap

router = APIRouter()
override_prefix = None
override_prefix_all = None


class Register(BaseModel):
    username: str
    password: str


class ReviewResponse(BaseModel):
    review_id: str
    movie_id: str
    create_date: str
    description: str
    contains_spoiler: bool
    rating: float
    num_helpful: int
    num_funny: int
    num_spoiler: int
    flagged_helpful: bool
    flagged_funny: bool
    flagged_spoiler: bool


class ListReviewResponse(BaseModel):
    items: List[ReviewResponse]


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
async def get_reviews_user(username: str):
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
            movie_id=str(r.movie_id),
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
        for r in await Reviews.filter(
            user_id=user_id, delete_date=None
        ).prefetch_related("rating", "helpful_votes", "funny_votes", "spoiler_votes")
    ]

    return wrap({"items": reviews})


# REVIEW RELATED END


@router.get("/{username}/wishlist")
async def get_user_wishlist(username: str):
    return wrap({"items": []})
