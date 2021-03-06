"""
Contains the API endpoints relating to Search and Recommendations
"""

import math
import re
from datetime import datetime
from random import choices
from typing import Dict, List, Optional

from dateutil.relativedelta import relativedelta
from elasticsearch import RequestsHttpConnection, Urllib3HttpConnection
from elasticsearch_dsl import Q, Search, connections
from fastapi import APIRouter, Query, Request
from humps import camelize
from pydantic import BaseModel, conint, constr
from tortoise.functions import Count

from app.core.config import settings
from app.models.db.banlists import Banlists
from app.models.db.movies import Movies
from app.models.db.ratings import Ratings
from app.utils.dict_storage.redis import RedisDictStorageDriver
from app.utils.recommender import load_movie_set, predict_on_movie, predict_on_user
from app.utils.wrapper import ApiException, Wrapper, wrap

router = APIRouter()
override_prefix = None
override_prefix_all = None

search_cache_driver = None
recommendation_cache_driver = None
elasticsearch = None


class FilterResponse(BaseModel):
    """Response object used to populate filters on page"""

    type: str
    name: str
    key: str
    selections: List


class SearchResponse(BaseModel):
    """Represents a movie object for populating movie tiles on page"""

    id: str
    title: str
    release_year: str
    genres: Optional[List[str]]
    image_url: Optional[str]
    average_rating: float
    num_votes: float
    cumulative_rating: float
    score: float

    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True


class MovieSuggestion(BaseModel):
    """Represents a suggestion line in the search bar as user is typing"""

    id: str
    title: str
    release_date: str
    image_url: Optional[str]

    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True


class ListMovieSuggestion(BaseModel):
    items: List[MovieSuggestion]


@router.on_event("startup")
async def init_search_cache_driver():
    """Initialise Redis connection for storing search history on startup."""
    global search_cache_driver
    if not search_cache_driver:
        search_cache_driver = RedisDictStorageDriver(
            key_prefix="search:",
            key_filter=r"[^a-zA-Z0-9_-]+",
            ttl=settings.REDIS_SEARCH_TTL,
            renew_on_ttl=settings.REDIS_SEARCH_TTL,
            redis_uri=settings.REDIS_URI,
            redis_pool_min=settings.REDIS_POOL_MIN,
            redis_pool_max=settings.REDIS_POOL_MAX,
        )
        await search_cache_driver.initialize_driver()
    return search_cache_driver


@router.on_event("startup")
async def init_recommendation_cache_driver():
    """Initialise Redis connection for storing recommendation history on startup."""
    global recommendation_cache_driver
    if not recommendation_cache_driver:
        recommendation_cache_driver = RedisDictStorageDriver(
            key_prefix="recommendations:",
            key_filter=r"[^a-zA-Z0-9_-]+",
            ttl=settings.REDIS_SEARCH_TTL,
            renew_on_ttl=settings.REDIS_SEARCH_TTL,
            redis_uri=settings.REDIS_URI,
            redis_pool_min=settings.REDIS_POOL_MIN,
            redis_pool_max=settings.REDIS_POOL_MAX,
        )
        await recommendation_cache_driver.initialize_driver()
    return recommendation_cache_driver


@router.on_event("startup")
def connect_elasticsearch():
    """Initialise Elasticsearch connection on startup."""
    global elasticsearch
    if not elasticsearch:
        elasticsearch = connections.create_connection(
            hosts=settings.ELASTICSEARCH_URI,
            alias=settings.ELASTICSEARCH_ALIAS,
            connection_class=RequestsHttpConnection
            if settings.ELASTICSEARCH_TRANSPORTCLASS == "RequestsHttpConnection"
            else Urllib3HttpConnection,
            timeout=settings.ELASTICSEARCH_TIMEOUT,
            use_ssl=settings.ELASTICSEARCH_USESSL,
            verify_certs=settings.ELASTICSEARCH_VERIFYCERTS,
            ssl_show_warn=settings.ELASTICSEARCH_SHOWSSLWARNINGS,
        )
    return elasticsearch


