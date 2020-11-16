from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Request
from humps import camelize
from pydantic import BaseModel
from tortoise.exceptions import OperationalError
from tortoise.transactions import in_transaction

from app.models.db.funny_votes import FunnyVotes
from app.models.db.helpful_votes import HelpfulVotes
from app.models.db.movies import Movies
from app.models.db.reviews import Reviews
from app.models.db.spoiler_votes import SpoilerVotes
from app.utils.wrapper import ApiException, Wrapper, wrap

router = APIRouter()
override_prefix = ""
override_prefix_all = None

"""
This API controller handles all routes under the prefix /review. It returns 
and handles review related data such as text, spoiler flagging, and review 
metadata such as funny and helpful votes.
"""

class NumVote(BaseModel):
    count: int

# basic review request involves just the text and whether it
# has been flagged by the author as containing a spoiler
class ReviewRequest(BaseModel):
    description: str
    contains_spoiler: bool

class ReviewCreateDate(BaseModel):
    create_date: datetime

# the detailed review response that contains all review
# related data
class ReviewResponse(BaseModel):
    review_id: str
    user_id: str
    username: str
    movie_id: str
    movie_title: str
    movie_year: str
    create_date: str
    description: str
    contains_spoiler: bool
    rating: Optional[float]
    num_helpful: int
    num_funny: int
    num_spoiler: int
    flagged_helpful: bool
    flagged_funny: bool
    flagged_spoiler: bool

    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True


class ListReviewResponse(BaseModel):
    items: List[ReviewResponse]

