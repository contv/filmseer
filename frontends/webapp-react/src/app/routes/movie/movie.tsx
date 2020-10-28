import Typography from "@material-ui/core/Typography";
import { ChatBubble } from "@material-ui/icons";
import BookmarkIcon from "@material-ui/icons/Bookmark";
import FlagIcon from "@material-ui/icons/Flag";
import VisibilityIcon from "@material-ui/icons/Visibility";
import Rating from "@material-ui/lab/Rating";
import { view } from "@risingstack/react-easy-state";
import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import GenreTile from "src/app/components/genre-tile";
import HorizontalList from "src/app/components/horizontal-list";
import MovieItem from "src/app/components/movie-item";
import { MovieItemProps } from "src/app/components/movie-item/movie-item";
import MovieSection from "src/app/components/movie-section";
import Review from "src/app/components/review";
import { ReviewProps } from "src/app/components/review/review";
import Trailer from "src/app/components/trailer";
import VerticalList from "src/app/components/vertical-list";
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
  cumulativeRating: Number;
  averageRating: Number;
  numReviews: Number;
  description: string;
  trailers: Array<Trailer>;
  crew?: Array<CastMember>;
  genres: Array<string>;
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

const dummyReviews = [
  {
    id: "someid",
    text: "Great Movie!",
    rating: 4.8,
    date: new Date(),
    username: "alice",
    containsSpoiler: false,
    profileImage: "https://material-ui.com/static/images/avatar/3.jpg",
    flags: {
      reviewId: "someid",
      flaggedFunny: true,
      flaggedHelpful: true,
      flaggedSpoiler: false,
      numFunny: 3,
      numHelpful: 12,
      numSpoiler: 5,
    },
  },
  {
    id: "someid",
    text: "Pretty terrible movie in my opinion",
    rating: 1.2,
    date: new Date(),
    username: "bob",
    containsSpoiler: false,
    profileImage: "https://material-ui.com/static/images/avatar/2.jpg",
    flags: {
      reviewId: "someid",
      flaggedFunny: false,
      flaggedHelpful: true,
      flaggedSpoiler: false,
      numFunny: 0,
      numHelpful: 4,
      numSpoiler: 5,
    },
  },
  {
    id: "someid",
    text: "it was okay...",
    date: new Date(),
    rating: 3.2,
    username: "john",
    containsSpoiler: false,
    profileImage: "https://material-ui.com/static/images/avatar/1.jpg",
    flags: {
      reviewId: "someid",
      flaggedFunny: true,
      flaggedHelpful: true,
      flaggedSpoiler: false,
      numFunny: 5,
      numHelpful: 7,
      numSpoiler: 9,
    },
  },
];

const MovieDetailPage = (props: { className?: string }) => {
  const { movieId } = useParams<{ movieId: string }>();
  const [movieDetails, setMovie] = useState<Movie>();
  const [reviews, setReviews] = useState<Array<ReviewProps>>();
  const [recommended, setRecommended] = useState<Array<MovieItemProps>>();
  const [hasError, setHasError] = useState<Boolean>(false);

  useEffect(() => {
    api({ path: `/movie/${movieId}`, method: "GET" }).then((res) => {
      if (res.code != 0) setHasError(true)
      else {
        setMovie(res.data as Movie);
        setHasError(false)
      }
    });
    setReviews(dummyReviews as Array<ReviewProps>);
    setRecommended(dummyRecommendedMovies as Array<MovieItemProps>);
  }, [movieId]);

  if (movieDetails) {
    return (
      <div className={`MovieDetailPage ${(props.className || "").trim()}`}>
        <MovieSection>
          <div className="MoviePoster">
            <img src={movieDetails.imageUrl} />
          </div>
          <div className="MovieAbout">
            <h3 className="MovieTitle">
              {movieDetails.title} ({movieDetails.releaseYear})
            </h3>
            {movieDetails.genres.map((genre) => (
              <GenreTile id={genre} text={genre}></GenreTile>
            ))}
            <div className="movieScore">
              {movieDetails.numReviews > 0 && (
                <>
                  {movieDetails.averageRating}({movieDetails.numReviews})
                </>
              )}
            </div>
            <p className="MovieDescription">{movieDetails.description}</p>
          </div>
          <div className="MovieInteract">
            <p>
              <VisibilityIcon />
              <Typography variant="body2" display="inline">
                Watched
              </Typography>
            </p>
            <p>
              <BookmarkIcon></BookmarkIcon>
              <Typography variant="body2" display="inline">
                Add to wishlist
              </Typography>
            </p>
            <p>
              <FlagIcon />
              <Typography variant="body2" display="inline">
                Flag inaccurate
              </Typography>
            </p>
            <p>
              <Typography variant="body2">Your rating</Typography>
              <Rating />
            </p>
            <p>
              <ChatBubble />
              <Typography variant="body2" display="inline">
                Post a review
              </Typography>
            </p>
          </div>
        </MovieSection>
        <MovieSection heading="Trailers">
          <div className="Trailers">
            {movieDetails.trailers.map((trailer) => (
              <Trailer site={trailer.site} videoId={trailer.key}></Trailer>
            ))}
          </div>
        </MovieSection>
        {movieDetails.crew && (
          <MovieSection heading="Cast and Crew">
            <div className="Cast">
              {movieDetails.crew.map((castMember) => (
                <div className="CastMember">
                  <img
                    width={60}
                    src={
                      castMember.image ||
                      "https://m.media-amazon.com/images/G/01/imdb/images/nopicture/medium/name-2135195744._CB466677935_.png"
                    }
                  ></img>
                  {castMember.name} - <i>{castMember.position}</i>
                </div>
              ))}
            </div>
          </MovieSection>
        )}
        {recommended && (
          <MovieSection heading="Recommended">
            <HorizontalList
              items={recommended.map((movie) => (
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
              ))}
            />
          </MovieSection>
        )}
        <MovieSection heading="Reviews">
          {reviews && (
            <div className="Reviews">
              <VerticalList
                items={reviews.map((review) => (
                  <Review
                    id={review.id}
                    text={review.text}
                    username={review.username}
                    date={review.date}
                    rating={review.rating}
                    profileImage={review.profileImage}
                    containsSpoiler={review.containsSpoiler}
                    flags={review.flags}
                  />
                ))}
              />
            </div>
          )}
        </MovieSection>
      </div>
    );
  } 
  if (hasError){
  return(<div>There have been errors</div>);
  }
  else return null;
};

export default view(MovieDetailPage);
