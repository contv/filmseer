import Rating from "@material-ui/lab/Rating";
import { view } from "@risingstack/react-easy-state";
import React, { useEffect, useState } from "react";
import { api } from "../../../utils";
import "./stars.scss";

type StarsProps = {
  movieId: string;
  size: "small" | "medium" | "large";
  votable: boolean;
  rating?: number;
};

const Stars = (props: StarsProps & { className?: string }) => {
  const [rating, setRating] = useState(props.rating || 0);
  const [didMount, setDidMount] = useState(false);
  const [hover, setHover] = useState(0);

  function handleClick() {
    setRating(hover);
  }

  useEffect(() => setDidMount(true), []);

  useEffect(() => {
    if (props.votable && didMount) {
      api({
        path: `/movie/${props.movieId}/rating/`,
        method: "POST",
        params: { rating: rating },
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [rating]);

  return (
    <div className={`Stars ${(props.className || "").trim()}`}>
      <Rating
        name="star-rating"
        value={rating}
        precision={props.votable ? 0.5 : 0.1} // Allow static variant to display smaller increments
        size={props.size}
        readOnly={!props.votable}
        onClick={handleClick}
        onChangeActive={(event, value) => setHover(value)}
      />
    </div>
  );
};

export default view(Stars);
