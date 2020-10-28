from datetime import datetime
from typing import List, Optional

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
    cumulative_rating: float
    num_votes: int
    num_reviews: int
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
    genres: Optional[List[str]] = Query(None),
    years: Optional[List[str]] = Query(None),
    directors: Optional[List[str]] = Query(None),
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
            "multi_match",
            query=keywords,
            fields=[
                "title^10",
                "year^8",
                "description",
                "genres.name",
                "people.name",
                "positions.char_name",
            ],
        ),  # Add year, genre and people once server-side schema has been updated
    ]
    search = Search(using=conn, index="movie").extra(size=100)
    for query in queries:
        search = search.query(query)

    # TODO filter for genres, years, directors

    response = search.execute()
    preprocessed = [(hit.meta.id, hit.meta.score) for hit in response]
    postprocessed = await batched_movie_fetcher(
        request.session.get("user_id"), preprocessed
    )
    return wrap(postprocessed)


async def batched_movie_fetcher(user_id: Optional[str], preprocessed: List[tuple]):
    # TODO FIL-15 Grab blocked users and postprocess ratings
    blocked_users = []

    movies = []
    for movie_id, score in preprocessed:
        async with in_transaction():
            movie = await Movies.get_or_none(movie_id=movie_id)
            if movie:
                await movie.fetch_related("genres")
                movieResponse = SearchResponse(
                    id=str(movie.movie_id),
                    title=movie.title,
                    release_year=movie.release_date.year,
                    genres=[genre.name for genre in movie.genres],
                    image_url=movie.image,
                    cumulative_rating=movie.cumulative_rating,
                    num_votes=movie.num_votes,
                    num_reviews=movie.num_reviews,
                    score=score,
                )
                movies.append(movieResponse)
    return movies


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
