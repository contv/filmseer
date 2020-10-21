from fastapi import APIRouter, Request
from tortoise.exceptions import OperationalError

from app.models.db.helpful_votes import HelpfulVotes
from app.models.db.funny_votes import FunnyVotes
from app.models.db.spoiler_votes import SpoilerVotes
from app.models.db.reviews import Reviews

from app.utils.wrapper import ApiException, Wrapper, wrap

router = APIRouter()
override_prefix = None
override_prefix_all = None


@router.post("/review/{id}/helpful")
async def mark_review_helpful(request: Request, id: str) -> Wrapper[dict]:
    user_id = request.session.get("user_id")
    if not user_id:
        return ApiException(
            401, 2500, "You must be logged in to mark the review as helpful."
        )
    try:
        await HelpfulVotes(review_id=id, user_id=user_id).save()
        helpful_in_review = await Reviews.filter(review_id=id)
        helpful_in_review.helpful_votes = helpful_in_review.helpful_votes + 1
        helpful_in_review.save()
    except OperationalError:
        return ApiException(401, 2501, "An exception occurred")
    return wrap({})


@router.post("/review/{id}/funny")
async def mark_review_funny(request: Request, id: str) -> Wrapper[dict]:
    user_id = request.session.get("user_id")
    if not user_id:
        return ApiException(
            401, 2500, "You must be logged in to mark the review as funny."
        )
    try:
        await FunnyVotes(review_id=id, user_id=user_id).save()
        funny_in_review = await Reviews.filter(review_id=id)
        funny_in_review.funny_votes = funny_in_review.funny_votes + 1
        funny_in_review.save()
    except OperationalError:
        return ApiException(401, 2501, "An exception occurred")
    return wrap({})


@router.post("/review/{id}/spoiler")
async def mark_review_spoiler(request: Request, id: str) -> Wrapper[dict]:
    user_id = request.session.get("user_id")
    if not user_id:
        return ApiException(
            401, 2500, "You must be logged in to mark the review as helpful."
        )
    try:
        await SpoilerVotes(review_id=id, user_id=user_id).save()
        spoiler_in_review = await Reviews.filter(review_id=id)
        spoiler_in_review.spoiler_votes = spoiler_in_review.spoiler_votes + 1
        if spoiler_in_review.spoiler_votes > 9:
            spoiler_in_review.contain_spoiler = 1
        spoiler_in_review.save()
    except OperationalError:
        return ApiException(401, 2501, "An exception occurred")
    return wrap({})


@router.delete("/review/{id}/helpful")
async def unmark_review_helpful(request: Request, id: str) -> Wrapper[dict]:
    user_id = request.session.get("user_id")
    if not user_id:
        return ApiException(
            401, 2500, "You must be logged in to unmark the review as helpful."
        )
    try:
        await HelpfulVotes(review_id=id, user_id=user_id).delete()
        helpful_in_review = await Reviews.filter(review_id=id)
        helpful_in_review.helpful_votes = helpful_in_review.helpful_votes - 1
        helpful_in_review.save()
    except OperationalError:
        return ApiException(401, 2501, "An exception occurred")
    return wrap({})


@router.delete("/review/{id}/funny")
async def unmark_review_funny(request: Request, id: str) -> Wrapper[dict]:
    user_id = request.session.get("user_id")
    if not user_id:
        return ApiException(
            401, 2500, "You must be logged in to mark the review as helpful."
        )
    try:
        await FunnyVotes(review_id=id, user_id=user_id).delete()
        funny_in_review = await Reviews.filter(id=review_id)
        funny_in_review.funny_votes = funny_in_review.funny_votes - 1
        funny_in_review.save()
    except OperationalError:
        return ApiException(401, 2501, "An exception occurred")
    return wrap({})


@router.delete("/review/{id}/spoiler")
async def unmark_review_spoiler(request: Request, id: str) -> Wrapper[dict]:
    user_id = request.session.get("user_id")
    if not user_id:
        return ApiException(
            401, 2500, "You must be logged in to mark the review as helpful."
        )
    try:
        await SpoilerVotes(review_id=id, user_id=user_id).save()
        spoiler_in_review = await Reviews.filter(review_id=id)
        spoiler_in_review.spoiler_votes = spoiler_in_review.spoiler_votes - 1
        if spoiler_in_review.spoiler_votes > 9:
            spoiler_in_review.contain_spoiler = 1
        spoiler_in_review.save()
    except OperationalError:
        return ApiException(401, 2501, "An exception occurred")
    return wrap({})