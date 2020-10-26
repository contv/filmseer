from fastapi import APIRouter, Request
from typing import List

from app.utils.wrapper import wrap

router = APIRouter()
override_prefix = None
override_prefix_all = None


@router.get("/")
async def get_wishlist(request: Request):
    return wrap({"items": []})


@router.get("/{movie_id}")
async def is_movie_wishlist(request: Request, movie_id: str):
    return wrap({"added": True})


@router.put("/{movie_id}")
async def add_to_wishlist(request: Request, movie_id: str):
    return wrap({})


@router.delete("/{movie_id}")
async def delete_from_wishlist(request: Request, movie_id: str):
    return wrap({})
