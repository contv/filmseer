from fastapi import APIRouter
from pydantic import BaseModel

from app.models.db.movies import Movies
from app.utils.wrapper import ApiException, Wrapper, wrap

router = APIRouter()
override_prefix = None
override_prefix_all = None

@router.get("/{movie_id}", tags=["movie"])
async def get_movie(movie_id: str) -> Wrapper[dict]:
    movie = await Movies.filter(movie_id=movie_id).first()
    print(movie)
    return wrap(movie)