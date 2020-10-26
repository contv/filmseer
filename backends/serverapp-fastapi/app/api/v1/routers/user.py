from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.models.db.users import Users
from app.models.db.wishlists import Wishlists
from app.utils.password import hash
from app.utils.wrapper import ApiException, Wrapper, wrap

router = APIRouter()
override_prefix = None
override_prefix_all = None


class Register(BaseModel):
    username: str
    password: str


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

@router.get("/{username}/wishlist")
async def get_user_wishlist(username: str):
    return wrap([])

# @router.get("/{username}/wishlist")
# async def get_user_wishlist(username: str):
#     user = await Users.filter(username=username).first()

#     if not user:
#         return ApiException(
#             404, 2031, "That user doesn't exist."
#         )

#     wishlist = await Wishlists.filter(
#         user_id=user.user_id
#     ).prefetch_related("movie")

#     return wrap(wishlist)
