import { view } from "@risingstack/react-easy-state";
import React from "react";
import ReviewFlags from "src/app/components/review-flags";
import { ReviewFlagsProps } from "src/app/components/review-flags/review-flags";
import "./review.scss";

export type ReviewProps = {
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
  console.log(props.flags)
  return (
    <div className={`Review ${(props.className || "").trim()}`}>
      <a href={`/user/${props.username}`}><img
        className="ReviewerProfilePicture"
        src={props.profileImage}
        width={60}
      />
      </a>
      <div className="ReviewContent">
        <p className="ReviewMeta">
          {props.rating} stars -{" "}
          <a href={`/user/${props.username}`}>{props.username}</a>{" "}
          <span className="ReviewDate">
            posted at {`${props.date.toUTCString()}`}
          </span>
        </p>
        <p className="ReviewContent">{props.text}</p>
      </div>
      {props.flags && (
        <ReviewFlags
          reviewId={props.id}
          flaggedHelpful={props.flags.flaggedHelpful}
          flaggedFunny={props.flags.flaggedFunny}
          flaggedSpoiler={props.flags.flaggedHelpful}
          numHelpful={props.flags.numHelpful}
          numFunny={props.flags.numFunny}
          numSpoiler={props.flags.numSpoiler}
        />
      )}
    </div>
  );
};

export default view(Review);
