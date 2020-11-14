import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import CardHeader from "@material-ui/core/CardHeader";
import CardMedia from "@material-ui/core/CardMedia";
import Typography from "@material-ui/core/Typography";
import { view } from "@risingstack/react-easy-state";
import React from "react";
import { Link } from "react-router-dom";
import GenreTile from "../genre-tile";
import Stars from "../stars";
import "./movie-item.scss";

export type MovieItemProps = {
  movieId: string;
  title: string;
  year: number;
  genres: { id: string; text: string }[];
  imageUrl?: string;
  cumulativeRating: number;
  numRatings: number;
  numReviews: number;
};

// Convert a number into a formatted string with k or M suffix applied
export const nFormatter = (num: number, digits: number) => {
  var suffix = [
    { value: 1, symbol: "" },
    { value: 1e3, symbol: "K" },
    { value: 1e6, symbol: "M" },
  ];
  var digitsAfterDecimalRx = /\.0+$|(\.[0-9]*[1-9])0+$/;
  var i;
  for (i = suffix.length - 1; i > 0; i--) {
    if (num >= suffix[i].value) {
      break;
    }
  }
  return (
    (num / suffix[i].value)
      .toFixed(digits)
      .replace(digitsAfterDecimalRx, "$1") + suffix[i].symbol
  );
};

const MovieItem = (props: MovieItemProps & { className?: string }) => {
  const avgRating: number = props.numRatings
    ? parseFloat((props.cumulativeRating / props.numRatings).toFixed(1))
    : 0;
  const formattedNumRatings: string = nFormatter(props.numRatings, 0);

  let genres = [];
  for (const genre of props.genres) {
    genres.push(<GenreTile key={genre.id} {...genre} />);
  }

  return (
    <Link
      className={`MovieItem ${(props.className || "").trim()}`}
      to={"/movie/" + props.movieId}
    >
      <Card className="MovieItem__card">
        <CardMedia
          className="MovieItem__media"
          image={props.imageUrl}
          title={props.title + " (" + props.year + ")"}
        >
          {" "}
        </CardMedia>
        <CardHeader
          className="MovieItem__header"
          title={props.title + " (" + props.year + ")"}
          subheader={genres}
        ></CardHeader>
        <CardContent className="MovieItem__content">
          {props.numRatings > 0 && (
            <>
              <Stars
                movieId={props.movieId}
                rating={avgRating}
                setRating={() => {}}
                size="small"
                votable={false}
              />
              <Typography>
                {avgRating}({formattedNumRatings})
              </Typography>
            </>
          )}
        </CardContent>
      </Card>
    </Link>
  );
};

export default view(MovieItem);
