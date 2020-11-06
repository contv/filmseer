from datetime import datetime
from random import choices
from typing import Dict, List, Optional

from dateutil.relativedelta import relativedelta

from app.core.config import settings
from app.models.db.movies import Movies
from app.models.db.ratings import Ratings
from app.utils.ratings import calc_average_rating
from app.utils.recommender import load_movie_set, predict_on_movie, predict_on_user
from app.utils.wrapper import ApiException, Wrapper, wrap
from fastapi import APIRouter, Query, Request
from humps import camelize
from pydantic import BaseModel
from tortoise.exceptions import OperationalError
from tortoise.functions import Count
from tortoise.transactions import in_transaction

router = APIRouter()
override_prefix = None
override_prefix_all = None


class RecommendationResponse(BaseModel):
    id: str
    title: str
    release_year: str
    genres: Optional[List[str]]
    image_url: Optional[str]
    average_rating: float

    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True


async def get_movie(movie_id: str):
    try:
        movie = await Movies.filter(movie_id=movie_id, delete_date=None).first()
    except OperationalError:
        raise ApiException(401, 2501, "You cannot do that.")

    if movie is None:
        raise ApiException(404, 2100, "That movie doesn't exist")

    genres = [genre.name for genre in await movie.genres]

    # TODO remove ratings from blocked users
    average_rating = calc_average_rating(movie.cumulative_rating, movie.num_votes)

    recommendation = RecommendationResponse(
        id=str(movie.movie_id),
        title=movie.title,
        release_year=str(movie.release_date.year),
        genres=genres,
        image_url=movie.image,
        average_rating=average_rating,
    )

    return recommendation


@router.get("/recommendation", tags=["Movies"])
async def get_recommendation(
    request: Request,
    type: str,
    size: Optional[int] = 20,
    movie_id: Optional[str] = None,
    recency: Optional[int] = 7,
):

    # Confine parameters to prevent excessive computation
    if recency < 0:
        recency = 0
    elif recency > 30:
        recency = 30

    if size <= 0:
        size = 1
    elif size > 50:
        size = 50

    if type == "foryou":
        user_id = request.session.get("user_id")
        if not user_id:
            return ApiException(500, 2001, "You are not logged in!")
        # Grab seen movies
        movies_seen = set(
            str(item[0])
            for item in await Ratings.filter(
                user_id=user_id, delete_date=None
            ).values_list("movie_id")
        )
        # Calculate unseen movies
        movie_set = await load_movie_set()
        unseen = movie_set.difference(movies_seen)
        # Get a random subset for variety
        unseen = choices(tuple(unseen), k=settings.RECOMMENDER_RANDOM_SAMPLESIZE)
        try:
            movies = await predict_on_user(user_id, unseen, size)
        except TypeError:
            return ApiException(404, 3000, "Recommendation not available")

    if type == "detail":
        if not movie_id:
            return ApiException(404, 3002, "You must provide a valid movie")
        try:
            movies = await predict_on_movie(movie_id, size)
        except ValueError:
            return ApiException(404, 3001, "Movie has not been rated before")
        except TypeError:
            return ApiException(404, 3000, "Recommendation not available")

    if type == "popular":
        cutoff_date = datetime.now() - relativedelta(days=recency)
        movies = (
            await Ratings.filter(create_date__gte=cutoff_date, delete_date=None)
            .annotate(movie_id_count=Count("movie_id"))
            .group_by("movie_id")
            .order_by("-movie_id_count")
            .limit(size)
            .values_list("movie_id", "movie_id_count")
        )
        movies = [movie[0] for movie in movies]

    if type == "new":
        cutoff_date = datetime.now() - relativedelta(days=recency)
        movies = (
            await Movies.filter(
                release_date__gte=cutoff_date,
                release_date__lte=datetime.now(),
                delete_date=None,
            )
            .order_by("-release_date")
            .limit(size)
            .values_list("movie_id")
        )
        movies = [movie[0] for movie in movies]

    movies = [await get_movie(movie) for movie in movies]
    return wrap(movies)
