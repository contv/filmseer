import { view } from "@risingstack/react-easy-state";
import React from "react";
import "./review_flags.scss";

export type ReviewFlagsProps = {
  reviewId: string;
  flaggedHelpful?: boolean;
  flaggedFunny?: boolean;
  flaggedSpoiler?: boolean;
  numHelpful?: number;
  numFunny?: number;
  numSpoiler?: number;
};

const ReviewFlags = (props: ReviewFlagsProps & { className?: string }) => {
  return (
    <div className={`ReviewFlags ${(props.className || "").trim()}`}></div>
  );
};

export default view(ReviewFlags);