@router.on_event("shutdown")
async def terminate_recommendation_cache_driver():
    """Terminate recommendation history Redis driver"""
    global recommendation_cache_driver
    await recommendation_cache_driver.terminate_driver()


@router.on_event("shutdown")
async def terminate_search_cache_driver():
    """Terminate search history Redis driver"""
    global search_cache_driver
    await search_cache_driver.terminate_driver()


@router.get("/", tags=["movies"], response_model=Wrapper[Dict])
async def search_movies(
    request: Request,
    keywords: str = "",
    genres: Optional[List[str]] = Query(None),
    years: Optional[List[constr(regex=r"^$|^\d{4}$")]] = Query(None),  # noqa: F722
    directors: Optional[List[str]] = Query(None),
    per_page: Optional[conint(gt=0, le=100)] = None,
    page: Optional[conint(gt=0)] = 1,
    sort: Optional[constr(regex=r"^(?:relevance|rating|name|year)$")] = (  # noqa: F722
        "relevance",
        "rating",
        "name",
        "year",
    )[0],
    desc: Optional[bool] = True,
    field: Optional[str] = "all",
):
    """
    Main entrypoint for keyword search for movies using Elasticsearch.
    See docstring for get_movies().
    """

    return wrap(
        await get_movies(
            request=request,
            keywords=keywords,
            genres=list(filter(None, genres or [])),
            years=list(filter(None, years or [])),
            directors=list(filter(None, directors or [])),
            per_page=per_page or 1,
            page=page or 1,
            sort=sort or ("relevance", "rating", "name", "year")[0],
            desc=desc if desc is not None else True,
            cache_result=True,
            field=field or "all",
        )
    )


async def process_movie_payload(
    preprocessed: Dict,
    year_filter: List[str],
    director_filter: List[str],
    genre_filter: List[str],
    per_page: int,
    page: int,
    sort: str,
    desc: bool,
) -> Dict:
    """
    Given a preprocessed Elasticsearch response payload, apply filters, sorting and
    pagination, and returns an ordered array of SearchResponse objects each representing
    a movie tile.
    """
    # Populate filter options based on total payload
    genre_set = set(
        genre["name"]
        for movie_id in preprocessed
        if preprocessed[movie_id]["movie"]["genres"]
        for genre in preprocessed[movie_id]["movie"]["genres"]
    )
    director_set = set(
        position["people"]["name"]
        for movie_id in preprocessed
        if preprocessed[movie_id]["movie"]["positions"]
        for position in preprocessed[movie_id]["movie"]["positions"]
        if position["position"] == "director"
    )
    year_set = set(
        preprocessed[movie_id]["movie"]["release_date"][0:4]
        for movie_id in preprocessed
        if preprocessed[movie_id]["movie"]["release_date"]
    )

    # Use dicts for fast insertion of count, extract the values and discard keys later
    genre_selections = {
        genre: {"key": genre, "name": genre, "count": 0} for genre in genre_set
    }
    director_selections = {
        director: {"key": director, "name": director, "count": 0}
        for director in director_set
    }
    year_selections = {
        year: {"key": year, "name": year, "count": 0} for year in year_set
    }

    # Populate filter counts using all results
    for movie_id in preprocessed:
        movie = preprocessed[movie_id]
        if movie["movie"]["genres"]:
            for genre in movie["movie"]["genres"]:
                genre_selections[genre["name"]]["count"] += 1
        if movie["movie"]["positions"]:
            for position in movie["movie"]["positions"]:
                if position["position"] == "director":
                    director_selections[position["people"]["name"]]["count"] += 1
        if movie["movie"]["release_date"]:
            year_selections[movie["movie"]["release_date"][0:4]]["count"] += 1

    genre_selections = FilterResponse(
        type="list",
        name="Genre",
        key="genre",
        selections=sorted(list(genre_selections.values()), key=lambda x: x["name"]),
    )

    director_selections = FilterResponse(
        type="list",
        name="Directors",
        key="director",
        selections=sorted(list(director_selections.values()), key=lambda x: x["name"]),
    )

    year_selections = FilterResponse(
        type="slide",
        name="Year",
        key="year",
        selections=sorted(list(year_selections.values()), key=lambda x: x["name"]),
    )

    # Filter
    postprocessed = []
    for movie_id in preprocessed:
        genre_filter_pass, year_filter_pass, director_filter_pass = True, True, True
        movie = preprocessed[movie_id]["movie"]
        if genre_filter:
            try:
                genres = set(genre["name"] for genre in movie["genres"])
                if not genres.intersection(genre_filter):
                    genre_filter_pass = False
            except TypeError:
                genre_filter_pass = False
        if year_filter:
            try:
                year = movie["release_date"][0:4]
                if year not in year_filter:
                    year_filter_pass = False
            except TypeError:
                year_filter_pass = False
        if director_filter:
            try:
                directors = set(
                    position["people"]["name"]
                    for position in movie["positions"]
                    if position["position"] == "director"
                )
                if not directors.intersection(director_filter):
                    director_filter_pass = False
            except TypeError:
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
            postprocessed, key=lambda x: x["movie"]["title"], reverse=desc
        )
    elif sort == "year":
        postprocessed = sorted(
            postprocessed, key=lambda x: x["movie"]["average_rating"], reverse=True
        )
        postprocessed = sorted(
            postprocessed, key=lambda x: x["movie"]["release_date"], reverse=desc
        )

    # Calculate total
    total_pages = math.ceil(len(postprocessed) / per_page)

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
            num_votes=float(movie["movie"]["average_rating"][1]),
            cumulative_rating=float(movie["movie"]["average_rating"][2]),
            score=float(movie["score"]),
        )

    response = {
        "movies": postprocessed,
        "filters": [genre_selections, director_selections, year_selections],
        "total": total_pages,
    }

    return response


