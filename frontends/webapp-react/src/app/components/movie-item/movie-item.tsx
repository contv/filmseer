import { view } from "@risingstack/react-easy-state";
import React from "react";
import "./movie-tile.scss";

type MovieItemProps = {
  movieId: string;
  title: string;
  year: number;
  genres?: string[];
  imageUrl?: string;
  avgRating: number;
  numReviews: number;
};

const MovieItem = (props: MovieItemProps & { className?: string }) => {
  return <div className={`MovieItem ${(props.className || "").trim()}`}></div>;
};

export default view(MovieItem);
