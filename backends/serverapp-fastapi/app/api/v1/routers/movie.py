from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Request
from humps import camelize
from pydantic import BaseModel
from tortoise.exceptions import IntegrityError, OperationalError
from tortoise.transactions import in_transaction

from app.models.db.banlists import Banlists
from app.models.db.funny_votes import FunnyVotes
from app.models.db.helpful_votes import HelpfulVotes
from app.models.db.movies import Movies
from app.models.db.positions import Positions
from app.models.db.ratings import Ratings
from app.models.db.reviews import Reviews
from app.models.db.spoiler_votes import SpoilerVotes
from app.utils.ratings import calc_average_rating
from app.utils.wrapper import ApiException, Wrapper, wrap

from .review import ListReviewResponse, ReviewCreateDate, ReviewRequest, ReviewResponse

router = APIRouter()
override_prefix = None
override_prefix_all = None

"""
This API controller handles all routes under the prefix /movie. It returns 
detailed movie responses, movie reviews and handles user-related movie 
interactions such as ratings and leaving reviews.
"""

# trailers are represented by their site and their key as 
# a unique url identifier e.g. {site}.com/{key}. We support
# vimeo and youtube which both follow this scheme
class Trailer(BaseModel):
    key: str
    site: str

# crew objects represent both cast and other film crew members
# such as filmographers and directors.
class CrewMember(BaseModel):
    id: str
    name: str
    position: str
    image: Optional[str]

# this is the highest detail response for a movie, providing
# most relevant details about that movie.
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

# represents a user's movie rating
class RatingResponse(BaseModel):
    id: str
    rating: float

# represents the average rating of a movie 
class AverageRatingResponse(BaseModel):
    average: float

# this method gets the average rating for a movie, with banned list taking into account.
@router.get("/{movie_id}/ratings", response_model=Wrapper[AverageRatingResponse])
async def get_average_rating(movie_id: str, request: Request) -> Wrapper[dict]:
    user_id = request.session.get("user_id")
    
    # gets the relevant movie object
    try:
        movie = (
            await Movies.filter(movie_id=movie_id, delete_date=None)
            .prefetch_related("genres")
            .first()
        )
    except OperationalError:
        raise ApiException(401, 2070, "There was a problem fetching that movie's ratings.")

    if movie is None:
        raise ApiException(404, 2060, "That movie doesn't exist.")

    # passes the count and cumulative rating to our utility which produces the correct
    # result with banned users taken into account.
    return wrap(
        {
            "average": (
                await calc_average_rating(
                    movie.cumulative_rating, movie.num_votes, user_id, movie_id
                )
            )["average_rating"]
        }
    )

# gets the detailed movie object
@router.get("/{movie_id}", tags=["movies"], response_model=Wrapper[MovieResponse])
async def get_movie(movie_id: str, request: Request):
    user_id = request.session.get("user_id")
    try:
        movie = await Movies.filter(movie_id=movie_id, delete_date=None).first()
    except OperationalError:
        raise ApiException(401, 2501, "An exception occurred")

    if movie is None:
        raise ApiException(404, 2100, "That movie doesn't exist")

    # collect genres
    genres = [genre.name for genre in await movie.genres]
    
    # gets all people who worked on the film and then creates a 
    # crew object for each
    crew = [
        CrewMember(
            id=str(p.person_id),
            name=p.person.name,
            position=p.position,
            image=p.person.image,
        )
        for p in await Positions.filter(movie_id=movie_id).prefetch_related("person")
    ]

    # get rating, with banned list taken into account
    rating = await calc_average_rating(
        movie.cumulative_rating, movie.num_votes, user_id, movie_id
    )
    
    # final movie detail to return
    movie_detail = MovieResponse(
        id=str(movie.movie_id),
        title=movie.title,
        release_date=str(movie.release_date),
        release_year=str(movie.release_date.year),
        description=movie.description,
        image_url=movie.image,
        trailers=movie.trailer,
        num_reviews=movie.num_reviews,
        num_votes=rating["num_votes"],
        average_rating=rating["average_rating"],
        genres=genres,
        crew=crew,
    )

    return wrap(movie_detail)


# REVIEW RELATED START

