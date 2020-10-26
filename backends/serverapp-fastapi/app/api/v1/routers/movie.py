from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from tortoise.exceptions import OperationalError
from humps import camelize

from app.models.db.movies import Movies
from app.models.db.positions import Positions
from app.utils.wrapper import ApiException, Wrapper, wrap

router = APIRouter()
override_prefix = None
override_prefix_all = None


class Trailer(BaseModel):
    key: str
    site: str


class CrewMember(BaseModel):
    id: str
    name: str
    position: str
    image: Optional[str]


class MovieResponse(BaseModel):
    id: str
    title: str
    release_date: str
    release_year: str
    image_url: Optional[str]
    description: Optional[str]
    trailers: List[Trailer]
    num_reviews: int
    num_votes: int
    average_rating: float
    crew: List[CrewMember]

    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True


def calc_average_rating(cumulative_rating, num_votes) -> float:
    return round(cumulative_rating / num_votes if num_votes > 0 else 0.0, 1)


@router.get("/{movie_id}/ratings")
async def get_average_rating(movie_id: str) -> Wrapper[dict]:
    try:
        movie = await Movies.filter(
            movie_id=movie_id, delete_date=None
        ).first()
    except OperationalError:
        return ApiException(
            401, 2501, "You cannot do that."
        )

    if movie is None:
        return ApiException(404, 2100, "That movie doesn't exist")

    # TODO remove ratings from blocked users
    return wrap({"average": calc_average_rating(
        movie.cumulative_rating, movie.num_votes
    )})


@router.get(
    "/{movie_id}", tags=["movies"], response_model=Wrapper[MovieResponse]
)
async def get_movie(movie_id: str):
    try:
        movie = await Movies.filter(
            movie_id=movie_id, delete_date=None
        ).first()
    except OperationalError:
        return ApiException(
            401, 2501, "You cannot do that."
        )

    if movie is None:
        raise ApiException(404, 2100, "That movie doesn't exist")

    crew = [
        CrewMember(
            id=str(p.person_id),
            name=p.person.name,
            position=p.position,
            image=p.person.image,
        )
        for p in await Positions.filter(
            movie_id=movie_id
        ).prefetch_related("person")
    ]

    # TODO remove ratings from blocked users
    average_rating = calc_average_rating(
        movie.cumulative_rating, movie.num_votes
    )

    movie_detail = MovieResponse(
        id=str(movie.movie_id),
        title=movie.title,
        release_date=str(movie.release_date),
        release_year=str(movie.release_date.year),
        description=movie.description,
        image_url=movie.image,
        trailers=movie.trailer,
        num_reviews=movie.num_reviews,
        num_votes=movie.num_votes,
        average_rating=average_rating,
        crew=crew,
    )

    return wrap(movie_detail)