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


class RatingResponse(BaseModel):
    id: str
    rating: float


class AverageRatingResponse(BaseModel):
    average: float


@router.get("/{movie_id}/ratings", response_model=Wrapper[AverageRatingResponse])
async def get_average_rating(movie_id: str, request: Request) -> Wrapper[dict]:
    user_id = request.session.get("user_id")
    try:
        movie = (
            await Movies.filter(movie_id=movie_id, delete_date=None)
            .prefetch_related("genres")
            .first()
        )
    except OperationalError:
        raise ApiException(401, 2501, "You cannot do that.")

    if movie is None:
        raise ApiException(404, 2100, "That movie doesn't exist")

    # TODO remove ratings from blocked users
    return wrap(
        {
            "average": (
                await calc_average_rating(
                    movie.cumulative_rating, movie.num_votes, user_id, movie_id
                )
            )["average_rating"]
        }
    )


@router.get("/{movie_id}", tags=["movies"], response_model=Wrapper[MovieResponse])
async def get_movie(movie_id: str, request: Request):
    user_id = request.session.get("user_id")
    try:
        movie = await Movies.filter(movie_id=movie_id, delete_date=None).first()
    except OperationalError:
        raise ApiException(401, 2501, "You cannot do that.")

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

    rating = await calc_average_rating(
        movie.cumulative_rating, movie.num_votes, user_id, movie_id
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
        num_votes=rating["num_votes"],
        average_rating=rating["average_rating"],
        genres=genres,
        crew=crew,
    )

    return wrap(movie_detail)


# REVIEW RELATED START


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
        raise ApiException(401, 2501, "You cannot do that.")

    if movie is None:
        raise ApiException(404, 2100, "That movie doesn't exist")

    user_id = request.session.get("user_id")
    if not user_id:
        raise ApiException(
            401, 2607, "You must be logged in to submit/update/delete a review"
        )

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
        raise ApiException(500, 2501, "An exception occurred")

    return wrap({"create_date": create_date})


@router.delete("/{movie_id}/review", tags=["movies"])
async def delete_user_review(movie_id: str, request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        raise ApiException(
            401, 2607, "You must be logged in to submit/update/delete a review"
        )
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


@router.post(
    "/{movie_id}/rating", tags=["movies"], response_model=Wrapper[RatingResponse]
)
async def rate_movie(request: Request, movie_id: str, rating: float):
    user_id = request.session.get("user_id")
    if not user_id:
        raise ApiException(500, 2001, "You are not logged in!")
    if not 0 <= rating <= 5.0 or rating % 0.5 != 0.0:
        raise ApiException(500, 2101, "Invalid rating")

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
        raise ApiException(500, 2102, "Could not rate movie")
    except IntegrityError:
        raise ApiException(500, 2104, "Could not update fields")

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
        raise ApiException(500, 2103, "Could not find or delete rating")
    except IntegrityError:
        raise ApiException(500, 2104, "Could not update fields")

    return wrap({"id": str(rating_id), "rating": rating})


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
            exceptions=[ApiException(500, 2103, "Could not find or delete rating")],
        )

    response = RatingResponse(id=str(rating.rating_id), rating=rating.rating)

    return wrap(response)
