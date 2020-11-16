import { view } from "@risingstack/react-easy-state";
import React from "react";
import { CheckSquare, Edit, UserX, XCircle } from "react-feather";
import { Link, useParams } from "react-router-dom";
import MovieItem from "src/app/components/movie-item";
import Pagination from "src/app/components/pagination";
import { PaginationHandle } from "src/app/components/pagination/pagination";
import Review from "src/app/components/review";
import { ReviewProps } from "src/app/components/review/review";
import TileList from "src/app/components/tile-list";
import userIcon from "src/app/components/user-menu/user-icon.svg";
import VerticalList from "src/app/components/vertical-list";
import { api, apiEffect, baseApiUrl, notify, useUpdateEffect } from "src/utils";
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
  cumulativeRating: number;
  numVotes: number;
};

type BanlistItem = {
  banlistId: string;
  bannedUserId: string;
  bannedUsername: string;
  bannedUserImage?: string;
};

type BlockedResponse = {
  banned: boolean;
};

const UserPage = (props: { className?: string }) => {
  const { username } = useParams<{ username?: string }>();
  const [user, setUser] = React.useState<User>();
  const [wishlist, setWishlist] = React.useState<WishlistItem[]>([]);
  const [banlist, setBanlist] = React.useState<BanlistItem[]>([]);
  const [reviews, setReviews] = React.useState<ReviewProps[]>([]);
  const wishlistPerPage = 6;
  const banlistPerPage = 6;
  const reviewsPerPage = 4;
  const [existing, setExisting] = React.useState(true);
  const [isEditingBio, setIsEditingBio] = React.useState(false);
  const isMe = !username;
  const bioRef = React.useRef<HTMLInputElement>(null);
  const [isBanned, setIsBanned] = React.useState(false);
  let reviewHandle: PaginationHandle;
  let wishlistHandle: PaginationHandle;
  let banlistHandle: PaginationHandle;

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
    [props.className, username]
  );

  React.useEffect(
    apiEffect(
      {
        path: `/banlist/${username}`,
        method: "GET",
      },
      (response) => {
        setIsBanned(!!(response.data as BlockedResponse).banned);
      },
      (error) => {
        setIsBanned(false);
        console.warn(error);
      },
      () => {
        return !isMe;
      }
    ),
    [props.className, username]
  );

  useUpdateEffect(() => {
    reviewHandle?.refresh(1);
    wishlistHandle?.refresh(1);
    banlistHandle?.refresh(1);
  }, [props.className, username]);

  const blockUserCallback = (username: string) => {
    return (event: React.MouseEvent) => {
      event.stopPropagation();
      event.preventDefault();
      event.nativeEvent.stopImmediatePropagation();
      event.nativeEvent.preventDefault();
      if (username === "") {
        return;
      }
      api({
        path: `/banlist/${username}`,
        method: isBanned ? "DELETE" : "POST",
      })
        .then(() => {
          api({
            path: `/banlist/${username}`,
            method: "GET",
          }).then((response) => {
            setIsBanned(!!(response.data as BlockedResponse).banned);
          });
        })
        .catch(() => {
          notify(
            "Unable to remove your comment, please try again later.",
            "error"
          );
        });
    };
  };

  const removeReviewCallback = (reviewId: string) => {
    return (event: React.MouseEvent) => {
      event.stopPropagation();
      event.preventDefault();
      event.nativeEvent.stopImmediatePropagation();
      event.nativeEvent.preventDefault();
      if (reviewId === "") {
        return;
      }
      api({
        path: `/review/${reviewId}`,
        method: "DELETE",
      })
        .then(() => {
          reviewHandle?.refresh(
            reviewHandle.countItemsOnPage() > 1
              ? reviewHandle.getPageNumber()
              : Math.max(1, reviewHandle.getPageNumber() - 1)
          );
        })
        .catch(() => {
          notify(
            "Unable to remove your comment, please try again later.",
            "error"
          );
        });
    };
  };

  const removeWishlistCallback = (wishlistId: string) => {
    return (event: React.MouseEvent) => {
      event.stopPropagation();
      event.preventDefault();
      event.nativeEvent.stopImmediatePropagation();
      event.nativeEvent.preventDefault();
      if (wishlistId === "") {
        return;
      }
      api({
        path: `/wishlist/${wishlistId}`,
        method: "DELETE",
      })
        .then(() => {
          wishlistHandle?.refresh(
            wishlistHandle.countItemsOnPage() > 1
              ? wishlistHandle.getPageNumber()
              : Math.max(1, wishlistHandle.getPageNumber() - 1)
          );
        })
        .catch(() => {
          notify(
            "Unable to remove from your wishlist, please try again later.",
            "error"
          );
        });
    };
  };

  const removeBanlistCallback = (username: string) => {
    return (event: React.MouseEvent) => {
      event.stopPropagation();
      event.preventDefault();
      event.nativeEvent.stopImmediatePropagation();
      event.nativeEvent.preventDefault();
      api({
        path: `/banlist/${username}`,
        method: "DELETE",
      })
        .then(() => {
          banlistHandle?.refresh(
            banlistHandle.countItemsOnPage() > 1
              ? banlistHandle.getPageNumber()
              : Math.max(1, banlistHandle.getPageNumber() - 1)
          );
        })
        .catch(() => {
          notify(
            "Unable to remove from your banlist, please try again later.",
            "error"
          );
        });
    };
  };

  const refresh = () => {
    api({
      path: "/user" + (username ? "/" + username : ""),
      method: "GET",
    }).then((response) => {
      setUser(response.data as User);
    });
  };

  const changeAvatar = (event: React.MouseEvent) => {
    event.stopPropagation();
    event.preventDefault();
    event.nativeEvent.stopImmediatePropagation();
    event.nativeEvent.preventDefault();
    let input = document.createElement("input");
    input.type = "file";
    input.onchange = (_event: Event) => {
      const file = (input.files || [])[0];
      if (!file) {
        notify("Please select an image to upload.", "info");
      } else if (!["image/jpeg", "image/png"].includes(file.type)) {
        notify("You need to select a valid JPG or PNG image.", "error");
      } else if (file.size >= 1024 * 300) {
        notify("The image need to be less than 300 KB.", "error");
      } else {
        let reader = new FileReader();

        reader.onloadend = function () {
          if (reader.result === null) {
            notify("Unable to read the file", "error");
            return;
          }
          let b64 = (reader.result as string).replace(/^data:.+;base64,/, "");
          api({
            path: "/user",
            method: "PUT",
            body: {
              image: b64,
            },
          })
            .then(() => {
              refresh();
            })
            .catch(() => {
              notify(
                "Unable to upload image, please try again later.",
                "error"
              );
            });
        };

        reader.readAsDataURL(file);
      }
    };
    input.click();
  };

  const clickBioEdit = (event: React.MouseEvent) => {
    event.stopPropagation();
    event.preventDefault();
    event.nativeEvent.stopImmediatePropagation();
    event.nativeEvent.preventDefault();
    if (isEditingBio) {
      if (bioRef.current) {
        api({
          path: "/user",
          method: "PUT",
          body: {
            description: (bioRef.current.value || "").trim(),
          },
        })
          .then(() => {
            setIsEditingBio(false);
            refresh();
          })
          .catch(() => {
            notify(
              "Unable to update your bio, please try again later.",
              "error"
            );
          });
      }
    } else {
      setIsEditingBio(true);
    }
  };

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
            <div className="UserPage__edit" onClick={changeAvatar}>
              <Edit size={18} />
            </div>
          )}
          <img
            src={
              user.image
                ? baseApiUrl + user.image + "?" + Date.now().toString()
                : userIcon
            }
            alt="Avatar"
            className="UserPage__avatar-image"
          />
        </div>
        <div className="UserPage__brief-info">
          <div className="UserPage__username">{user.username}</div>
          <div className="UserPage__bio">
            {isEditingBio ? (
              <input type="text" className="UserPage__bio-edit" ref={bioRef} />
            ) : (user.description || "").trim().length > 0 ? (
              <div className="UserPage__bio-content">{user.description}</div>
            ) : (
              isMe && (
                <div className="UserPage__bio-content UserPage__bio-content--empty">
                  Your bio is empty.
                </div>
              )
            )}
            {isMe && (
              <div className="UserPage__edit" onClick={clickBioEdit}>
                {isEditingBio ? <CheckSquare size={22} /> : <Edit size={22} />}
              </div>
            )}
          </div>
        </div>
        {!isMe && (
          <div className="UserPage__operations">
            <button
              className="UserPage__button"
              onClick={blockUserCallback(username || "")}
            >
              <div className="UserPage__button-icon">
                <UserX size={22} style={{ verticalAlign: "middle" }} />
              </div>
              <div className="UserPage__button-text">
                {isBanned ? "Blocked" : "Block"}
              </div>
            </button>
          </div>
        )}
      </div>
      <div className="UserPage__section">
        <div className="UserPage__section-title">Reviews</div>
        <VerticalList
          className="UserPage__reviews-list"
          items={reviews.map((review) => {
            return (
              <div
                className="UserPage__review-wrapper"
                key={`${review.reviewId}`}
              >
                {isMe && (
                  <div
                    className="UserPage__remove-item"
                    onClick={removeReviewCallback(review.reviewId)}
                  >
                    <XCircle size={22} />
                  </div>
                )}
                <Review
                  className="UserPage__review"
                  hideFlags={true}
                  showMovie={true}
                  {...review}
                />
              </div>
            );
          })}
        />
        <div className="UserPage__pagination-wrapper">
          <Pagination
            ref={(c) => {
              reviewHandle = c;
            }}
            displayType="numbered"
            dataType="slice"
            perPage={reviewsPerPage}
            dataCallback={async () => {
              const response = await api({
                path: !isMe ? `/user/${username}/reviews` : "/reviews",
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
        </div>
        <TileList
          className="UserPage__wishlist"
          items={wishlist.map((wishlistItem) => {
            return (
              <div
                className="UserPage__wishlist-item-wrapper"
                key={`${wishlistItem.wishlistId}`}
              >
                {isMe && (
                  <div
                    className="UserPage__remove-item"
                    onClick={removeWishlistCallback(wishlistItem.movieId)}
                  >
                    <XCircle size={22} />
                  </div>
                )}
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
            ref={(c) => {
              wishlistHandle = c;
            }}
            displayType="numbered"
            dataType="slice"
            perPage={wishlistPerPage}
            dataCallback={async () => {
              const response = await api({
                path: !isMe ? `/user/${username}/wishlist` : "/wishlist",
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
      <div className="UserPage__section">
        <div className="UserPage__section-title">
          <span>Banlist</span>
        </div>
        <TileList
          className="UserPage__banlist"
          items={banlist.map((banlistItem) => {
            return (
              <div
                className="UserPage__banlist-item-wrapper"
                key={`${banlistItem.banlistId}`}
              >
                {isMe && (
                  <div
                    className="UserPage__remove-item"
                    onClick={removeBanlistCallback(banlistItem.bannedUsername)}
                  >
                    <XCircle size={22} />
                  </div>
                )}
                <Link
                  className="UserPage__banlist-item"
                  to={`/user/${banlistItem.bannedUsername}`}
                >
                  <div className="UserPage__banlist-avatar">
                    <img
                      src={
                        banlistItem.bannedUserImage
                          ? baseApiUrl +
                            banlistItem.bannedUserImage +
                            "?" +
                            Date.now().toString()
                          : userIcon
                      }
                      alt="Avatar"
                      className="UserPage__banlist-avatar-image"
                    />
                  </div>
                  <div className="UserPage__banlist-username">
                    {banlistItem.bannedUsername}
                  </div>
                </Link>
              </div>
            );
          })}
        />
        <div className="UserPage__pagination-wrapper">
          <Pagination
            ref={(c) => {
              banlistHandle = c;
            }}
            displayType="numbered"
            dataType="slice"
            perPage={banlistPerPage}
            dataCallback={async () => {
              const response = await api({
                path: !isMe ? `/user/${username}/banlist` : "/banlist",
                method: "GET",
              });
              return response.data.items as BanlistItem[];
            }}
            renderCallback={(data) => {
              setBanlist(data as BanlistItem[]);
            }}
          />
        </div>
      </div>
    </div>
  );
};

export default view(UserPage);
