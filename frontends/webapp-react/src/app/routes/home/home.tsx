import { view } from "@risingstack/react-easy-state";
import React from "react";
import MovieItem from "src/app/components/movie-item/movie-item";
import movieLogo from "src/app/components/movie-item/movie-logo.png";
import Pagination from "src/app/components/pagination";
import TileList from "src/app/components/tile-list";
import { SearchItem } from "src/app/routes/search/search";
import state from "src/app/states";
import { api } from "src/utils";
import "./home.scss";

const HomePage = (props: { className?: string }) => {
  const [moviesForYou, setMoviesForYou] = React.useState<SearchItem[]>([]);
  const [moviesNew, setMoviesNew] = React.useState<SearchItem[]>([]);
  const [moviesPopular, setMoviesPopular] = React.useState<SearchItem[]>([]);
  const [isLoadingForYou, setIsLoadingForYou] = React.useState<boolean>(true);
  const [isLoadingNew, setIsLoadingNew] = React.useState<boolean>(true);
  const [isLoadingPopular, setIsLoadingPopular] = React.useState<boolean>(true);
  const [hasErrorForYou, setHasErrorForYou] = React.useState<boolean>(false);
  const [hasErrorNew, setHasErrorNew] = React.useState<boolean>(false);
  const [hasErrorPopular, setHasErrorPopular] = React.useState<boolean>(false);
  const total = 50;

  // This is an UGLY approach, but a CSS reader is even worse
  // UPDATE THIS WHEN YOU MODIFY SCSS
  // const perPage = (
  //   CONTAINER_MAX_WIDTH + GRID_GAP
  // ) / (ITEM_MAX_WIDTH + GRID_GAP) * NUMBER_OF_ROWS
  const itemPerRow = Math.floor(
    (document.body.clientWidth * 0.8 + 24) / (150 + 24)
  );

  return (
    <div className={`HomePage ${(props.className || "").trim()}`}>
      {state.loggedIn && (
        <section className="HomePage__section">
          <div className="HomePage__section-title">Recommended for you</div>
          <div className="HomePage__section-content">
            {isLoadingForYou || hasErrorForYou ? (
              isLoadingForYou ? (
                <div className="HomePage__loading-messages">
                  Fetching suggestions...
                </div>
              ) : (
                <div className="HomePage__loading-messages">
                  An error occurred, please try again.
                </div>
              )
            ) : moviesForYou ? (
              <TileList
                className="HomePage__list"
                itemClassName="HomePage__item"
                items={moviesForYou.map((movie) => (
                  <MovieItem
                    movieId={movie.id}
                    year={movie.releaseYear}
                    title={movie.title}
                    genres={movie.genres.map((g) => ({
                      id: `${g}-${movie.id}`,
                      text: g,
                    }))}
                    imageUrl={movie.imageUrl || movieLogo}
                    cumulativeRating={movie.cumulativeRating}
                    numRatings={movie.numVotes}
                    numReviews={0}
                  />
                ))}
              />
            ) : (
              <div className="HomePage__loading-messages">
                Sorry, we couldn't find any suggestions.
              </div>
            )}
          </div>

          <div className="HomePage__pagination-wrapper">
            <Pagination
              className={
                `HomePage__pagination` +
                (isLoadingForYou || hasErrorForYou
                  ? "HomePage__pagination--hidden"
                  : "")
              }
              displayType="dotted"
              dataType="slice"
              dataCallback={async () => {
                setIsLoadingForYou(true);
                let res;
                try {
                  res = await api({
                    path: "/movies/recommendation",
                    method: "GET",
                    params: {
                      type: "foryou",
                      size: total,
                      per_page: total,
                      page: 1,
                      sort: "rating",
                      desc: true,
                    },
                  });
                } catch (e) {
                  setIsLoadingForYou(false);
                  setHasErrorForYou(true);
                  return [];
                }
                setIsLoadingForYou(false);
                if (res.code !== 0) {
                  setHasErrorForYou(true);
                  return [];
                } else {
                  setHasErrorForYou(false);
                  return res.data.movies;
                }
              }}
              renderCallback={(data) => {
                setMoviesForYou(data as SearchItem[]);
              }}
              perPage={itemPerRow * 2}
            />
          </div>
        </section>
      )}
      <section className="HomePage__section">
        <div className="HomePage__section-title">What's New</div>
        <div className="HomePage__section-content">
          {isLoadingNew || hasErrorNew ? (
            isLoadingNew ? (
              <div className="HomePage__loading-messages">
                Fetching suggestions...
              </div>
            ) : (
              <div className="HomePage__loading-messages">
                An error occurred, please try again.
              </div>
            )
          ) : moviesNew ? (
            <TileList
              className="HomePage__list"
              itemClassName="HomePage__item"
              items={moviesNew.map((movie) => (
                <MovieItem
                  movieId={movie.id}
                  year={movie.releaseYear}
                  title={movie.title}
                  genres={movie.genres.map((g) => ({
                    id: `${g}-${movie.id}`,
                    text: g,
                  }))}
                  imageUrl={movie.imageUrl || movieLogo}
                  cumulativeRating={movie.cumulativeRating}
                  numRatings={movie.numVotes}
                  numReviews={0}
                />
              ))}
            />
          ) : (
            <div className="HomePage__loading-messages">
              Sorry, we couldn't find anything new.
            </div>
          )}
        </div>
        <div className="HomePage__pagination-wrapper">
          <Pagination
            className={
              `HomePage__pagination` +
              (isLoadingNew || hasErrorNew
                ? "HomePage__pagination--hidden"
                : "")
            }
            displayType="dotted"
            dataType="slice"
            dataCallback={async () => {
              setIsLoadingNew(true);
              let res;
              try {
                res = await api({
                  path: "/movies/recommendation",
                  method: "GET",
                  params: {
                    type: "new",
                    size: total,
                    per_page: total,
                    page: 1,
                    sort: "rating",
                    desc: true,
                  },
                });
              } catch (e) {
                setIsLoadingNew(false);
                setHasErrorNew(true);
                return [];
              }
              setIsLoadingNew(false);
              if (res.code !== 0) {
                setHasErrorNew(true);
                return [];
              } else {
                setHasErrorNew(false);
                return res.data.movies;
              }
            }}
            renderCallback={(data) => {
              setMoviesNew(data as SearchItem[]);
            }}
            perPage={itemPerRow * 2}
          />
        </div>
      </section>
      {!state.loggedIn && (
        <section className="HomePage__section">
          <div className="HomePage__section-title">Popular</div>
          <div className="HomePage__section-content">
            {isLoadingPopular || hasErrorPopular ? (
              isLoadingPopular ? (
                <div className="HomePage__loading-messages">
                  Fetching suggestions...
                </div>
              ) : (
                <div className="HomePage__loading-messages">
                  An error occurred, please try again.
                </div>
              )
            ) : moviesPopular ? (
              <TileList
                className="HomePage__list"
                itemClassName="HomePage__item"
                items={moviesPopular.map((movie) => (
                  <MovieItem
                    movieId={movie.id}
                    year={movie.releaseYear}
                    title={movie.title}
                    genres={movie.genres.map((g) => ({
                      id: `${g}-${movie.id}`,
                      text: g,
                    }))}
                    imageUrl={movie.imageUrl || movieLogo}
                    cumulativeRating={movie.cumulativeRating}
                    numRatings={movie.numVotes}
                    numReviews={0}
                  />
                ))}
              />
            ) : (
              <div className="HomePage__loading-messages">
                Sorry, we couldn't find anything new.
              </div>
            )}
          </div>
          <div className="HomePage__pagination-wrapper">
            <Pagination
              className={
                `HomePage__pagination` +
                (isLoadingPopular || hasErrorPopular
                  ? "HomePage__pagination--hidden"
                  : "")
              }
              displayType="dotted"
              dataType="slice"
              dataCallback={async () => {
                setIsLoadingPopular(true);
                let res;
                try {
                  res = await api({
                    path: "/movies/recommendation",
                    method: "GET",
                    params: {
                      type: "popular",
                      size: total,
                      per_page: total,
                      page: 1,
                      sort: "rating",
                      desc: true,
                    },
                  });
                } catch (e) {
                  setIsLoadingPopular(false);
                  setHasErrorPopular(true);
                  return [];
                }
                setIsLoadingPopular(false);
                if (res.code !== 0) {
                  setHasErrorPopular(true);
                  return [];
                } else {
                  setHasErrorPopular(false);
                  return res.data.movies;
                }
              }}
              renderCallback={(data) => {
                setMoviesPopular(data as SearchItem[]);
              }}
              perPage={itemPerRow * 2}
            />
          </div>
        </section>
      )}
    </div>
  );
};

export default view(HomePage);
