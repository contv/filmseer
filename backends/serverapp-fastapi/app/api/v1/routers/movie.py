import re
from datetime import datetime
from typing import List, Optional, Dict
import asyncio
import aioredis
import json

from elasticsearch import Elasticsearch, RequestsHttpConnection, Urllib3HttpConnection
from elasticsearch_dsl import Q, Search, connections

from app.core.config import settings
from app.models.db.movies import Movies
from app.models.db.positions import Positions
from app.models.db.ratings import Ratings
from app.models.db.reviews import Reviews
from app.models.db.users import Users
from app.utils.wrapper import ApiException, Wrapper, wrap
from fastapi import APIRouter, Query, Request
from humps import camelize
from pydantic import BaseModel
from tortoise.exceptions import IntegrityError, OperationalError
from tortoise.transactions import in_transaction

from app.utils.unique_id import id, to_uuid
from app.utils.dict_storage.redis import RedisDictStorageDriver


def _new_uuid():
    return to_uuid(id())


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
    trailers: Optional[List[Trailer]]
    genres: List[str]
    num_reviews: int
    num_votes: int
    average_rating: float
    crew: List[CrewMember]

    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True


class SearchResponse(BaseModel):
    id: str
    title: str
    release_year: str
    genres: Optional[List[str]]
    image_url: Optional[str]
    average_rating: float
    score: float

    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True


class RatingResponse(BaseModel):
    id: str
    rating: float


def calc_average_rating(cumulative_rating, num_votes) -> float:
    return round(cumulative_rating / num_votes if num_votes > 0 else 0.0, 1)


@router.get("/{movie_id}/ratings")
async def get_average_rating(movie_id: str) -> Wrapper[dict]:
    try:
        movie = (
            await Movies.filter(movie_id=movie_id, delete_date=None)
            .prefetch_related("genres")
            .first()
        )
    except OperationalError:
        return ApiException(401, 2501, "You cannot do that.")

    if movie is None:
        return ApiException(404, 2100, "That movie doesn't exist")

    # TODO remove ratings from blocked users
    return wrap(
        {"average": calc_average_rating(movie.cumulative_rating, movie.num_votes)}
    )


@router.get("/{movie_id}", tags=["movies"], response_model=Wrapper[MovieResponse])
async def get_movie(movie_id: str):
    try:
        movie = await Movies.filter(movie_id=movie_id, delete_date=None).first()
    except OperationalError:
        return ApiException(401, 2501, "You cannot do that.")

    if movie is None:
        raise ApiException(404, 2100, "That movie doesn't exist")

    genres = [genre.name for genre in await movie.genres]
    crew = [
        CrewMember(
            id=str(p.person_id),
            name=p.person.name,
            position=p.position,
            image=p.person.image,
        )
        for p in await Positions.filter(movie_id=movie_id).prefetch_related("person")
    ]

    # TODO remove ratings from blocked users
    average_rating = calc_average_rating(movie.cumulative_rating, movie.num_votes)

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
        genres=genres,
        crew=crew,
    )

    return wrap(movie_detail)


@router.get("/{movie_id}/reviews", tags=["movies"])
async def get_movie_reviews(movie_id: str):
    return wrap({})


@router.post("/{movie_id}/review", tags=["movies"])
async def create_user_review(movie_id: str, request: Request):
    return wrap({})


@router.put("/{movie_id}/review", tags=["movies"])
async def update_user_review(movie_id: str, request: Request):
    return wrap({})


@router.delete("/{movie_id}/review", tags=["movies"])
async def delete_user_review(movie_id: str, request: Request):
    return wrap({})


## REVIEW RELATED END


