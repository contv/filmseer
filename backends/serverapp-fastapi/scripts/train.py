import asyncio
import pickle

import asyncpg
import pandas as pd
from surprise import SVD, Dataset, KNNBaseline, Reader, dump

from app.core.config import settings

"""
model training script to serialise models for recommendation enginge.
"""

async def get_rating_data():
    conn = await asyncpg.connect(
        user="postgres",
        password="mysecret",
        host="127.0.0.1",
        port="2345",
        database="filmseer",
    )
    async with conn.transaction():
        movies = await conn.fetch(
            """
            SELECT distinct(movie_id) FROM public.movies WHERE movie_id IS NOT NULL
            """
        )
        movie_set = set(item[0] for item in movies)
        with open(settings.STORAGES_ROOT / "recommender/movie_set", "wb") as file:
            pickle.dump(movie_set, file, protocol=pickle.HIGHEST_PROTOCOL)
        ratings = await conn.fetch(
            """
            SELECT user_id::text, movie_id::text, rating FROM public.ratings
            WHERE rating IS NOT NULL
            """
        )
        df = pd.DataFrame(ratings, columns=["user_id", "movie_id", "rating"])
        return df


async def train():
    df = await get_rating_data()
    reader = Reader(rating_scale=(0, 5))
    data = Dataset.load_from_df(df[["user_id", "movie_id", "rating"]], reader)
    trainset = data.build_full_trainset()

    # Save inner id dicts

    with open(settings.STORAGES_ROOT / "recommender/raw_to_inner_id", "wb") as file:
        pickle.dump(
            trainset._raw2inner_id_items, file, protocol=pickle.HIGHEST_PROTOCOL
        )
    with open(settings.STORAGES_ROOT / "recommender/inner_to_raw_id", "wb") as file:
        pickle.dump(
            {inner: raw for raw, inner in trainset._raw2inner_id_items.items()},
            file,
            protocol=pickle.HIGHEST_PROTOCOL,
        )

    # Train kNN recommender for getting movies similar to a given movie
    sim_options = {"name": "pearson_baseline", "user_based": False}
    algo = KNNBaseline(sim_options=sim_options)
    algo.fit(trainset)
    dump.dump(settings.STORAGES_ROOT / "recommender/movie_movie_recommender", algo=algo)
    print("Saved kNN model")

    # Train SVD recommender for getting movies that a user is predicted to rate highly
    algo2 = SVD()
    algo2.fit(trainset)
    dump.dump(settings.STORAGES_ROOT / "recommender/user_movie_recommender", algo=algo2)
    print("Saved SVD model")


def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(train())
