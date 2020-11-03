import { view } from "@risingstack/react-easy-state";
import React from "react";
import { Edit } from "react-feather";
import { useParams } from "react-router-dom";
import MovieItem from "src/app/components/movie-item";
import Pagination from "src/app/components/pagination";
import Review from "src/app/components/review";
import { ReviewProps } from "src/app/components/review/review";
import TileList from "src/app/components/tile-list";
import VerticalList from "src/app/components/vertical-list";
import { api, apiEffect } from "src/utils";
import "./user.scss";

export type User = {
  id: string;
  username: string;
  description?: string;
  image?: string;
};

type WishlistItem = {
  wishlistId: string;
  movieId: string;
  title: string;
  releaseYear: string;
  imageUrl?: string;
  averageRating: number;
};

const UserPage = (props: { className?: string }) => {
  const { username } = useParams<{ username?: string }>();
  const [user, setUser] = React.useState<User>();
  const [wishlist, setWishlist] = React.useState<WishlistItem[]>([]);
  const [reviews, setReviews] = React.useState<ReviewProps[]>([]);
  const wishlistPerPage = 8;
  const reviewsPerPage = 8;
  const [existing, setExisting] = React.useState(true);
  const isMe = !username;

  React.useEffect(
    apiEffect(
      {
        path: "/user" + (username ? "/" + username : ""),
        method: "GET",
      },
      (response) => {
        setUser(() => (response.data as User));
      },
      (error) => {
        setExisting(false);
        console.warn(error);
      }
    ),
    []
  );

  if (!user) {
    if (existing) {
      return <div>Loading...</div>;
    } else {
      return <div>No such user</div>;
    }
  }

  return (
    <div className={`UserPage ${(props.className || "").trim()}`}>
      <div className="UserPage__info-section">
        <div className="UserPage__avatar">
          {isMe && (
            <div className="UserPage__edit">
              <Edit size={18} />
            </div>
          )}
          <img
            src={user.image}
            alt="Avatar"
            className="UserPage__avatar-image"
          />
        </div>
        <div className="UserPage__username">{user.username}</div>
        <div className="UserPage__bio">
          {isMe && (
            <div className="UserPage__edit">
              <Edit size={18} />
            </div>
          )}
          <div className="UserPage__bio-content">{user.description}</div>
        </div>
      </div>
      <div className="UserPage__section">
        <div className="UserPage__section-title">Reviews</div>
        <VerticalList
          className="UserPage__reviews-list"
          items={reviews.map((review) => {
            return <Review {...review} />;
          })}
        />
        <Pagination
          displayType="numbered"
          dataType="slice"
          perPage={reviewsPerPage}
          dataCallback={async () => {
            const response = await api({
              path: username ? `/user/${username}/reviews` : "/reviews",
              method: "GET",
            });
            return response.data.items as ReviewProps[];
          }}
          renderCallback={(data) => {
            setReviews(data as ReviewProps[]);
          }}
        />
      </div>
      <div className="UserPage__section">
        <div className="UserPage__section-title">
          <span>Wishlist</span>
          {isMe && (
            <div className="UserPage__edit">
              <Edit size={22} />
            </div>
          )}
        </div>
        <TileList
          className="UserPage__wishlist"
          items={wishlist.map((wishlistItem) => {
            return (
              <div className="UserPage_wishlist-item-wrapper">
                <MovieItem
                  movieId={wishlistItem.movieId}
                  title={wishlistItem.title}
                  year={parseInt(wishlistItem.releaseYear, 10)}
                  genres={[]}
                  imageUrl={wishlistItem.imageUrl}
                  cumulativeRating={wishlistItem.averageRating}
                  numRatings={1}
                  numReviews={0}
                />
              </div>
            );
          })}
        />
        <Pagination
          displayType="numbered"
          dataType="slice"
          perPage={wishlistPerPage}
          dataCallback={async () => {
            const response = await api({
              path: username ? `/user/${username}/wishlist` : "/wishlist",
              method: "GET",
            });
            return response.data.items as WishlistItem[];
          }}
          renderCallback={(data) => {
            setWishlist(data as WishlistItem[]);
          }}
        />
      </div>
    </div>
  );
};

export default view(UserPage);
