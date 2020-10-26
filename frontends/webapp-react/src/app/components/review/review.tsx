import { view } from "@risingstack/react-easy-state";
import React from "react";
import ReviewFlags from "src/app/components/review-flags";
import { ReviewFlagsProps } from "src/app/components/review-flags/review-flags";
import "./review_flags.scss";

type ReviewProps = {
  id: string;
  text: string;
  username: string;
  profileImage?: string;
  date: Date;
  rating: Number;
  containsSpoiler: Boolean;
  flags?: ReviewFlagsProps;
};

const Review = (props: ReviewProps & { className?: string }) => {
  return props.flags ? (
    <div className={`Review ${(props.className || "").trim()}`}>
      <img src={props.profileImage} width={60} />
      <div>
        <i>
          posted at {props.date.toDateString()} - {props.rating} stars{" "}
        </i>
        <p>
          {props.username} : {props.text}
        </p>
      </div>
      <ReviewFlags
        reviewId={props.id}
        flaggedHelpful={props.flags.flaggedHelpful}
        flaggedFunny={props.flags.flaggedFunny}
        flaggedSpoiler={props.flags.flaggedHelpful}
        numHelpful={props.flags.numHelpful}
        numFunny={props.flags.numFunny}
        numSpoiler={props.flags.numSpoiler}
      />
    </div>
  ) : null;
};

export default view(Review);
