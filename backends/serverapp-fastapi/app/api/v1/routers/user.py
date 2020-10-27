from fastapi import APIRouter, Request
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
    create_date: str
    movie_id: str
    description: str
    contains_spoiler: bool
    rating: float
    num_helpful: int
    num_funny: int
    num_spoiler: int


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


@router.get("/{username}/reviews", tags=["user"])
async def get_reviews_user(username: str, request: Request):
    user = (
        await Users.filter(username=username, delete_date=None)
        .first()
        .values("user_id")
    )
    if not user:
        return ApiException(404, 2003, "Invalid user name.")

    user_id = user[0]["user_id"]
    r = [
        await Reviews.filter(user_id=user_id).prefetch_related("rating")
    ]

    return wrap({"items": r})


# REVIEW RELATED END


@router.get("/{username}/wishlist")
async def get_user_wishlist(username: str):
    return wrap({"items": []})
