from app.models.db.banlists import Banlists
from app.models.db.ratings import Ratings
from app.models.db.reviews import Reviews


async def calc_average_rating(
    cumulative_rating, num_votes, user_id=None, movie_id=None
) -> float:
    if (user_id is not None) and (movie_id is not None):
        ban_list = await Banlists.filter(user_id=user_id, delete_date=None).values(
            "banned_user_id"
        )
        exclude_list = []
        for item in ban_list:
            exclude_list.append(str(item["banned_user_id"]))

        exclude_rating = await Ratings.filter(
            movie_id=movie_id, user_id__in=exclude_list, delete_date=None
        ).values("rating")
        num_votes = num_votes - len(exclude_rating)
        for item in exclude_rating:
            cumulative_rating = cumulative_rating - item["rating"]

    average_rating = round(cumulative_rating / num_votes if num_votes > 0 else 0.0, 1)
    rating = dict()
    rating["average_rating"] = average_rating
    rating["num_votes"] = num_votes
    rating["cumulative_rating"] = cumulative_rating
    return rating


__all__ = ["calc_average_rating"]
