import pickle
import random
import asyncio
import aiofiles
from typing import Set

from surprise import dump

from app.core.config import settings

movie_set = None
user_movie_recommender = None
movie_movie_recommender = None
raw_to_inner = None
inner_to_raw = None


async def predict_on_movie(movie_id: str, size: int = 10):
    """Finds the nearest neighbours of the given movie id using kNN model

    Args:
        movie_id: string representing the movie's id
        size: int representing how many movie results to return

    Returns:
        a list of movie ids each representing a similar movie
    """

    global movie_movie_recommender
    if not movie_movie_recommender:
        try:
            _, movie_movie_recommender = dump.load(
                settings.STORAGES_ROOT / "recommender/movie_movie_recommender"
            )
        except FileNotFoundError:
            raise TypeError("Could not find model")

    # Load id converters
    global raw_to_inner
    global inner_to_raw
    if not raw_to_inner:
        try:
            async with aiofiles.open(
                settings.STORAGES_ROOT / "recommender/raw_to_inner_id", "rb"
            ) as file:
                raw_to_inner = await file.read()
                raw_to_inner = pickle.loads(raw_to_inner)
        except FileNotFoundError:
            raise TypeError("Could not find raw_to_inner_id")
    if not inner_to_raw:
        try:
            async with aiofiles.open(
                settings.STORAGES_ROOT / "recommender/inner_to_raw_id", "rb"
            ) as file:
                inner_to_raw = await file.read()
                inner_to_raw = pickle.loads(inner_to_raw)
        except FileNotFoundError:
            raise TypeError("Could not find inner_to_raw_id")

    try:
        inner_id = raw_to_inner[movie_id]
    except KeyError:
        # The movie hasn't been rated before; return a random movie's nearest neighbours
        inner_id = random.choice(list(inner_to_raw))

    prediction = movie_movie_recommender.get_neighbors(inner_id, size)
    return [inner_to_raw[movie_id] for movie_id in prediction]


async def predict_on_user(user_id: str, movie_ids: Set[str], size: int):
    """Return movies recommendations which the given user is likely to rate highly

    Args:
        user_id: a string representing the user's id
        movie_ids: a set of movie ids representing the movies the user has already watched
        size: int representing how many results to return

    Returns:
        a list of movie ids each representing a recommended movie based on rating prediction
    """

    global user_movie_recommender
    if not user_movie_recommender:
        try:
            _, user_movie_recommender = dump.load(
                settings.STORAGES_ROOT / "recommender/user_movie_recommender"
            )
        except FileNotFoundError:
            raise TypeError("Could not find model")

    predictions = []
    for movie_id in movie_ids:
        predictions.append(user_movie_recommender.predict(user_id, movie_id))

    top_n = await get_top_n(predictions, size)
    return top_n


async def get_top_n(predictions, n=10):
    # Extract movie_id and predicted rating
    top_n = []
    for uid, iid, true_r, est, _ in predictions:
        top_n.append((iid, est))

    # Then sort the predictions and retrieve the top k
    top_n = sorted(top_n, key=lambda x: x[1], reverse=True)
    return [str(movie[0]) for movie in top_n[0:n]]


async def load_movie_set():
    global movie_set
    if not movie_set:
        try:
            async with aiofiles.open(settings.STORAGES_ROOT / "recommender/movie_set", "rb") as file:
                movie_set = await file.read()
                movie_set = pickle.loads(movie_set)
        except FileNotFoundError:
            raise TypeError("Could not find movie set")
    return movie_set