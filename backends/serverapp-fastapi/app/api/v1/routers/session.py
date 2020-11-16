from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.models.db.users import Users
from app.utils.password import hash, is_hash_deprecated, verify
from app.utils.wrapper import ApiException, Wrapper, wrap

router = APIRouter()
override_prefix = None
override_prefix_all = None

"""
This API controller handles session related data, such as login, logout, 
and current session.
"""

class Login(BaseModel):
    username: str
    password: str

# this returns 200 if you have a session i.e. you're logged in
@router.get("/", tags=["session"])
async def check_session(request: Request) -> Wrapper[dict]:
    username = request.session.get("username")
    user_id = request.session.get("user_id")
    if username:
        if await Users.filter(
            username=username, user_id=user_id, delete_date=None
        ).exists():
            return wrap({})
        else:
            del request.session["username"]
            del request.session["user_id"]
            raise ApiException(500, 2002, "This user no longer exists!")
    raise ApiException(500, 2001, "You are not logged in!")

# login
@router.post("/", tags=["session"])
async def create_session(login: Login, request: Request) -> Wrapper[dict]:
    if "username" in request.session:
        del request.session["username"]
    if "user_id" in request.session:
        del request.session["user_id"]
    user = await Users.filter(username=login.username, delete_date=None).first()
    if not user:
        raise ApiException(500, 2010, "Incorrect username or password")
    # when a user logs in adds user session keys for caching in Redis
    if verify(user.password_hash, login.password):
        if is_hash_deprecated(user.password_hash):
            user.password_hash = hash(login.password)
            await user.save()
        request.session["username"] = str(user.username)
        request.session["user_id"] = str(user.user_id)
        request.session["searches"] = {}
        request.session["title_searches"] = {}
        request.session["description_searches"] = {}
        request.session["genres_searches"] = {}
        request.session["people_searches"] = {}
        request.session["recommendations"] = {}
        return wrap({})
    raise ApiException(500, 2010, "Incorrect username or password")

# logout, clears session data
@router.delete("/", tags=["session"])
async def delete_session(request: Request) -> Wrapper[dict]:
    if "username" in request.session:
        del request.session["username"]
    if "user_id" in request.session:
        del request.session["user_id"]
    return wrap({})
