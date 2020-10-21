import { view } from "@risingstack/react-easy-state";
import React, { useState } from "react";
import Rating from "@material-ui/lab/Rating";
import "./stars.scss";

type StarsProps = {
  movieId: string;
  size: "small" | "medium" | "large";
  votable: boolean;
  rating?: number;
};

const Stars = (props: StarsProps & { className?: string }) => {
  const [rating, setRating] = useState(props.rating || 0);
  const [hover, setHover] = useState(0);

  function handleClick() {
    setRating(hover);
    // onClick to update movie rating when votable=True
  }

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
