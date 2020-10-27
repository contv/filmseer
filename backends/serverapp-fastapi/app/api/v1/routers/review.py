from fastapi import APIRouter, Request
from typing import Optional
from pydantic import BaseModel
from tortoise.exceptions import OperationalError
from tortoise.transactions import in_transaction
from datetime import datetime

from app.models.db.helpful_votes import HelpfulVotes
from app.models.db.funny_votes import FunnyVotes
from app.models.db.spoiler_votes import SpoilerVotes
from app.models.db.reviews import Reviews

from app.utils.wrapper import ApiException, Wrapper, wrap

router = APIRouter()
override_prefix = None
override_prefix_all = None


class NumVote(BaseModel):
    count: int


class ReviewRequest(BaseModel):
    description: str
    contains_spoiler: bool


class ReviewResponse(BaseModel):
    review_id: str
    create_date: str
    description: str
    contains_spoiler: bool
    rating: float
    num_helpful: int
    num_funny: int
    num_spoiler: int
    flagged_helpful: bool
    flagged_funny: bool
    flagged_spoiler: bool


# TODO LATER: This API is in the next sprint (follow) and should be in follow route

# GET /followed/reviews
# This lists all recent reviews from followed users.
#


@router.get("/reviews", tags=["review"])
async def search_user_review(request: Request, keyword: Optional[str] = ""):
    user_id = request.session.get("user_id")
    if not user_id:
        return ApiException(401, 2001, "You are not logged in")

    reviews = [
        ReviewResponse(
            review_id=str(r.review_id),
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
            user_id=user_id, delete_date=None, description__icontains=keyword
        ).prefetch_related("rating", "helpful_votes", "funny_votes", "spoiler_votes")
    ]

    return wrap({"items": reviews})


@router.put("/{review_id}", tags=["review"])
async def update_author_review(
    review_id: str, review: ReviewRequest, request: Request
):
    session_user_id = request.session.get("user_id")
    if not session_user_id:
        return ApiException(401, 2001, "You are not logged in")

    review_user_id = str(
        (await Reviews.filter(review_id=review_id, delete_date=None).values("user_id"))[
            0
        ]["user_id"]
    )

    if not review_user_id:
        return ApiException(404, 2610, "Invalid review id.")

    if session_user_id != review_user_id:
        return ApiException(
            401, 2609, "You must be the author to update/delete the review."
        )

    try:
        # should we update create_date?
        await Reviews.filter(review_id=review_id).update(
            delete_date=None,
            description=review.description,
            contains_spoiler=review.contains_spoiler,
        )
    except OperationalError:
        return ApiException(500, 2501, "An exception occurred")

    return wrap({})


@router.delete("/{review_id}", tags=["review"])
async def delete_author_review(review_id: str, request: Request):
    session_user_id = "058ffe8f-d27c-5e6a-21aa-c41401b996f9"
    if not session_user_id:
        return ApiException(401, 2001, "You are not logged in")

    review_user_id = str(
        (await Reviews.filter(review_id=review_id, delete_date=None).values("user_id"))[
            0
        ]["user_id"]
    )

    if not review_user_id:
        return ApiException(404, 2610, "Invalid review id.")

    if session_user_id != review_user_id:
        return ApiException(
            401, 2609, "You must be the author to update/delete the review."
        )

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
    except OperationalError:
        return ApiException(500, 2501, "An exception occurred")

    return wrap({})


@router.post("/{review_id}/helpful", tags=["review"], response_model=Wrapper[NumVote])
async def mark_review_helpful(review_id: str, request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return ApiException(
            401, 2600, "You must be logged in to mark the review as helpful."
        )
    try:
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
        return ApiException(500, 2501, "An exception occurred")
    return wrap({"count": num_helpful})


@router.post("/{review_id}/funny", tags=["review"], response_model=Wrapper[NumVote])
async def mark_review_funny(request: Request, review_id: str):
    user_id = request.session.get("user_id")
    if not user_id:
        return ApiException(
            401, 2601, "You must be logged in to mark the review as funny."
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
            await Reviews.filter(review_id=review_id).update(num_funny=num_funny)
    except OperationalError:
        return ApiException(500, 2501, "An exception occurred")
    return wrap({"count": num_funny})


@router.post("/{review_id}/spoiler", tags=["review"], response_model=Wrapper[NumVote])
async def mark_review_spoiler(request: Request, review_id: str):
    user_id = request.session.get("user_id")
    if not user_id:
        return ApiException(
            401, 2602, "You must be logged in to mark the review as spoiler."
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
            await Reviews.filter(review_id=review_id).update(num_spoiler=num_spoiler)
    except OperationalError:
        return ApiException(500, 2501, "An exception occurred")
    return wrap({"count": num_spoiler})


@router.delete("/{review_id}/helpful", tags=["review"], response_model=Wrapper[NumVote])
async def unmark_review_helpful(request: Request, review_id: str):
    user_id = request.session.get("user_id")
    if not user_id:
        return ApiException(
            401, 2603, "You must be logged in to unmark the review as helpful."
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
            await Reviews.filter(review_id=review_id).update(num_helpful=num_helpful)
    except OperationalError:
        return ApiException(500, 2501, "An exception occurred")
    return wrap({"count": num_helpful})


@router.delete("/{review_id}/funny", tags=["review"], response_model=Wrapper[NumVote])
async def unmark_review_funny(request: Request, review_id: str):
    user_id = request.session.get("user_id")
    if not user_id:
        return ApiException(
            401, 2604, "You must be logged in to unmark the review as funny."
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
            await Reviews.filter(review_id=review_id).update(num_funny=num_funny)
    except OperationalError:
        return ApiException(500, 2501, "An exception occurred")
    return wrap({"count": num_funny})


@router.delete("/{review_id}/spoiler", tags=["review"], response_model=Wrapper[NumVote])
async def unmark_review_spoiler(request: Request, review_id: str):
    user_id = request.session.get("user_id")
    if not user_id:
        return ApiException(
            401, 2605, "You must be logged in to unmark the review as spoiler."
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
            await Reviews.filter(review_id=review_id).update(num_spoiler=num_spoiler)
    except OperationalError:
        return ApiException(500, 2501, "An exception occurred")
    return wrap({"count": num_spoiler})
