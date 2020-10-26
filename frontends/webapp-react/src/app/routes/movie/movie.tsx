import { view } from "@risingstack/react-easy-state";
import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import MovieSection from "src/app/components/movie-section";
import Trailer from "src/app/components/trailer";
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

type Review = {
  text: string;
  date: Date;
  reviewerImage: string;
  reviewerName: string;
  rating: Number;
};

const dummyReviews = [
  {
    text: "Great Movie!",
    rating: 4.8,
    date: new Date(),
    reviewerName: "alice",
    reviewerImage: "https://material-ui.com/static/images/avatar/3.jpg",
  },
  {
    text: "Pretty terrible movie in my opinion",
    rating: 1.2,
    date: new Date(),
    reviewerName: "bob",
    reviewerImage: "https://material-ui.com/static/images/avatar/2.jpg",
  },
  {
    text: "it was okay...",
    date: new Date(),
    rating: 3.2,
    reviewerName: "john",
    reviewerImage: "https://material-ui.com/static/images/avatar/1.jpg",
  },
];

const MovieDetailPage = (props: { className?: string }) => {
  const { movieId } = useParams<{ movieId: string }>();
  const [movieDetails, setMovie] = useState<Movie>();
  const [reviews, setReviews] = useState<Array<Review>>();

  useEffect(() => {
    api({ path: `/movie/${movieId}`, method: "GET" }).then((res) =>
      setMovie(res.data as Movie)
    );
    setReviews(dummyReviews as Array<Review>)
  }, [movieId]);

  if (movieDetails) {
    console.log(movieDetails);
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
            {/* <GenreTags genres={movieDetails.genres}></GenreTags> */}
            Genre Tags go here.
            <div className="movieScore">
              {movieDetails.averageRating}({movieDetails.numReviews})
            </div>
            <p className="MovieDescription">{movieDetails.description}</p>
          </div>
          <div className="MovieInteract">
            <p>Watched</p>
            <p>Add to wishlist</p>
            <p>Flag inaccurate</p>
            <p>Your rating</p>
            <p>Post a review</p>
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
        </MovieSection>)}
        <MovieSection heading="Reviews">
          <div className="Reviews">
            {reviews &&
              reviews.map((review) => (
                <div className="Review">
                  <img src={review.reviewerImage} width={60}/>
                  <div>
                    <i>
                      posted at {review.date.toDateString()} - {review.rating}{" "}
                      stars{" "}
                    </i>
                    <p>
                      {review.reviewerName} : {review.text}
                    </p>
                  </div>
                </div>
              ))}
          </div>
        </MovieSection>
      </div>
    );
  } else return null;
};

export default view(MovieDetailPage);