# gets all reviews for a movie
@router.get(
    "/{movie_id}/reviews", tags=["movies"], response_model=Wrapper[ListReviewResponse]
)
async def get_movie_reviews(
    movie_id: str,
    request: Request,
    page: int = 0,
    per_page: int = 0,
    me: Optional[bool] = False,
):
    # handle pagination parameters
    if per_page >= 42:
        raise ApiException(400, 2700, "Please limit the numer of items per page")
    if (per_page < 0) or (page < 0):
        raise ApiException(400, 2701, "Invalid page/per_page parameter")
    user_id = request.session.get("user_id")
    # No need to raise exception if user_id = None as guest user should see the review

    # Return the review for current user only (for this movie)
    if me:
        reviews = [
            ReviewResponse(
                review_id=str(r.review_id),
                user_id=str(r.user_id),
                username=r.user.username,
                create_date=str(r.create_date),
                description=r.description,
                contains_spoiler=r.contains_spoiler,
                rating=r.rating.rating,
                num_helpful=r.num_helpful,
                num_funny=r.num_funny,
                num_spoiler=r.num_spoiler,
                flagged_helpful=await r.helpful_votes.filter(
                    user_id=user_id, delete_date=None
                ).count(),
                flagged_funny=await r.funny_votes.filter(
                    user_id=user_id, delete_date=None
                ).count(),
                flagged_spoiler=await r.spoiler_votes.filter(
                    user_id=user_id, delete_date=None
                ).count(),
            )
            for r in await Reviews.filter(
                movie_id=movie_id, delete_date=None, user_id=user_id
            )
            .order_by("-create_date")
            .offset((page - 1) * per_page)
            .limit(per_page)
            .prefetch_related(
                "rating", "helpful_votes", "funny_votes", "spoiler_votes", "user"
            )
        ]
    # Return the review for all other users (for this movie)
    else:
        exclude_list = []
        if user_id is not None:
            exclude_list.append(user_id)
            ban_list = await Banlists.filter(user_id=user_id, delete_date=None).values(
                "banned_user_id"
            )
            for item in ban_list:
                exclude_list.append(str(item["banned_user_id"]))

        reviews = [
            ReviewResponse(
                review_id=str(r.review_id),
                user_id=str(r.user_id),
                username=r.user.username,
                create_date=str(r.create_date),
                description=r.description,
                contains_spoiler=r.contains_spoiler,
                rating=r.rating.rating,
                num_helpful=r.num_helpful,
                num_funny=r.num_funny,
                num_spoiler=r.num_spoiler,
                flagged_helpful=await r.helpful_votes.filter(
                    user_id=user_id, delete_date=None
                ).count(),
                flagged_funny=await r.funny_votes.filter(
                    user_id=user_id, delete_date=None
                ).count(),
                flagged_spoiler=await r.spoiler_votes.filter(
                    user_id=user_id, delete_date=None
                ).count(),
            )
            for r in await Reviews.filter(movie_id=movie_id, delete_date=None)
            .exclude(user_id__in=exclude_list)
            .order_by("-create_date")
            .offset((page - 1) * per_page)
            .limit(per_page)
            .prefetch_related(
                "rating", "helpful_votes", "funny_votes", "spoiler_votes", "user"
            )
        ]
    return wrap({"items": reviews})

# adds or modifies a review
@router.post(
    "/{movie_id}/review", tags=["movies"], response_model=Wrapper[ReviewCreateDate]
)
@router.put(
    "/{movie_id}/review", tags=["movies"], response_model=Wrapper[ReviewCreateDate]
)
async def create_update_user_review(
    movie_id: str, review: ReviewRequest, request: Request
):
    try:
        movie = await Movies.filter(movie_id=movie_id, delete_date=None).first()
    except OperationalError:
        raise ApiException(401, 2080, "You cannot post a review for that movie.")

    if movie is None:
        raise ApiException(404, 2060, "That movie doesn't exist")

    user_id = request.session.get("user_id")
    if not user_id:
        raise ApiException(
            401, 2001, "You are not logged in!"
        )

    # attempt to add review to db
    try:
        async with in_transaction():
            rating = await (
                Ratings.get_or_create(
                    user_id=user_id,
                    movie_id=movie_id,
                )
            )
            create_date = datetime.now()
            if await Reviews.filter(user_id=user_id, movie_id=movie_id):
                await Reviews.filter(user_id=user_id, movie_id=movie_id).update(
                    rating_id=rating[0].rating_id,
                    delete_date=None,
                    create_date=create_date,
                    description=review.description,
                    contains_spoiler=review.contains_spoiler,
                )
            else:
                await Reviews(
                    user_id=user_id,
                    movie_id=movie_id,
                    create_date=create_date,
                    rating_id=rating[0].rating_id,
                    description=review.description,
                    contains_spoiler=review.contains_spoiler,
                    delete_date=None,
                ).save()
            num_reviews = await Reviews.filter(
                movie_id=movie_id, delete_date=None
            ).count()
            await Movies.filter(movie_id=movie_id).update(num_reviews=num_reviews)
    except OperationalError:
        raise ApiException(500, 2080, "An exception occurred")

    return wrap({"create_date": create_date})

