from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.models.db.users import Users
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
    user = await Users.filter(username=register.username).first()
    if user:
        raise ApiException(500, 2021, "This username already exists")
    # TODO: Validation
    await Users(username=register.username, password_hash=hash(register.password)).save()
    return wrap({})


@router.get("/{username}/wishlist")
async def get_user_wishlist(username: str):
    return wrap([])
