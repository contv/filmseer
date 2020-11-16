import "./movie.scss";

import React, { useEffect, useRef, useState } from "react";
import { api, apiEffect, useUpdateEffect } from "src/utils";

import GenreTile from "src/app/components/genre-tile";
import HorizontalList from "src/app/components/horizontal-list";
import MovieInteract from "src/app/components/movie-interact";
import MovieItem from "src/app/components/movie-item";
import MovieSection from "src/app/components/movie-section";
import Pagination from "src/app/components/pagination";
import Review from "src/app/components/review";
import ReviewEditor from "src/app/components/review-editor";
import { ReviewProps } from "src/app/components/review/review";
import { SearchItem } from "src/app/routes/search/search";
import Stars from "src/app/components/stars";
import TileList from "src/app/components/tile-list";
import Trailer from "src/app/components/trailer";
import Typography from "@material-ui/core/Typography";
import { User } from "src/app/routes/user/user";
import VerticalList from "src/app/components/vertical-list";
import avatar from "src/app/components/review/default-avatar.png";
import movieLogo from "src/app/components/movie-item/movie-logo.png";
import { nFormatter } from "src/app/components/movie-item/movie-item";
import state from "src/app/states";
import { useParams } from "react-router-dom";
import { view } from "@risingstack/react-easy-state";

type CastMember = {
  id: string;
  name: string;
  image?: string;
  position: string;
};

type Trailer = {
  site: "Vimeo" | "YouTube";
  key: string;
};

type Movie = {
  title: string;
  imageUrl: string;
  releaseYear: string;
  cumulativeRating: number;
  averageRating: number;
  numReviews: number;
  numVotes: number;
  description: string;
  trailers?: Array<Trailer>;
  crew?: Array<CastMember>;
  genres?: Array<string>;
};
const total = 16;
const itemPerRow = Math.floor(
  (document.body.clientWidth * 0.8 + 24) / (150 + 24) / 2
);

type Handle<T> = T extends React.ForwardRefExoticComponent<
  React.RefAttributes<infer T2>
>
  ? T2
  : {
      refresh: (page?: number) => void;
    } | null;