@router.get("/", tags=["movies"], response_model=Wrapper[List[SearchResponse]])
async def search_movies(
    request: Request,
    keywords: str = "",
    genres: Optional[List[str]] = Query([]),
    years: Optional[List[str]] = Query([]),
    directors: Optional[List[str]] = Query([]),
    per_page: Optional[int] = None,
    page: Optional[int] = 1,
    sort: Optional[str] = ("relevance", "rating", "name", "year")[0],
    desc: Optional[bool] = True,
):
    # Initialise driver
    driver = RedisDictStorageDriver(
        key_prefix="search:",
        key_filter=r"[^a-zA-Z0-9_-]+",
        ttl=settings.REDIS_SEARCH_TTL,
        renew_on_ttl=settings.REDIS_SEARCH_TTL,
        redis_uri=settings.REDIS_URI,
        redis_pool_min=settings.REDIS_POOL_MIN,
        redis_pool_max=settings.REDIS_POOL_MAX,
    )
    await driver.initialize_driver()

    # Lookup existing search in session
    searches = request.session["searches"]
    try:
        search_id = searches[keywords]
    except KeyError:
        search_id = await driver.create()
        if len(searches.keys()) >= settings.REDIS_SEARCHES_MAX:
            searches.pop(list(searches)[0])
        searches[keywords] = search_id

    # Attempt to retrieve stored movie payload from Redis
    payload, _ = await driver.get(search_id)
    if payload:
        print("PAYLOAD FOUND")
        await driver.terminate_driver()
        return wrap(
            await process_movie_payload(
                payload, years, directors, genres, per_page, page, sort, desc
            )
        )

    print("PAYLOAD NOT FOUND")
    # Otherwise perform new Elasticsearch query
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

    # Build query context for scoring results
    years_in_keywords = re.findall("(\d{4})", keywords)
    queries = [
        Q(
            "bool",
            must=[
                Q(
                    "multi_match",
                    query=keywords,
                    fields=[
                        "title^10",
                        "description",
                        "genres.name",
                        "positions.people",
                        "positions.char_name",
                    ],
                )
            ],
            should=[
                Q(
                    {
                        "bool": {
                            "should": [
                                {
                                    "range": {
                                        "release_date": {
                                            "gte": year + "||/y",
                                            "lte": year + "||/y",
                                            "format": "yyyy",
                                        }
                                    }
                                },
                            ],
                        },
                    }
                )
                for year in years_in_keywords
            ],
        )
    ]

    search = Search(using=conn, index=settings.ELASTICSEARCH_MOVIEINDEX).extra(
        size=settings.ELASTICSEARCH_RESPONSESIZE
    )

    for q in queries:
        search = search.query(q)

    # TODO Retrieve banlist and pass into script field
    # eg "listban":"1ebde7ba-9ef8-411f-bdc1-2d1c083e778b,1ebde7ba-9ef8-411f-bdc1-2d1c083e778b"
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

    print(f"FOUND {len(response.hits)} hits")

    # Convert response into dict for Redis storage
    preprocessed = {
        hit.meta.id: {"score": hit.meta.score, "movie": hit.to_dict()}
        for hit in response
    }

    # Save response in Redis
    await driver.update(search_id, preprocessed)
    await driver.terminate_driver()

    return wrap(
        await process_movie_payload(
            preprocessed, years, directors, genres, per_page, page, sort, desc
        )
    )


