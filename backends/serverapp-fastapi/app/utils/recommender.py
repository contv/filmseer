import asyncio
import pickle
import random
from typing import Set

import asyncpg
from surprise import SVD, KNNBaseline, Reader, dump

from app.core.config import settings

# Import models and dicts globally
_, movie_movie_recommender = dump.load(
    settings.STORAGES_ROOT / "recommender/movie_movie_recommender"
)
_, user_movie_recommender = dump.load(
    settings.STORAGES_ROOT / "recommender/user_movie_recommender"
)
with open(settings.STORAGES_ROOT / "recommender/raw_to_inner_id", "rb") as file:
    raw_to_inner = pickle.load(file)
with open(settings.STORAGES_ROOT / "recommender/inner_to_raw_id", "rb") as file:
    inner_to_raw = pickle.load(file)
with open(settings.STORAGES_ROOT / "recommender/movie_set", "rb") as file:
    movie_set = pickle.load(file)


async def predict_on_movie(movie_id: str, size: int = 10):
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
            with open(
                settings.STORAGES_ROOT / "recommender/raw_to_inner_id", "rb"
            ) as file:
                raw_to_inner = pickle.load(file)
        except FileNotFoundError:
            raise TypeError("Could not find raw_to_inner_id")
    if not inner_to_raw:
        try:
            with open(
                settings.STORAGES_ROOT / "recommender/inner_to_raw_id", "rb"
            ) as file:
                inner_to_raw = pickle.load(file)
        except FileNotFoundError:
            raise TypeError("Could not find inner_to_raw_id")

    try:
        inner_id = raw_to_inner[movie_id]
    except KeyError:
        # This movie hasn't been rated before; return a random movie's nearest neighbours
        inner_id = random.choice(list(inner_to_raw))

    prediction = movie_movie_recommender.get_neighbors(inner_id, size)
    return [inner_to_raw[movie_id] for movie_id in prediction]


async def predict_on_user(user_id: str, movie_ids: Set[str], size: int):
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
    return [movie[0] for movie in top_n[0:n]]


async def load_movie_set():
    global movie_set
    if not movie_set:
        try:
            with open(settings.STORAGES_ROOT / "recommender/movie_set", "rb") as file:
                movie_set = pickle.load(file)
        except FileNotFoundError:
            raise TypeError("Could not find movie set")
    return movie_set
