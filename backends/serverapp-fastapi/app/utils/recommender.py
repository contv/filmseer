import io
import os
import pickle
import random
from collections import defaultdict
from typing import Set

import pandas as pd
import psycopg2
from surprise import (
    SVD,
    BaselineOnly,
    Dataset,
    KNNBaseline,
    Reader,
    dump,
    get_dataset_dir,
)
from surprise.model_selection import cross_validate


def get_rating_data():
    try:
        connection = psycopg2.connect(
            user="postgres",
            password="mysecret",
            host="127.0.0.1",
            port="2345",
            database="filmseer",
        )
        cursor = connection.cursor()
        # print ( connection.get_dsn_parameters(),"\n")
        cursor.execute("SELECT version();")
        record = cursor.fetchone()
        print("You are connected to - ", record, "\n")
        cursor.execute(
            """
                       SELECT distinct(movie_id) FROM public.movies WHERE movie_id IS NOT NULL
                       """
        )
        movie_set = set(item[0] for item in cursor.fetchall())
        with open("movie_set", "wb") as file:
            pickle.dump(movie_set, file, protocol=pickle.HIGHEST_PROTOCOL)
        cursor.execute(
            """
                        SELECT user_id, movie_id, rating FROM public.ratings 
                        WHERE rating IS NOT NULL
                       """
        )
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=["user_id", "movie_id", "rating"])
        return df
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)


def train():
    df = get_rating_data()
    reader = Reader(rating_scale=(0, 5))
    data = Dataset.load_from_df(df[["user_id", "movie_id", "rating"]], reader)

    trainset = data.build_full_trainset()

    # Save inner id dicts
    with open("./raw_to_inner_id", "wb") as file:
        pickle.dump(
            trainset._raw2inner_id_items, file, protocol=pickle.HIGHEST_PROTOCOL
        )
    with open("./inner_to_raw_id", "wb") as file:
        pickle.dump(
            {inner: raw for raw, inner in trainset._raw2inner_id_items.items()},
            file,
            protocol=pickle.HIGHEST_PROTOCOL,
        )

    # Train kNN recommender for getting movies similar to a given movie
    sim_options = {"name": "pearson_baseline", "user_based": False}
    algo = KNNBaseline(sim_options=sim_options)
    algo.fit(trainset)
    file_name = "./movie_movie_recommender"
    dump.dump(file_name, algo=algo)
    print("Saved kNN model")

    # Train SVD recommender for getting movies that a given user is predicted to rate highly
    algo2 = SVD()
    algo2.fit(trainset)
    file_name = "./user_movie_recommender"
    dump.dump(file_name, algo=algo2)
    print("Saved SVD model")


async def get_top_n(predictions, n=10):
    # Extract movie_id and predicted rating
    top_n = []
    for uid, iid, true_r, est, _ in predictions:
        top_n.append((iid, est))

    # Then sort the predictions and retrieve the top k
    top_n = sorted(top_n, key=lambda x: x[1], reverse=True)
    return [movie[0] for movie in top_n[0:n]]


async def predict_on_movie(movie_id: str, size: int = 10):
    _, algo = dump.load("app/utils/movie_movie_recommender")
    if not algo:
        raise TypeError("Could not find model")

    # Load id converter
    with open("app/utils/raw_to_inner_id", "rb") as file:
        raw_to_inner = pickle.load(file)
    with open("app/utils/inner_to_raw_id", "rb") as file:
        inner_to_raw = pickle.load(file)

    if not raw_to_inner or not inner_to_raw:
        raise TypeError("Could not find an id converter")

    try:
        inner_id = raw_to_inner[movie_id]
    except KeyError:
        # This movie hasn't been rated before; return a random movie's nearest neighbours
        inner_id = random.choice(list(inner_to_raw))

    prediction = algo.get_neighbors(inner_id, size)
    return [inner_to_raw[movie_id] for movie_id in prediction]


async def predict_on_user(user_id: str, movie_ids: Set[str], size: int):
    _, algo = dump.load("app/utils/user_movie_recommender")
    if not algo:
        raise TypeError("Could not find model")

    predictions = []
    for movie_id in movie_ids:
        predictions.append(algo.predict(user_id, movie_id))

    top_n = await get_top_n(predictions, size)
    return top_n


async def load_movie_set():
    with open("app/utils/movie_set", "rb") as file:
        movie_set = pickle.load(file)
    return movie_set


if __name__ == "__main__":
    train()
