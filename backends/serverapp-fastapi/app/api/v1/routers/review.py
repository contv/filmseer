from fastapi import APIRouter, Request
from tortoise.exceptions import OperationalError
from tortoise.transactions import atomic, in_transaction

from app.models.db.helpful_votes import HelpfulVotes
from app.models.db.funny_votes import FunnyVotes
from app.models.db.spoiler_votes import SpoilerVotes
from app.models.db.reviews import Reviews

from app.utils.wrapper import ApiException, Wrapper, wrap

router = APIRouter()
override_prefix = None
override_prefix_all = None


@router.post("/{id}/helpful")
async def mark_review_helpful(request: Request, id: str) -> Wrapper[dict]:
    user_id = request.session.get("user_id")
    if not user_id:
        return ApiException(
            401, 2500, "You must be logged in to mark the review as spoiler."
        )
    try:
        async with in_transaction():
            await HelpfulVotes(review_id=id, user_id=user_id).get_or_create()
            # PENDING Update helpful vote count in Reviews?
    except OperationalError:
        return ApiException(401, 2501, "An exception occurred")
    return wrap({})


@router.post("/{id}/funny")
async def mark_review_funny(request: Request, id: str) -> Wrapper[dict]:
    user_id = request.session.get("user_id")
    if not user_id:
        return ApiException(
            401, 2500, "You must be logged in to mark the review as spoiler."
        )
    try:
        async with in_transaction():
            await FunnyVotes(review_id=id, user_id=user_id).get_or_create()
            # PENDING Update funny vote count in Reviews?
    except OperationalError:
        return ApiException(401, 2501, "An exception occurred")
    return wrap({})


@router.post("/{id}/spoiler")
async def mark_review_spoiler(request: Request, id: str) -> Wrapper[dict]:
    user_id = request.session.get("user_id")
    if not user_id:
        return ApiException(
            401, 2500, "You must be logged in to mark the review as spoiler."
        )
    try:
        async with in_transaction():
            await SpoilerVotes(review_id=id, user_id=user_id).get_or_create()
            count_spoiler = await SpoilerVotes.filter(review_id=id).count()
            if count_spoiler >= 10:
                await Reviews.filter(review_id=id).update(contains_spoiler=True)
            else:
                await Reviews.filter(review_id=id).update(contains_spoiler=False)
            # PENDING Update spoiler vote count in Reviews?
    except OperationalError:
        return ApiException(401, 2501, "An exception occurred")
    return wrap({})


@router.delete("/{id}/helpful")
async def unmark_review_helpful(request: Request, id: str) -> Wrapper[dict]:
    user_id = request.session.get("user_id")
    if not user_id:
        return ApiException(
            401, 2500, "You must be logged in to mark the review as spoiler."
        )
    try:
        async with in_transaction():
            await HelpfulVotes.filter(review_id=id, user_id=user_id).delete()
            # PENDING Update helpful vote count in Reviews?
    except OperationalError:
        return ApiException(401, 2501, "An exception occurred")
    return wrap({})


@router.delete("/{id}/funny")
async def unmark_review_funny(request: Request, id: str) -> Wrapper[dict]:
    user_id = request.session.get("user_id")
    if not user_id:
        return ApiException(
            401, 2500, "You must be logged in to mark the review as spoiler."
        )
    try:
        async with in_transaction():
            await FunnyVotes.filter(review_id=id, user_id=user_id).delete()
            # PENDING Update funny vote count in Reviews?
    except OperationalError:
        return ApiException(401, 2501, "An exception occurred")
    return wrap({})


@router.delete("/{id}/spoiler")
async def unmark_review_spoiler(request: Request, id: str) -> Wrapper[dict]:
    user_id = request.session.get("user_id")
    if not user_id:
        return ApiException(
            401, 2500, "You must be logged in to mark the review as spoiler."
        )
    try:
        async with in_transaction():
            await SpoilerVotes.filter(review_id=id, user_id=user_id).delete()
            count_spoiler = await SpoilerVotes.filter(review_id=id).count()
            if count_spoiler >= 10:
                await Reviews.filter(review_id=id).update(contains_spoiler=True)
            else:
                await Reviews.filter(review_id=id).update(contains_spoiler=False)
    except OperationalError:
        return ApiException(401, 2501, "An exception occurred")
    return wrap({})