const MovieDetailPage = (props: { className?: string }) => {
  const { movieId } = useParams<{ movieId: string }>();
  const [movieDetails, setMovie] = useState<Movie>();
  const [author, setAuthor] = useState<User>();
  const [reviews, setReviews] = useState<Array<ReviewProps>>();
  const [authorReview, setAuthorReview] = useState<Array<ReviewProps>>();
  const [recommended, setRecommended] = useState<Array<SearchItem>>();
  const [hasError, setHasError] = useState<Boolean>(false);
  const [userRating, setUserRating] = useState<number>(0);
  const reviewSection: any = useRef();
  const [isLoadingRecommended, setIsLoadingRecommended] = React.useState<
    boolean
  >(true);
  const [hasErrorRecommened, setHasErrorRecommended] = React.useState<boolean>(
    false
  );

  const snapToReviews = () => reviewSection.current.scrollIntoView();
  let paginationHandle: Handle<typeof Pagination>;

  useEffect(() => {
    if (state.loggedIn) {
      api({ path: `/user`, method: "GET" }).then((res) => {
        if (res.code !== 0) {
          setHasError(true);
        } else {
          setAuthor(res.data as User);
          setHasError(false);
        }
      });
      apiEffect(
        {
          path: `/movie/${movieId}/rating`,
          method: "GET",
        },
        (res) => {
          setUserRating(res.data.rating);
        }
      )();
    }
    api({ path: `/movie/${movieId}`, method: "GET" }).then((res) => {
      if (res.code !== 0) {
        setHasError(true);
      } else {
        setMovie(res.data as Movie);
        setHasError(false);
      }
    });
    api({ path: `/movie/${movieId}/reviews`, method: "GET" }).then((res) => {
      if (res.code !== 0) {
        setHasError(true);
      } else {
        setReviews(res.data.items as Array<ReviewProps>);
        setHasError(false);
      }
    });
    api({
      path: `/movie/${movieId}/reviews`,
      method: "GET",
      params: { me: true },
    }).then((res) => {
      if (res.code !== 0) {
        setHasError(true);
      } else {
        setAuthorReview(res.data.items as Array<ReviewProps>);
        setHasError(false);
      }
    });
  }, [movieId]);
  

  useUpdateEffect(() => {
    paginationHandle && paginationHandle.refresh(1);
  }, [movieId]);

  if (movieDetails) {
    const formattedNumRatings: string = nFormatter(movieDetails.numVotes, 0);
    return (
      <div className={`MovieDetailPage ${(props.className || "").trim()}`}>
        <MovieSection>
          <div className="Movie__poster">
            <img
              src={movieDetails.imageUrl || movieLogo}
              alt=""
              className="Movie__poster-image"
            />
          </div>
          <div className="Movie__about">
            <h3 className="Movie__title">
              {movieDetails.title} ({movieDetails.releaseYear})
            </h3>
            {movieDetails.genres &&
              movieDetails.genres.map((genre, i) => (
                <GenreTile
                  id={genre}
                  key={i}
                  text={genre === "\\N" ? "Genre not listed" : genre}
                ></GenreTile>
              ))}
            <div className="movieScore">
              {movieDetails.numVotes > 0 && (
                <>
                  <Stars
                    id="movie-main-static"
                    movieId={movieId}
                    rating={movieDetails.averageRating}
                    setRating={() => {}}
                    size="small"
                    votable={false}
                  />
                  <Typography>
                    {movieDetails.averageRating}({formattedNumRatings})
                  </Typography>
                </>
              )}
            </div>
            <p className="Movie__description">{movieDetails.description}</p>
          </div>
          <div className="Movie__interact">
            <MovieInteract
              movieId={movieId}
              userRating={userRating}
              setUserRating={setUserRating}
              snapToReviews={snapToReviews}
            />
          </div>
        </MovieSection>
        {movieDetails.trailers && (
          <MovieSection heading="Trailers">
            <HorizontalList
              items={movieDetails.trailers.map((trailer) => (
                <div className="Movie__trailer">
                  <Trailer site={trailer.site} videoId={trailer.key}></Trailer>
                </div>
              ))}
            />
          </MovieSection>
        )}
        {movieDetails.crew && (
          <MovieSection heading="Cast and Crew">
            <div className="Cast">
              {movieDetails.crew.map((castMember, i) => (
                <div key={i} className="CastMember">
                  <img width={60} src={castMember.image || avatar} alt=""></img>
                  <span className="Movie__castname">{castMember.name}</span>
                  <i>{castMember.position}</i>
                </div>
              ))}
            </div>
          </MovieSection>
        )}
          <MovieSection heading="Recommended">
            <div className="Movie__section-content">
              {isLoadingRecommended || hasErrorRecommened ? (
                isLoadingRecommended ? (
                  <div className="Movie__loading-messages">
                    Fetching suggestions...
                  </div>
                ) : (
                  <div className="Movie__loading-messages">
                    An error occurred, please try again.
                  </div>
                )
              ) : recommended ? (
                <TileList
                  className="Movie__list"
                  itemClassName="Movie__item"
                  items={recommended.map((movie) => (
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
                <div className="Movie__loading-messages">
                  Sorry, we couldn't find anything new.
                </div>
              )}
            </div>

            <div className="Movie__pagination-wrapper">
              <Pagination
                className="Movie__pagination"
                displayType="dotted"
                dataType="slice"
                ref={(c) => {
                  paginationHandle = c;
                }}      
                dataCallback={async () => {
                  setIsLoadingRecommended(true);
                  let res;
                  try {
                    res = await api({
                      path: "/movies/recommendation",
                      method: "GET",
                      params: {
                        per_page: total,
                        type: "detail",
                        movie_id: movieId,
                        size: total,
                        page: 1,
                        sort: "rating",
                        desc: true,
                      },
                    });
                  } catch (e) {
                    setIsLoadingRecommended(false);
                    setHasErrorRecommended(true);
                    return [];
                  }
                  setIsLoadingRecommended(false);
                  if (res.code !== 0) {
                    setHasErrorRecommended(true);
                    return [];
                  } else {
                    setHasErrorRecommended(false);
                    return res.data.movies;
                  }
                }}
                renderCallback={(data) => {
                  console.log(data);
                  setRecommended(data as Array<SearchItem>);
                }}
                perPage={itemPerRow * 2}
              />
            </div>
          </MovieSection>
        
        <MovieSection heading="Reviews">
          <div id="ReviewSection" ref={reviewSection}></div>
          {authorReview && authorReview.length > 0 && (
            <ReviewEditor
              reviewId={authorReview[0].reviewId}
              movieId={movieId}
              description={authorReview[0].description}
              username={authorReview[0].username}
              createDate={authorReview[0].createDate}
              rating={userRating}
              setRating={setUserRating}
              profileImage={authorReview[0].profileImage || avatar}
              containsSpoiler={authorReview[0].containsSpoiler}
              flaggedFunny={authorReview[0].flaggedFunny}
              flaggedHelpful={authorReview[0].flaggedHelpful}
              flaggedSpoiler={authorReview[0].flaggedSpoiler}
              numFunny={authorReview[0].numFunny}
              numHelpful={authorReview[0].numHelpful}
              numSpoiler={authorReview[0].numSpoiler}
              disable={true}
              hideFlags={true}
              hideStats={false}
            ></ReviewEditor>
          )}
          {authorReview && authorReview.length === 0 && author && (
            <ReviewEditor
              reviewId=""
              movieId={movieId}
              username={author.username || ""}
              profileImage={author.image || avatar}
              hideFlags={true}
              hideStats={true}
              rating={userRating}
              setRating={setUserRating}
            ></ReviewEditor>
          )}
          {reviews && reviews.length > 0 && (
            <div className="Reviews">
              <VerticalList
                items={reviews.map((review) => (
                  <Review
                    reviewId={review.reviewId}
                    description={review.description}
                    username={review.username}
                    createDate={review.createDate}
                    rating={review.rating}
                    profileImage={review.profileImage || avatar}
                    containsSpoiler={review.containsSpoiler}
                    flaggedFunny={review.flaggedFunny}
                    flaggedHelpful={review.flaggedHelpful}
                    flaggedSpoiler={review.flaggedSpoiler}
                    numFunny={review.numFunny}
                    numHelpful={review.numHelpful}
                    numSpoiler={review.numSpoiler}
                  />
                ))}
              />
            </div>
          )}
        </MovieSection>
      </div>
    );
  }
  if (hasError) {
    return <div>There have been errors</div>;
  } else return null;
};

export default view(MovieDetailPage);