async def get_movies(
    request: Request,
    movies: Optional[List[str]] = None,
    keywords: Optional[str] = None,
    genres: Optional[List[str]] = None,
    years: Optional[List[str]] = None,
    directors: Optional[List[str]] = None,
    per_page: int = 1,
    page: int = 1,
    sort: str = ("relevance", "rating", "name", "year")[0],
    desc: bool = True,
    cache_result: bool = False,
    field: str = "all",
) -> Dict:
    """Performs Elasticsearch query to obtain movie payload.

    Used by both Search and Recommendations. Elasticsearch query will use the keyword
    term to search, and any movie ids provided in movies will be looked up and added
    to the movie payload.

    Args:
        movies: a list of strings representing each movie_id to be retrieved
        keywords: a string representing the user's search term as entered into the search bar.
        genres: a list of strings representing desired genres to match.
        years: a list of strings representing desired years to match.
        directors: a list of strings representing desired director names to match.
        per_page: int specifying how many results to return per page.
        page: int specifying the desired page to retrieve based on per_page.
        sort: string indicating sort field. Possible values are relevance, rating, name and year.
        desc: boolean specifying sort order. Default is descending order.
        cache_result: bool whether the Redis should be used to store resulting movie ids in memory.
        field: string indicating the user's chosen search type in the search bar.

    Returns:
        A dict response object structured as follows:
            response = {
                "movies": postprocessed,
                "filters": [genre_selections, director_selections, year_selections],
                "total": total_pages,
            }
        where postprocessed is a SearchResponse object, and filters is a list of FilterResponse objects.
    """

    if genres is None:
        genres = []
    if years is None:
        years = []
    if directors is None:
        directors = []
    if cache_result and keywords is not None:
        global search_cache_driver
        if not search_cache_driver:
            search_cache_driver = await init_search_cache_driver()

        # Lookup existing search in session
        session_name = "searches"
        if field != "all":
            session_name = field + "_searches"

        searches = request.session.get(session_name, {})
        try:
            search_id = searches[keywords]
        except KeyError:
            search_id = await search_cache_driver.create()
            if len(searches.keys()) >= settings.REDIS_SEARCHES_MAX:
                searches.pop(list(searches)[0])
            searches[keywords] = search_id
            request.session[session_name] = searches

        # Attempt to retrieve stored movie payload from Redis
        # If found, return the result without querying Elasticsearch
        payload, _ = await search_cache_driver.get(search_id)
        if payload:
            return await process_movie_payload(
                payload, years, directors, genres, per_page, page, sort, desc
            )

    global elasticsearch
    if not elasticsearch:
        connect_elasticsearch()

    # Build query context for scoring results
    years_in_keywords: List[str] = (
        re.findall(r"(\d{4})", keywords) if keywords is not None else []
    )

    # Support different search types selected via search bar
    fields = []
    if field == "all":
        fields = [
            "title^10",
            "description",
            "genres.name.keyword",
            "positions.people.name",
            "positions.char_name",
        ]
    if field == "title":
        fields = ["title"]
    elif field == "description":
        fields = ["description"]
    elif field == "genres":
        fields = ["genres.name"]
    elif field == "people":
        fields = ["positions.people.name"]

    # Match on fields and consider numbers in keyword as years if present
    queries = [
        Q(
            "bool",
            must=[
                Q(
                    "multi_match",
                    query=keywords,
                    fields=fields,
                )
            ]
            if keywords is not None
            else [],
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
            ]
            + (
                [Q("match", movie_id=movie_id) for movie_id in movies]
                if movies is not None
                else []
            ),
            minimum_should_match=(
                1 if ((movies is not None) or years_in_keywords) else 0
            ),
        )
    ]

    search = Search(using=elasticsearch, index=settings.ELASTICSEARCH_MOVIEINDEX).extra(
        size=settings.ELASTICSEARCH_RESPONSESIZE
    )

    for q in queries:
        search = search.query(q)

    # Get user's banlist and provide this to Elasticsearch
    list_ban = ""
    user_id = request.session.get("user_id")
    if user_id is not None:
        user_ban_list = await Banlists.filter(user_id=user_id, delete_date=None).values(
            "banned_user_id"
        )
        user_ban_list = [str(item["banned_user_id"]) for item in user_ban_list]
        list_ban = ",".join(user_ban_list)

    search = search.script_fields(
        average_rating={
            "script": {"id": "calculate_rating_field", "params": {"listban": list_ban}}
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

    if cache_result and keywords is not None:
        # Save response in Redis
        await search_cache_driver.update(search_id, preprocessed)

    postprocessed = await process_movie_payload(
        preprocessed, years, directors, genres, per_page, page, sort, desc
    )

    return postprocessed


@router.get(
    "/search-hint", tags=["Movies"], response_model=Wrapper[ListMovieSuggestion]
)
async def get_suggestion(
    keyword: str = "", limit: Optional[int] = 8, field: Optional[str] = "all"
):
    """Enables suggestions based on the user's currently entered search string

    Args:
        keyword: string representing what the user has currently entered
        limit: int representing the maximum number of suggestions to return
        field: a string indicating the type of search query to be performed

    Returns:
        a dict with key "items" containing an array of MovieSuggestion objects
    """

    global elasticsearch
    if not elasticsearch:
        elasticsearch = connect_elasticsearch()

    fields = []
    if field == "all":
        fields = [
            "title^10",
            "description",
            "genres.name.keyword",
            "positions.people.name",
            "positions.char_name",
        ]
    if field == "title":
        fields = ["title"]
    elif field == "description":
        fields = ["description"]
    elif field == "genres":
        fields = ["genres.name"]
    elif field == "people":
        fields = ["positions.people.name"]

    queries = [
        Q(
            "bool",
            must=[
                Q(
                    "multi_match",
                    query=keyword,
                    fields=fields,
                )
            ],
        )
    ]

    search = Search(using=elasticsearch, index=settings.ELASTICSEARCH_MOVIEINDEX).extra(
        size=limit
    )

    for q in queries:
        search = search.query(q)

    search = search.source(["movie_id", "title", "image", "release_date"])

    search = search.sort({"_score": {"order": "desc"}})
    response = search.execute()

    suggestions = [
        MovieSuggestion(
            id=hit.movie_id,
            title=hit.title,
            release_date=hit.release_date,
            image_url=hit.image,
        )
        for hit in response
    ]

    return wrap({"items": suggestions})


@router.get("/recommendation", tags=["Movies"], response_model=Wrapper[Dict])
async def get_recommendation(
    request: Request,
    type: constr(
        regex=r"^(?:foryou|detail|new|popular)$"  # noqa: F722
    ),  # "foryou", "detail", "new", "popular"
    size: conint(gt=0, le=50) = 20,
    movie_id: Optional[str] = None,
    recency: conint(gt=0, le=30) = 7,
    genres: Optional[List[str]] = Query(None),
    years: Optional[List[constr(regex=r"^$|^\d{4}$")]] = Query(None),  # noqa: F722
    directors: Optional[List[str]] = Query(None),
    per_page: Optional[conint(gt=0, le=100)] = None,
    page: Optional[conint(gt=0)] = 1,
    sort: Optional[constr(regex=r"^(?:relevance|rating|name|year)$")] = (  # noqa: F722
        "relevance",
        "rating",
        "name",
        "year",
    )[0],
    desc: Optional[bool] = True,
):
    """Retrieves movie recommendations to populate the What's New, Popular, For You and
    Movie Detail panels

    Args:
        type: a string representing the type of recommendation.
        size: int representing how many movies to return.
        movie_id: string representing movie id of the movie to find similar movies. Only required when type = "detail".
        recency: int representing how many days back in time to consider. Only required when type = "new" or "popular".
        genres: a list of strings representing desired genres to match.
        years: a list of strings representing desired years to match.
        directors: a list of strings representing desired director names to match.
        per_page: int specifying how many results to return per page.
        page: int specifying the desired page to retrieve based on per_page.
        sort: string indicating sort field. Possible values are relevance, rating, name and year.
        desc: boolean specifying sort order. Default is descending order.

    Returns:
        A dict response object structured as follows:
        response = {
            "movies": postprocessed,
            "filters": [genre_selections, director_selections, year_selections],
            "total": total_pages,
        }
        where postprocessed is a SearchResponse object, and filters is a list of FilterResponse objects.
    """

    cached_popular = False

    if not genres:
        genres = []
    genres = list(filter(None, genres))
    if not years:
        years = []
    years = list(filter(None, years))
    if not directors:
        directors = []
    directors = list(filter(None, directors))

    global recommendation_cache_driver
    if not recommendation_cache_driver:
        recommendation_cache_driver = await init_recommendation_cache_driver()

    # For You type recommendations
    if type == "foryou":
        user_id = request.session.get("user_id")
        if not user_id:
            raise ApiException(500, 2001, "You are not logged in!")
        # Check if foryou has been generated recently
        searches = request.session.get("recommendations", {})
        try:
            search_id = searches["foryou"]
        except KeyError:
            search_id = await recommendation_cache_driver.create()
            if len(searches.keys()) >= settings.REDIS_SEARCHES_MAX:
                searches.pop(list(searches)[0])
            searches["foryou"] = search_id
            request.session["recommendations"] = searches
        # Attempt to retrieve stored movie payload from Redis
        movies, _ = await recommendation_cache_driver.get(search_id)
        if movies:
            movies = movies["movies"]
        else:
            # Grab seen movies
            movies_seen = set(
                str(item[0])
                for item in await Ratings.filter(
                    user_id=user_id, delete_date=None
                ).values_list("movie_id")
            )
            # Calculate unseen movies
            try:
                movie_set = await load_movie_set()
            except TypeError:
                raise ApiException(404, 3000, "Recommendation not available")
            unseen = movie_set.difference(movies_seen)
            # Get a random subset for variety
            unseen = choices(tuple(unseen), k=settings.RECOMMENDER_RANDOM_SAMPLESIZE)
            try:
                movies = await predict_on_user(user_id, unseen, size)
                await recommendation_cache_driver.update(search_id, {"movies": movies})
            except TypeError:
                raise ApiException(404, 2090, "Recommendation not available")
    # Movie detail recommendations
    elif type == "detail":
        if not movie_id:
            raise ApiException(404, 2060, "That movie doesn't exist.")
        # Check if movie has had recommendations calculated on it within same session
        searches = request.session.get("recommendations", {})
        try:
            search_id = searches[movie_id]
        except KeyError:
            search_id = await recommendation_cache_driver.create()
            if len(searches.keys()) >= settings.REDIS_SEARCHES_MAX:
                searches.pop(list(searches)[0])
            searches[movie_id] = search_id
            request.session["recommendations"] = searches
        # Attempt to retrieve stored movie payload from Redis
        movies, _ = await recommendation_cache_driver.get(search_id)
        if movies:
            movies = movies["movies"]
        else:
            try:
                movies = await predict_on_movie(movie_id, size)
                await recommendation_cache_driver.update(search_id, {"movies": movies})
            except ValueError:
                raise ApiException(404, 2074, "Movie has not been rated before")
            except TypeError:
                raise ApiException(404, 2090, "Recommendation not available")
    # Popular type recommendations
    elif type == "popular":
        # Try to retrieve a cached popular recommendation
        movies, _ = await recommendation_cache_driver.get("popular")
        if movies:
            cached_popular = True
        else:
            cutoff_date = datetime.now() - relativedelta(days=recency)
            movies = (
                await Ratings.filter(create_date__gte=cutoff_date, delete_date=None)
                .annotate(movie_id_count=Count("movie_id"))
                .group_by("movie_id")
                .order_by("-movie_id_count")
                .limit(size)
                .values_list("movie_id", "movie_id_count")
            )
            movies = [str(movie[0]) for movie in movies]
    # New type recommendations
    elif type == "new":
        movies, _ = await recommendation_cache_driver.get("new")
        if movies:
            movies = movies["movies"]
        else:
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
            movies = [str(movie[0]) for movie in movies]
            await recommendation_cache_driver.update("new", {"movies": movies})
    else:
        raise ApiException(404, 2091, "Invalid recommendation type")

    # Postprocess to apply filters, sorting and pagination
    if cached_popular:
        # Parse movie payload retrieved from Redis into correct return structure
        movies["movies"] = [
            SearchResponse.parse_obj(movie) for movie in movies["movies"]
        ]
        movies["filters"] = [
            FilterResponse.parse_obj(filter) for filter in movies["filters"]
        ]
        postprocessed = movies
    else:
        postprocessed = await get_movies(
            request=request,
            movies=movies,
            genres=genres,
            years=years,
            directors=directors,
            per_page=per_page or 1,
            page=page or 1,
            sort=sort or ("relevance", "rating", "name", "year")[0],
            desc=desc if desc is not None else True,
            cache_result=False,
        )
        # Cache postprocessed payload for Popular, which is only visible to logged out users (no banlist required)
        if type == "popular":
            # Convert movie payload as necessary to save into Redis
            postprocessed_to_save = postprocessed.copy()
            postprocessed_to_save["movies"] = [
                movie.dict() for movie in postprocessed_to_save["movies"]
            ]
            postprocessed_to_save["filters"] = [
                filter.dict() for filter in postprocessed_to_save["filters"]
            ]
            await recommendation_cache_driver.update("popular", postprocessed_to_save)

    return wrap(postprocessed)
