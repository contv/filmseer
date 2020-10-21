import { view } from "@risingstack/react-easy-state";
import React from "react";
import "./review_emoji.scss";

type ReviewEmojiProps = {
  reviewId: string;
  helpfulPressed?: boolean;
  funnyPressed?: boolean;
  spoilerPressed?: boolean;
  helpfulCount?: number;
  funnyCount?: number;
  spoilerCount?: number;
};

const ReviewEmoji = (props: ReviewEmojiProps & { className?: string }) => {
  return (
    <div className={`ReviewEmoji ${(props.className || "").trim()}`}></div>
  );
};

export default view(ReviewEmoji);