async def process_movie_payload(
    preprocessed: Dict,
    year_filter: Optional[List[str]],
    director_filter: Optional[List[str]],
    genre_filter: Optional[List[str]],
    per_page: Optional[int],
    page: Optional[int],
    sort: Optional[str],
    desc: Optional[bool],
) -> List[SearchResponse]:
    """
    Given a preprocessed Elasticsearch response payload, apply filters, sorting and pagination, and
    returns an ordered array of SearchResponse objects each representing a movie tile
    """
    # Filter
    postprocessed = []
    for movie_id in preprocessed:
        genre_filter_pass, year_filter_pass, director_filter_pass = True, True, True
        movie = preprocessed[movie_id]["movie"]
        if genre_filter:
            genres = set(genre["name"] for genre in movie["genres"])
            if not genres.intersection(genre_filter):
                genre_filter_pass = False
        if year_filter:
            year = movie["release_date"][0:4]
            if not year in year_filter:
                year_filter_pass = False
        if director_filter:
            directors = set(
                position["people"]["name"]
                for position in movie["positions"]
                if position["position"] == "director"
            )
            if not directors.intersection(director_filter):
                director_filter_pass = False
        if genre_filter_pass and year_filter_pass and director_filter_pass:
            postprocessed.append(preprocessed[movie_id])

    # Sort
    if sort == "relevance":
        postprocessed = sorted(postprocessed, key=lambda x: x["movie"]["title"])
        postprocessed = sorted(postprocessed, key=lambda x: x["score"], reverse=desc)
    elif sort == "rating":
        postprocessed = sorted(postprocessed, key=lambda x: x["movie"]["title"])
        postprocessed = sorted(
            postprocessed, key=lambda x: x["movie"]["average_rating"], reverse=desc
        )
    elif sort == "name":
        postprocessed = sorted(
            postprocessed, key=lambda x: x["movie"]["title"], reverse=not desc
        )
    elif sort == "year":
        postprocessed = sorted(
            postprocessed, key=lambda x: x["movie"]["average_rating"], reverse=True
        )
        postprocessed = sorted(
            postprocessed, key=lambda x: x["movie"]["release_date"], reverse=desc
        )

    # Pagination
    if per_page:
        start = (page - 1) * per_page
        end = page * per_page
        if start < 0 or start > len(postprocessed):
            start = 0
        if end < 0 or end > len(postprocessed):
            end = len(postprocessed)
        postprocessed = postprocessed[start:end]

    # Convert to SearchResponse objects
    for i in range(len(postprocessed)):
        movie = postprocessed[i]
        postprocessed[i] = SearchResponse(
            id=movie["movie"]["movie_id"],
            title=movie["movie"]["title"],
            release_year=movie["movie"]["release_date"][0:4],
            genres=[genre["name"] for genre in movie["movie"]["genres"]],
            image_url=movie["movie"]["image"],
            average_rating=float(movie["movie"]["average_rating"][0]),
            score=float(movie["score"]),
        )

    return postprocessed


@router.post(
    "/{movie_id}/rating", tags=["movies"], response_model=Wrapper[RatingResponse]
)
async def rate_movie(request: Request, movie_id: str, rating: float):
    user_id = request.session.get("user_id")
    if not user_id:
        return ApiException(500, 2001, "You are not logged in!")
    if not 0 <= rating <= 5.0 or rating % 0.5 != 0.0:
        return ApiException(500, 2101, "Invalid rating")

    try:
        async with in_transaction():
            existing_rating = await Ratings.get_or_none(
                user_id=user_id, movie_id=movie_id
            )
            if existing_rating:
                existing_rating.delete_date = None
                existing_rating.rating = rating
                await existing_rating.save(update_fields=["rating", "delete_date"])
            else:
                await Ratings.create(user_id=user_id, movie_id=movie_id, rating=rating)

            current_rating = await Ratings.get(user_id=user_id, movie_id=movie_id)
            existing_review = await Reviews.get_or_none(
                user_id=user_id, movie_id=movie_id
            )
            if existing_review:
                existing_review.rating = current_rating
                await existing_review.save(update_fields=["rating_id"])
    except OperationalError:
        return ApiException(500, 2102, "Could not rate movie")
    except IntegrityError:
        return ApiException(500, 2104, "Could not update fields")

    return wrap({"id": str(current_rating.rating_id), "rating": current_rating.rating})


@router.delete(
    "/{movie_id}/rating", tags=["movies"], response_model=Wrapper[RatingResponse]
)
async def delete_rating(request: Request, movie_id: str) -> Wrapper[dict]:
    user_id = request.session.get("user_id")
    if not user_id:
        return ApiException(500, 2001, "You are not logged in!")
    rating_id = ""
    rating = None
    try:
        async with in_transaction():
            existing_rating = await Ratings.get_or_none(
                user_id=user_id, movie_id=movie_id
            )
            if existing_rating:
                rating_id = existing_rating.rating_id
                rating = existing_rating.rating
                existing_rating.delete_date = datetime.now()
                await existing_rating.save(update_fields=["delete_date"])
                related_review = await Reviews.get_or_none(
                    user_id=user_id, movie_id=movie_id
                )
                if related_review:
                    related_review.rating = None
                    await related_review.save(update_fields=["rating_id"])
    except OperationalError:
        return ApiException(500, 2103, "Could not find or delete rating")
    except IntegrityError:
        return ApiException(500, 2104, "Could not update fields")

    return wrap({"id": str(rating_id), "rating": rating})
