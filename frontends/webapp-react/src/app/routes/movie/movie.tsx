import Typography from "@material-ui/core/Typography";
import { view } from "@risingstack/react-easy-state";
import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import GenreTile from "src/app/components/genre-tile";
import MovieInteract from "src/app/components/movie-interact";
import MovieItem from "src/app/components/movie-item";
import {
  MovieItemProps,
  nFormatter,
} from "src/app/components/movie-item/movie-item";
import MovieSection from "src/app/components/movie-section";
import Review from "src/app/components/review";
import ReviewEditor from "src/app/components/review-editor";
import avatar from "src/app/components/review/default-avatar.png";
import { ReviewProps } from "src/app/components/review/review";
import Stars from "src/app/components/stars";
import TileList from "src/app/components/tile-list";
import Trailer from "src/app/components/trailer";
import VerticalList from "src/app/components/vertical-list";
import { User } from "src/app/routes/user/user";
import state from "src/app/states";
import { api } from "src/utils";
import "./movie.scss";

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

const dummyRecommendedMovies = [
  {
    movieId: "someId",
    title: "movie1",
    year: 1992,
    genres: [
      { id: "1", text: "drama" },
      { id: "2", text: "mystery" },
    ],
    imageUrl:
      "https://m.media-amazon.com/images/M/MV5BOTQyMjBmNDAtNDA0YS00ODFiLTk2OTUtMWM5NzI4NjM1YzhhXkEyXkFqcGdeQXVyMTA2MDU0NjM5._V1_UX182_CR0,0,182,268_AL_.jpg",
    cumulativeRating: 450,
    numRatings: 100,
    numReviews: 200,
  },
  {
    movieId: "someId2",
    title: "movie2",
    year: 1993,
    genres: [
      { id: "1", text: "war" },
      { id: "2", text: "mystery" },
    ],
    imageUrl:
      "https://m.media-amazon.com/images/M/MV5BOTQyMjBmNDAtNDA0YS00ODFiLTk2OTUtMWM5NzI4NjM1YzhhXkEyXkFqcGdeQXVyMTA2MDU0NjM5._V1_UX182_CR0,0,182,268_AL_.jpg",
    cumulativeRating: 250,
    numRatings: 52,
    numReviews: 22,
  },
  {
    movieId: "someId3",
    title: "movie3",
    year: 2001,
    genres: [{ id: "1", text: "comedy" }],
    imageUrl:
      "https://m.media-amazon.com/images/M/MV5BOTQyMjBmNDAtNDA0YS00ODFiLTk2OTUtMWM5NzI4NjM1YzhhXkEyXkFqcGdeQXVyMTA2MDU0NjM5._V1_UX182_CR0,0,182,268_AL_.jpg",
    cumulativeRating: 450,
    numRatings: 150,
    numReviews: 15,
  },
  {
    movieId: "someId4",
    title: "movie4",
    year: 2015,
    genres: [
      { id: 1, text: "horror" },
      { id: 2, text: "mystery" },
    ],
    imageUrl:
      "https://m.media-amazon.com/images/M/MV5BOTQyMjBmNDAtNDA0YS00ODFiLTk2OTUtMWM5NzI4NjM1YzhhXkEyXkFqcGdeQXVyMTA2MDU0NjM5._V1_UX182_CR0,0,182,268_AL_.jpg",
    cumulativeRating: 200,
    numRatings: 40,
    numReviews: 7,
  },
];

const MovieDetailPage = (props: { className?: string }) => {
  const { movieId } = useParams<{ movieId: string }>();
  const [movieDetails, setMovie] = useState<Movie>();
  const [author, setAuthor] = useState<User>();
  const [reviews, setReviews] = useState<Array<ReviewProps>>();
  const [authorReview, setAuthorReview] = useState<Array<ReviewProps>>();
  const [recommended, setRecommended] = useState<Array<MovieItemProps>>();
  const [hasError, setHasError] = useState<Boolean>(false);

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
    setRecommended(dummyRecommendedMovies as Array<MovieItemProps>);
  }, [movieId]);

  if (movieDetails) {
    const formattedNumRatings: string = nFormatter(movieDetails.numVotes, 0);
    return (
      <div className={`MovieDetailPage ${(props.className || "").trim()}`}>
        <MovieSection>
          <div className="Movie__poster">
            <img src={movieDetails.imageUrl} alt="" />
          </div>
          <div className="Movie__about">
            <h3 className="Movie__title">
              {movieDetails.title} ({movieDetails.releaseYear})
            </h3>
            {movieDetails.genres &&
              movieDetails.genres.map((genre) => (
                <GenreTile
                  id={genre}
                  text={genre === "\\N" ? "Genre not listed" : genre}
                ></GenreTile>
              ))}
            <div className="movieScore">
              {movieDetails.numVotes > 0 && (
                <>
                  <Stars
                    movieId={movieId}
                    rating={movieDetails.averageRating}
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
            <MovieInteract movieId={movieId} />
          </div>
        </MovieSection>
        {movieDetails.trailers && (
          <MovieSection heading="Trailers">
            <TileList
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
              {movieDetails.crew.map((castMember) => (
                <div className="CastMember">
                  <img width={60} src={castMember.image || avatar} alt=""></img>
                  <span className="Movie__castname">{castMember.name}</span>
                  <i>{castMember.position}</i>
                </div>
              ))}
            </div>
          </MovieSection>
        )}
        {recommended && (
          <MovieSection heading="Recommended">
            <TileList
              items={recommended.map((movie) => (
                <div className="Movie__review">
                  <MovieItem
                    movieId={movie.movieId}
                    year={movie.year}
                    title={movie.title}
                    genres={movie.genres}
                    imageUrl={movie.imageUrl}
                    cumulativeRating={movie.cumulativeRating}
                    numRatings={movie.numRatings}
                    numReviews={movie.numReviews}
                  />
                </div>
              ))}
            />
          </MovieSection>
        )}
        <MovieSection heading="Reviews">
          <div id="ReviewSection"></div>
          {authorReview && authorReview.length > 0 && (
            <ReviewEditor
              reviewId={authorReview[0].reviewId}
              movieId={movieId}
              description={authorReview[0].description}
              username={authorReview[0].username}
              createDate={authorReview[0].createDate}
              rating={authorReview[0].rating}
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
