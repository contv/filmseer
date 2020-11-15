import "./user.scss";

import { Edit, Flag, MoreHorizontal, UserPlus, UserX } from "react-feather";
import { api, apiEffect } from "src/utils";

import MovieItem from "src/app/components/movie-item";
import Pagination from "src/app/components/pagination";
import React from "react";
import Review from "src/app/components/review";
import { ReviewProps } from "src/app/components/review/review";
import TileList from "src/app/components/tile-list";
import VerticalList from "src/app/components/vertical-list";
import { useParams } from "react-router-dom";
import userIcon from "src/app/components/user-menu/user-icon.svg";
import { view } from "@risingstack/react-easy-state";
import { baseApiUrl } from "src/utils";

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
  cumulativeRating: number;
  numVotes: number;
};

const UserPage = (props: { className?: string }) => {
  const { username } = useParams<{ username?: string }>();
  const [user, setUser] = React.useState<User>();
  const [wishlist, setWishlist] = React.useState<WishlistItem[]>([]);
  const [reviews, setReviews] = React.useState<ReviewProps[]>([]);
  const wishlistPerPage = 6;
  const reviewsPerPage = 4;
  const [existing, setExisting] = React.useState(true);
  const isMe = !username;

  React.useEffect(
    apiEffect(
      {
        path: "/user" + (username ? "/" + username : ""),
        method: "GET",
      },
      (response) => {
        setUser(response.data as User);
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
      return <div className="UserPage__loading-message">Loading...</div>;
    } else {
      return <div className="UserPage__loading-message">No such user</div>;
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
            src={user.image ? (baseApiUrl + user.image) : userIcon}
            alt="Avatar"
            className="UserPage__avatar-image"
          />
        </div>
        <div className="UserPage__brief-info">
          <div className="UserPage__username">{user.username}</div>
          <div className="UserPage__bio">
            <div className="UserPage__bio-content">{user.description}</div>
            {isMe && (
              <div className="UserPage__edit">
                <Edit size={18} />
              </div>
            )}
          </div>
        </div>
        {!isMe && (
          <div className="UserPage__operations">
            <button className="UserPage__follow-button">
              <UserPlus size={28} /> Follow
            </button>
            <div className="UserPage__more-operations">
              <button className="UserPage__more-operation-button">
                <MoreHorizontal size={28} />
              </button>
              <div className="UserPage__more-operation-dropdown">
                <button className="UserPage__report-user-button UserPage__dropdown-button">
                  <Flag size={22} /> Report
                </button>
                <button className="UserPage__block-user-button UserPage__dropdown-button">
                  <UserX size={22} /> Block
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
      <div className="UserPage__section">
        <div className="UserPage__section-title">Reviews</div>
        <VerticalList
          className="UserPage__reviews-list"
          items={reviews.map((review) => {
            return (
              <Review
                className="UserPage__review"
                hideFlags={true}
                {...review}
              />
            );
          })}
        />
        <div className="UserPage__pagination-wrapper">
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
              <div className="UserPage__wishlist-item-wrapper">
                <MovieItem
                  className="UserPage__movie-item"
                  movieId={wishlistItem.movieId}
                  title={wishlistItem.title}
                  year={parseInt(wishlistItem.releaseYear, 10)}
                  genres={[]}
                  imageUrl={wishlistItem.imageUrl}
                  cumulativeRating={wishlistItem.cumulativeRating}
                  numRatings={wishlistItem.numVotes}
                  numReviews={0}
                />
              </div>
            );
          })}
        />
        <div className="UserPage__pagination-wrapper">
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
    </div>
  );
};

export default view(UserPage);
