import { view } from "@risingstack/react-easy-state";
import React from "react";
import "./stars.scss";

type StarsProps = {
  size?: "small" | "medium" | "large";
  type?: "static" | "votable";
  displayRating?: boolean;
  cumulativeRating: number;
  numRatings: number;
  onClick?: () => void;
};

const Stars = (props: StarsProps & { className?: string }) => {
  const rating = props.displayRating
    ? (props.cumulativeRating / props.numRatings).toFixed(1)
    : "";

  return (
    <div>
      <div className={`Stars ${(props.className || "").trim()}`}>
        <a className="Stars__star" href="#" onClick={props.onClick}>
          <span>★</span>
        </a>
        <a className="Stars__star" href="#" onClick={props.onClick}>
          <span>★</span>
        </a>
        <a className="Stars__star" href="#" onClick={props.onClick}>
          <span>★</span>
        </a>
        <a className="Stars__star" href="#" onClick={props.onClick}>
          <span>★</span>
        </a>
        <a className="Stars__star" href="#" onClick={props.onClick}>
          <span>★</span>
        </a>
      </div>
      <div className="Rating">
        {rating}({props.numRatings})
      </div>
    </div>
  );
};

export default view(Stars);