# delete previously posted review
@router.delete("/{movie_id}/review", tags=["movies"])
async def delete_user_review(movie_id: str, request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        raise ApiException(
            401, 2001, "You are not logged in!"
        )
    
    #attempt to remove from db
    try:
        async with in_transaction():
            review = await Reviews.get_or_create(user_id=user_id, movie_id=movie_id)
            await Reviews.filter(
                user_id=user_id,
                movie_id=movie_id,
            ).update(delete_date=datetime.now())

            await HelpfulVotes.filter(review_id=review[0].review_id).update(
                delete_date=datetime.now()
            )
            await FunnyVotes.filter(review_id=review[0].review_id).update(
                delete_date=datetime.now()
            )
            await SpoilerVotes.filter(review_id=review[0].review_id).update(
                delete_date=datetime.now()
            )

            num_reviews = await Reviews.filter(
                movie_id=movie_id, delete_date=None
            ).count()
            await Movies.filter(movie_id=movie_id).update(num_reviews=num_reviews)

    except OperationalError:
        raise ApiException(500, 2501, "An exception occurred")

    return wrap({})


# REVIEW RELATED END

# adds a user rating for a movie
@router.post(
    "/{movie_id}/rating", tags=["movies"], response_model=Wrapper[RatingResponse]
)
async def rate_movie(request: Request, movie_id: str, rating: float):
    user_id = request.session.get("user_id")
    if not user_id:
        raise ApiException(500, 2001, "You are not logged in!")
    # handle invalid rating request
    if not 0 <= rating <= 5.0 or rating % 0.5 != 0.0:
        raise ApiException(500, 2073, "Invalid rating.")

    # attempt to add rating to db
    try:
        async with in_transaction():
            existing_rating = await Ratings.get_or_none(
                user_id=user_id, movie_id=movie_id
            )
            if existing_rating:
                old_rating = existing_rating.rating
                if existing_rating.delete_date:
                    existing_rating.delete_date = None
                    existing_rating.rating = rating
                    await update_cumulative_rating(movie_id, rating)
                else:
                    existing_rating.rating = rating
                    await update_cumulative_rating(movie_id, rating, old_rating)
                await existing_rating.save(update_fields=["rating", "delete_date"])
            else:
                await Ratings.create(user_id=user_id, movie_id=movie_id, rating=rating)
                await update_cumulative_rating(movie_id, rating)
            current_rating = await Ratings.get(user_id=user_id, movie_id=movie_id)
            await update_review_rating(user_id, movie_id, current_rating)
    except OperationalError:
        raise ApiException(500, 2072, "Could not rate movie.")
    except IntegrityError:
        raise ApiException(500, 2072, "Could not rate movie.")

    return wrap({"id": str(current_rating.rating_id), "rating": current_rating.rating})


async def update_cumulative_rating(
    movie_id: str, new_rating: float, old_rating: float = None
):
    """
    Updates a given movie's cumulative rating and num votes fields.
    If no old rating is provided, rating is assumed to a new or a deleted.
    In case of a deleted rating, ensure that new_rating is a negative floating value.
    """
    try:
        async with in_transaction():
            movie = await Movies.get_or_none(movie_id=movie_id, delete_date=None)
            if movie:
                if old_rating:
                    movie.cumulative_rating += new_rating - old_rating
                else:
                    movie.num_votes += 1 if new_rating >= 0 else -1
                    movie.cumulative_rating += new_rating
                await movie.save(update_fields=["cumulative_rating", "num_votes"])
    except OperationalError:
        raise OperationalError


async def update_review_rating(
    user_id: str, movie_id: str, rating_object: Ratings = None
):
    """
    Sets an existing review's 'rating' field to point to the provided rating_object
    or null the field if no rating object is provided
    """
    try:
        async with in_transaction():
            review = await Reviews.get_or_none(
                user_id=user_id, movie_id=movie_id, delete_date=None
            )
            if review:
                review.rating = rating_object
                await review.save(update_fields=["rating_id"])
    except OperationalError:
        raise OperationalError

# removes a rating for that user
@router.delete(
    "/{movie_id}/rating", tags=["movies"], response_model=Wrapper[RatingResponse]
)
async def delete_rating(request: Request, movie_id: str) -> Wrapper[dict]:
    user_id = request.session.get("user_id")
    if not user_id:
        raise ApiException(500, 2001, "You are not logged in!")
    rating_id = ""
    rating = None
    try:
        async with in_transaction():
            existing_rating = await Ratings.get_or_none(
                user_id=user_id, movie_id=movie_id
            )
            if existing_rating and not existing_rating.delete_date:
                rating_id = existing_rating.rating_id
                rating = existing_rating.rating
                existing_rating.delete_date = datetime.now()
                await existing_rating.save(update_fields=["delete_date"])
                await update_cumulative_rating(movie_id, -rating)
                await update_review_rating(user_id, movie_id)
    except OperationalError:
        raise ApiException(500, 2071, "Could not find or delete rating")
    except IntegrityError:
        raise ApiException(500, 2071, "Could not find or delete rating")

    return wrap({"id": str(rating_id), "rating": rating})

# returns the user rating for a movie
@router.get(
    "/{movie_id}/rating", tags=["Movies"], response_model=Wrapper[RatingResponse]
)
async def get_current_user_rating(request: Request, movie_id: str):
    user_id = request.session.get("user_id")
    if not user_id:
        raise ApiException(500, 2001, "You are not logged in!")

    rating = await Ratings.get_or_none(
        user_id=user_id, movie_id=movie_id, delete_date=None
    )

    if not rating:
        return wrap(
            code=200,
            message="No rating exists for this user",
            exceptions=[ApiException(500, 2071, "Could not find or delete rating")],
        )

    response = RatingResponse(id=str(rating.rating_id), rating=rating.rating)

    return wrap(response)
