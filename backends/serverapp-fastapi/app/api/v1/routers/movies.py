from datetime import datetime
from random import choices
from typing import Dict, List, Optional

from dateutil.relativedelta import relativedelta
from elasticsearch import RequestsHttpConnection, Urllib3HttpConnection
from elasticsearch_dsl import Q, Search, connections

from app.core.config import settings
from app.models.db.movies import Movies
from app.models.db.ratings import Ratings
from app.utils.dict_storage.redis import RedisDictStorageDriver
from app.utils.ratings import calc_average_rating
from app.utils.recommender import load_movie_set, predict_on_movie, predict_on_user
from app.utils.wrapper import ApiException, Wrapper, wrap
from fastapi import APIRouter, Query, Request
from humps import camelize
from pydantic import BaseModel
from tortoise.exceptions import OperationalError
from tortoise.functions import Count
from tortoise.transactions import in_transaction

from .movie import process_movie_payload

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


async def get_movies(
    request: Request,
    movies: List[str],
    genres: Optional[List[str]] = Query([]),
    years: Optional[List[str]] = Query([]),
    directors: Optional[List[str]] = Query([]),
    per_page: Optional[int] = None,
    page: Optional[int] = 1,
    sort: Optional[str] = ("relevance", "rating", "name", "year")[0],
    desc: Optional[bool] = True,
):
    conn = connections.create_connection(
        hosts=settings.ELASTICSEARCH_URI,
        alias=settings.ELASTICSEARCH_ALIAS,
        connection_class=RequestsHttpConnection
        if settings.ELASTICSEARCH_TRANSPORTCLASS == "RequestsHttpConnection"
        else Urllib3HttpConnection,
        timeout=settings.ELASTICSEARCH_TIMEOUT,
        use_ssl=settings.ELASTICSEARCH_USESSL,
        verify_certs=settings.ELASTICSEARCH_VERIFYCERTS,
        ssl_show_warn=settings.ELASTICSEARCH_SHOWSSLWARNINGS,
        opaque_id=request.session.get("user_id")
        or str(request.client.host) + ":" + str(request.client.port)
        or None
        if settings.ELASTICSEARCH_TRACEREQUESTS
        else None,
    )

    queries = [
        Q(
            "bool",
            should=[Q("match", movie_id=movie_id) for movie_id in movies],
            minimum_should_match=1,
        )
    ]

    search = Search(using=conn, index=settings.ELASTICSEARCH_MOVIEINDEX)

    for q in queries:
        search = search.query(q)

    # TODO Retrieve banlist and pass into script field
    # eg "listban":"{uuid1},{uuid2}"
    search = search.script_fields(
        average_rating={
            "script": {"id": "calculate_rating_field", "params": {"listban": ""}}
        }
    )

    # Execute search
    search = search.source(
        ["movie_id", "image", "title", "genres", "release_date", "positions"]
    )
    response = search.execute()

    preprocessed = {
        hit.meta.id: {"score": hit.meta.score, "movie": hit.to_dict()}
        for hit in response
    }
    postprocessed = await process_movie_payload(
        preprocessed, years, directors, genres, per_page, page, sort, desc
    )
    return postprocessed


@router.get("/recommendation", tags=["Movies"])
async def get_recommendation(
    request: Request,
    type: str,
    size: Optional[int] = 20,
    movie_id: Optional[str] = None,
    recency: Optional[int] = 7,
    genres: Optional[List[str]] = Query([]),
    years: Optional[List[str]] = Query([]),
    directors: Optional[List[str]] = Query([]),
    per_page: Optional[int] = None,
    page: Optional[int] = 1,
    sort: Optional[str] = ("relevance", "rating", "name", "year")[0],
    desc: Optional[bool] = True,
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
        # check if this movie has been searched already
        searches = request.session["recommendations"]

        driver = RedisDictStorageDriver(
            key_prefix="recommendations:",
            key_filter=r"[^a-zA-Z0-9_-]+",
            ttl=settings.REDIS_SEARCH_TTL,
            renew_on_ttl=settings.REDIS_SEARCH_TTL,
            redis_uri=settings.REDIS_URI,
            redis_pool_min=settings.REDIS_POOL_MIN,
            redis_pool_max=settings.REDIS_POOL_MAX,
        )
        await driver.initialize_driver()

        try:
            search_id = searches[movie_id]
        except KeyError:
            search_id = await driver.create()
            if len(searches.keys()) >= settings.REDIS_SEARCHES_MAX:
                searches.pop(list(searches)[0])
            searches[movie_id] = search_id

        # Attempt to retrieve stored movie payload from Redis
        movies, _ = await driver.get(search_id)
        if movies:
            movies = movies["movies"]

        if not movies:
            try:
                movies = await predict_on_movie(movie_id, size)
                await driver.update(search_id, {"movies": movies})
                await driver.terminate_driver()
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

    # Postprocess to apply filters, sorting and pagination
    postprocessed = await get_movies(
        request, movies, genres, years, directors, per_page, page, sort, desc
    )

    return wrap(postprocessed)
