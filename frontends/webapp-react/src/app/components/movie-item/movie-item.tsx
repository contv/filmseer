import { view } from "@risingstack/react-easy-state";
import React from "react";
import "./movie-item.scss";
import GenreLogo from "./genrelogo.svg";
import ReviewLogo from "./reviewlogo.svg";
import GenreTile from "../genre-tile";
import Stars from "../stars";

type MovieItemProps = {
  movieId: string;
  title: string;
  year: number;
  genres: { id: string; text: string }[];
  imageUrl?: string;
  cumulativeRating: number;
  numRatings: number;
  numReviews: number;
};

const MovieItem = (props: MovieItemProps & { className?: string }) => {
  const genres = [];
  for (const genre of props.genres) {
    genres.push(<GenreTile key={genre.id} {...genre} />);
  }

  return (
    <div className={`MovieItem ${(props.className || "").trim()}`}>
      <p className="MovieItem__title">
        {props.title} ({props.year})
      </p>
      <div className="MovieItem__subtitle">
        <img src={GenreLogo} alt=""></img>
        <ul className="MovieItem__genres">{genres}</ul>
      </div>
      <img
        className="MovieItem__image"
        src={props.imageUrl}
        alt={props.title}
      ></img>
      <div className="MovieItem__footer">
        <Stars
          cumulativeRating={props.cumulativeRating}
          numRatings={props.numRatings}
          displayRating={true}
        />
        <div className="MovieItem__footer">
          <img src={ReviewLogo} alt=""></img>
          <div style={{ display: "inline" }}>{props.numReviews}</div>
        </div>
      </div>
    </div>
  );
};

export default view(MovieItem);
