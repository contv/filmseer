import { view } from "@risingstack/react-easy-state";
import React from "react";
import { ReviewFlagsProps } from "src/app/components/review-flags/review-flags"
import "./review_flags.scss";

type ReviewProps = {
  reviewId: string;
  reviewText: string;
  reviewerUsername: string;
  flags: ReviewFlagsProps;
};

const Review = (props: ReviewProps & { className?: string }) => {
  return (
    <div className={`Review ${(props.className || "").trim()}`}></div>
  );
};

export default view(Review);
