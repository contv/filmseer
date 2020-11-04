import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import CardHeader from "@material-ui/core/CardHeader";
import CardMedia from "@material-ui/core/CardMedia";
import Typography from "@material-ui/core/Typography";
import { view } from "@risingstack/react-easy-state";
import React from "react";
import { useHistory } from "react-router-dom"
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
  let history = useHistory();

  const avgRating: number = parseFloat(
    (props.cumulativeRating / props.numRatings).toFixed(1)
  );
  const formattedNumRatings: string = nFormatter(props.numRatings, 0);

  const handleClick = () => {
    history.push("/movie/" + props.movieId)
  };

  let genres = [];
  for (const genre of props.genres) {
    genres.push(<GenreTile key={genre.id} {...genre} />);
  }

  return (
    <div className={`MovieItem ${(props.className || "").trim()}`}>
        <Card className="MovieItem__card" onClick={handleClick}>
          <CardMedia
            className="MovieItem__media"
            image={props.imageUrl}
            title={props.title + " (" + props.year + ")"}
          />
          <CardHeader
            className="MovieItem__header"
            title={props.title + " (" + props.year + ")"}
            subheader={genres}
          ></CardHeader>
          <CardContent className="MovieItem__content">
            <Stars
              movieId={props.movieId}
              rating={avgRating}
              size="small"
              votable={false}
            />
            <Typography>
              {avgRating}({formattedNumRatings})
            </Typography>
          </CardContent>
        </Card>
    </div>
  );
};

export default view(MovieItem);
