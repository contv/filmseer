from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.models.db.users import User
from app.utils.password import hash, is_hash_deprecated, verify
from app.utils.wrapper import ApiException, Wrapper, wrap

router = APIRouter()
override_prefix = None
override_prefix_all = None


class Login(BaseModel):
    username: str
    password: str


@router.get("/", tags=["session"])
async def check_session(request: Request) -> Wrapper[dict]:
    username = request.session.get("username")
    userid = request.session.get("userid")
    if username:
        if await User.filter(username=username, userid=userid).exists():
            return wrap({})
        else:
            del request.session["username"]
            del request.session["userid"]
            raise ApiException(500, 2002, "This user no longer exist!")
    raise ApiException(500, 2001, "You are not logged in!")


@router.post("/", tags=["session"])
async def create_session(login: Login, request: Request) -> Wrapper[dict]:
    if "username" in request.session:
        del request.session["username"]
    if "userid" in request.session:
        del request.session["userid"]
    user = await User.filter(username=login.username).first()
    if not user:
        raise ApiException(500, 2010, "Incorrect username or password")
    if verify(user.password_hash, login.password):
        if is_hash_deprecated(user.password_hash):
            user.password_hash = hash(login.password)
            await user.save()
        request.session["username"] = str(user.username)
        request.session["userid"] = str(user.userid)
        return wrap({})
    raise ApiException(500, 2010, "Incorrect username or password")


@router.delete("/", tags=["session"])
async def delete_session(request: Request) -> Wrapper[dict]:
    if "username" in request.session:
        del request.session["username"]
    if "userid" in request.session:
        del request.session["userid"]
    return wrap({})