#gets all reviews for that user, with pagination included
@router.get("/reviews", tags=["review"], response_model=Wrapper[ListReviewResponse])
async def search_user_review(
    request: Request, keyword: Optional[str] = "", page: int = 0, per_page: int = 0
):
    #validate pagination parameters
    if per_page >= 42:
        raise ApiException(400, 2700, "Please limit the numer of items per page")
    if (per_page < 0) or (page < 0):
        raise ApiException(400, 2701, "Invalid page/per_page parameter")
    user_id = request.session.get("user_id")
    if not user_id:
        raise ApiException(401, 2001, "You are not logged in")

    # gets all reviews ordered by created date, including
    # all relevant data and metadata 
    reviews = [
        ReviewResponse(
            review_id=str(r.review_id),
            user_id=str(r.user_id),
            username=r.user.username,
            movie_id=str(r.movie_id),
            movie_title=str(r.movie.title),
            movie_year=str(r.movie.release_date),
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
        for r in await Reviews.filter(user_id=user_id, delete_date=None)
        .order_by("-create_date")
        .offset((page - 1) * per_page)
        .limit(per_page)
        .prefetch_related(
            "rating", "helpful_votes", "funny_votes", "spoiler_votes", "user", "movie"
        )
    ]

    return wrap({"items": reviews})

# modifies a particular review by its author.
@router.put("/review/{review_id}", tags=["review"])
async def update_author_review(review_id: str, review: ReviewRequest, request: Request):
    session_user_id = request.session.get("user_id")
    if not session_user_id:
        raise ApiException(401, 2001, "You are not logged in")

    review_user_id = (await Reviews.filter(review_id=review_id, delete_date=None).values("user_id", "movie_id"))[0]["user_id"]
    if not review_user_id:
        raise ApiException(404, 2081, "Invalid review id.")
    #must be your review to update
    if session_user_id != str(review_user_id):
        raise ApiException(
            401, 2082, "You must be the author to update/delete the review."
        )

    review_movie_id = review[0]["movie_id"]

    #attempts to update review in db
    try:
        await Reviews.filter(review_id=review_id).update(
            delete_date=None,
            description=review.description,
            contains_spoiler=review.contains_spoiler,
        )
        num_reviews = await Reviews.filter(
            movie_id=review_movie_id, delete_date=None
        ).count()
        await Movies.filter(movie_id=review_movie_id).update(num_reviews=num_reviews)

    except OperationalError:
        raise ApiException(500, 2501, "An exception occurred")

    return wrap({})

# delets a given review
@router.delete("/review/{review_id}", tags=["review"])
async def delete_author_review(review_id: str, request: Request):
    session_user_id = request.session.get("user_id")
    if not session_user_id:
        raise ApiException(401, 2001, "You are not logged in")

    review_user_id = (await Reviews.filter(review_id=review_id, delete_date=None).values("user_id", "movie_id"))[0]["user_id"]
    if not review_user_id:
        raise ApiException(404, 2610, "Invalid review id.")
    
    # must be your own review to delete it
    if session_user_id != str(review_user_id):
        raise ApiException(
            401, 2609, "You must be the author to update/delete the review."
        )
    review_movie_id = review[0]["movie_id"]
    # deletes and updates all associated review data
    try:
        await Reviews.filter(review_id=review_id).update(
            delete_date=datetime.now(),
        )

        await HelpfulVotes.filter(review_id=review_id).update(
            delete_date=datetime.now()
        )
        await FunnyVotes.filter(review_id=review_id).update(delete_date=datetime.now())
        await SpoilerVotes.filter(review_id=review_id).update(
            delete_date=datetime.now()
        )
        num_reviews = await Reviews.filter(
            movie_id=review_movie_id, delete_date=None
        ).count()
        # updates data for movie.
        await Movies.filter(movie_id=review_movie_id).update(num_reviews=num_reviews)
    except OperationalError:
        raise ApiException(500, 2501, "An exception occurred")

    return wrap({})

# adds a helpful vote to a review
@router.post(
    "/review/{review_id}/helpful", tags=["review"], response_model=Wrapper[NumVote]
)
async def mark_review_helpful(review_id: str, request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        raise ApiException(
            401, 2001, "You are not logged in!"
        )
    try:
        # after adding helpful votes, update review helpful count
        async with in_transaction():
            await HelpfulVotes.get_or_create(review_id=review_id, user_id=user_id)
            await HelpfulVotes.filter(review_id=review_id, user_id=user_id).update(
                delete_date=None
            )
            num_helpful = await HelpfulVotes.filter(
                review_id=review_id, delete_date=None
            ).count()
            await Reviews.filter(review_id=review_id).update(num_helpful=num_helpful)
    except OperationalError:
        raise ApiException(500, 2501, "An exception occurred")
    return wrap({"count": num_helpful})

# adds a funny vote to a review
@router.post(
    "/review/{review_id}/funny", tags=["review"], response_model=Wrapper[NumVote]
)
async def mark_review_funny(request: Request, review_id: str):
    user_id = request.session.get("user_id")
    if not user_id:
        raise ApiException(
            401, 2001, "You are not logged in!"
        )
    try:
        async with in_transaction():
            await FunnyVotes.get_or_create(review_id=review_id, user_id=user_id)
            await FunnyVotes.filter(review_id=review_id, user_id=user_id).update(
                delete_date=None
            )
            num_funny = await FunnyVotes.filter(
                review_id=review_id, delete_date=None
            ).count()
            # after adding funny votes, update review funny count
            await Reviews.filter(review_id=review_id).update(num_funny=num_funny)
    except OperationalError:
        raise ApiException(500, 2501, "An exception occurred")
    return wrap({"count": num_funny})

# adds a spoiler vote for a review
@router.post(
    "/review/{review_id}/spoiler", tags=["review"], response_model=Wrapper[NumVote]
)
async def mark_review_spoiler(request: Request, review_id: str):
    user_id = request.session.get("user_id")
    if not user_id:
        raise ApiException(
            401, 2001, "You are not logged in!"
        )
    try:
        async with in_transaction():
            await SpoilerVotes.get_or_create(review_id=review_id, user_id=user_id)
            await SpoilerVotes.filter(review_id=review_id, user_id=user_id).update(
                delete_date=None
            )
            num_spoiler = await SpoilerVotes.filter(
                review_id=review_id, delete_date=None
            ).count()
            # after adding spoiler votes, update review spoiler count
            await Reviews.filter(review_id=review_id).update(num_spoiler=num_spoiler)
    except OperationalError:
        raise ApiException(500, 2501, "An exception occurred")
    return wrap({"count": num_spoiler})

# deletes helpful vote for review
@router.delete(
    "/review/{review_id}/helpful", tags=["review"], response_model=Wrapper[NumVote]
)
async def unmark_review_helpful(request: Request, review_id: str):
    user_id = request.session.get("user_id")
    if not user_id:
        raise ApiException(
            401, 2001, "You are not logged in!"
        )
    try:
        async with in_transaction():
            await HelpfulVotes.get_or_create(review_id=review_id, user_id=user_id)
            await HelpfulVotes.filter(review_id=review_id, user_id=user_id).update(
                delete_date=datetime.now()
            )
            num_helpful = await HelpfulVotes.filter(
                review_id=review_id, delete_date=None
            ).count()
            # after deleting helpful votes, update review helpful count
            await Reviews.filter(review_id=review_id).update(num_helpful=num_helpful)
    except OperationalError:
        raise ApiException(500, 2501, "An exception occurred")
    return wrap({"count": num_helpful})


# deletes funny vote for review
@router.delete(
    "/review/{review_id}/funny", tags=["review"], response_model=Wrapper[NumVote]
)
async def unmark_review_funny(request: Request, review_id: str):
    user_id = request.session.get("user_id")
    if not user_id:
        raise ApiException(
            401, 2001, "You are not logged in!"
        )
    try:
        async with in_transaction():
            await FunnyVotes.get_or_create(review_id=review_id, user_id=user_id)
            await FunnyVotes.filter(review_id=review_id, user_id=user_id).update(
                delete_date=datetime.now()
            )
            num_funny = await FunnyVotes.filter(
                review_id=review_id, delete_date=None
            ).count()
            # after deleting funny votes, updates review funny count
            await Reviews.filter(review_id=review_id).update(num_funny=num_funny)
    except OperationalError:
        raise ApiException(500, 2501, "An exception occurred")
    return wrap({"count": num_funny})


# deletes spoiler vote for review
@router.delete(
    "/review/{review_id}/spoiler", tags=["review"], response_model=Wrapper[NumVote]
)
async def unmark_review_spoiler(request: Request, review_id: str):
    user_id = request.session.get("user_id")
    if not user_id:
        raise ApiException(
            401, 2001, "You are not logged in!"
        )
    try:
        async with in_transaction():
            await SpoilerVotes.get_or_create(review_id=review_id, user_id=user_id)
            await SpoilerVotes.filter(review_id=review_id, user_id=user_id).update(
                delete_date=datetime.now()
            )
            num_spoiler = await SpoilerVotes.filter(
                review_id=review_id, delete_date=None
            ).count()
            # after deleting spoiler votes, updates review spoiler count
            await Reviews.filter(review_id=review_id).update(num_spoiler=num_spoiler)
    except OperationalError:
        raise ApiException(500, 2501, "An exception occurred")
    return wrap({"count": num_spoiler})
