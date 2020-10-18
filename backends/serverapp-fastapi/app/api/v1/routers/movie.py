from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from app.models.db.movies import Movies
from app.utils.wrapper import ApiException, Wrapper, wrap

router = APIRouter()
override_prefix = None
override_prefix_all = None


class MovieDetail(BaseModel):
    id: str
    title: str
    release_date: str
    release_year: str
    image_url: Optional[str]
    description: str
    trailer: Optional[str]
    num_reviews: int
    num_votes: int
    cumulative_rating: int


@router.get("/{movie_id}", tags=["movies"])
async def get_movie(movie_id: str) -> Wrapper[BaseModel]:
    movie = await Movies.filter(movie_id=movie_id).first()

    if movie is None:
        return ApiException(404, 2100, "That movie doesn't exist")

    movie_detail = MovieDetail(
        id=str(movie.movie_id),
        title=movie.title,
        release_date=str(movie.release_date),
        release_year=str(movie.release_date.year),
        description=movie.description,
        image_url=movie.image,
        trailer=movie.trailer,
        num_reviews=movie.num_reviews,
        num_votes=movie.num_votes,
        cumulative_rating=movie.cumulative_rating,
    )

    return wrap(movie_detail)
