from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
import re

from app.models.db.movies import Movies
from app.models.db.positions import Positions
from app.utils.wrapper import ApiException, Wrapper, wrap

router = APIRouter()
override_prefix = None
override_prefix_all = None


class MovieResponse(BaseModel):
    id: str
    title: str
    release_date: str
    release_year: str
    image_url: Optional[str]
    description: Optional[str]
    trailers: List[dict]
    num_reviews: int
    num_votes: int
    cumulative_rating: int
    crew: List[dict]


@router.get(
    "/{movie_id}", tags=["movies"], response_model=Wrapper[MovieResponse]
)
async def get_movie(movie_id: str):
    movie = await Movies.filter(movie_id=movie_id).first()

    if movie is None:
        return ApiException(404, 2100, "That movie doesn't exist")

    trailers = []
    trailer_re = r"key:(.+), *site:(.+)}"

    if movie.trailer is not None:
        # extracts key and site values from trailer entries
        # in form "{key:k1,site:s1},{key:k2,site:s2}..."
        trailers_split = movie.trailer.split(",{")
        for t in trailers_split:
            m = re.search(trailer_re, t)
            key = str(m.group(1))
            site = str(m.group(2))
            trailer = dict({"key": key, "site": site})
            trailers.append(trailer)

    crew = []
    movie_crew = await Positions.filter(
        movie_id=movie_id).prefetch_related("person")

    for p in movie_crew:
        crew.append(
            {
                "id": p.person_id,
                "name": p.person.name,
                "position": p.position,
                "image": p.person.image,
            }
        )

    movie_detail = {
        "id": str(movie.movie_id),
        "title": movie.title,
        "release_date": str(movie.release_date),
        "release_year": str(movie.release_date.year),
        "description": movie.description,
        "image_url": movie.image,
        "trailers": trailers,
        "num_reviews": movie.num_reviews,
        "num_votes": movie.num_votes,
        "cumulative_rating": movie.cumulative_rating,
        "crew": crew,
    }

    return wrap(movie_detail)
