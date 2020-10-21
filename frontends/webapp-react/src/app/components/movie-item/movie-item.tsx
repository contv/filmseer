import { view } from "@risingstack/react-easy-state";
import React from "react";
import Card from "@material-ui/core/Card";
import CardHeader from "@material-ui/core/CardHeader";
import CardMedia from "@material-ui/core/CardMedia";
import CardContent from "@material-ui/core/CardContent";
import Typography from "@material-ui/core/Typography";
import Stars from "../stars";
import GenreTile from "../genre-tile";
import "./movie-item.scss";

type MovieItemProps = {
  movieId: string;
  title: string;
  year: number;
  genres: { text: string }[];
  imageUrl?: string;
  cumulativeRating: number;
  numRatings: number;
  numReviews: number;
};

// Convert a number into a formatted string with k or M suffix applied
const nFormatter = (num: number, digits: number) => {
  var suffix = [
    { value: 1, symbol: "" },
    { value: 1e3, symbol: "K" },
    { value: 1e6, symbol: "M" },
  ];
  var rx = /\.0+$|(\.[0-9]*[1-9])0+$/;
  var i;
  for (i = suffix.length - 1; i > 0; i--) {
    if (num >= suffix[i].value) {
      break;
    }
  }
  return (
    (num / suffix[i].value).toFixed(digits).replace(rx, "$1") + suffix[i].symbol
  );
};

const MovieItem = (props: MovieItemProps & { className?: string }) => {
  const avgRating: number = parseFloat(
    (props.cumulativeRating / props.numRatings).toFixed(1)
  );
  const formattedNumRatings: string = nFormatter(props.numRatings, 0);

  const handleClick = () => {
    // redirect to movie detail page
  };

  let genres = [];
  for (const genre of props.genres) {
    genres.push(<GenreTile {...genre} />);
  }

  return (
    <Card>
      <CardMedia
        image={props.imageUrl}
        title={props.title + " (" + props.year + ")"}
        onClick={handleClick}
      />
      <CardHeader
        title={props.title + " (" + props.year + ")"}
        subheader={genres}
      />
      <CardContent>
        <Stars
          movieId={props.movieId}
          rating={avgRating}
          size="small"
          votable={false}
        />
        <Typography variant="subtitle1" display="inline">
          {avgRating}({formattedNumRatings})
        </Typography>
      </CardContent>
    </Card>
  );
};

export default view(MovieItem);
