import { Rating } from "@material-ui/lab";
import { view } from "@risingstack/react-easy-state";
import React from "react";
import ReviewFlags from "src/app/components/review-flags";
import "./review.scss";

export type ReviewProps = {
  reviewId: string;
  description: string;
  username: string;
  profileImage?: string;
  createDate: Date;
  rating: number;
  containsSpoiler: Boolean;
  flaggedHelpful?: boolean;
  flaggedFunny?: boolean;
  flaggedSpoiler?: boolean;
  numHelpful?: number;
  numFunny?: number;
  numSpoiler?: number;
};

const Review = (props: ReviewProps & { className?: string }) => {
  const showSpoiler = props.containsSpoiler || ((props.numHelpful || 0) > 10)
  return (
    <div className={`Review ${(props.className || "").trim()}`}>
      <a href={`/user/${props.username}`}>
        <img
          className="Reviewer__avatar"
          src={props.profileImage}
          width={60}
          alt=""
        />
      </a>
      <div className="Review__content">
        {props.rating && (
          <>
            <Rating
              name="star-rating"
              value={props.rating}
              precision={0.1}
              size="small"
              readOnly={true}
            />
            <span> {props.rating} stars</span>
          </>
        )}
        <p className="Review__meta">
          <a href={`/user/${props.username}`}>{props.username}</a>{" "}
          <span className="Review__date">
            posted at {`${new Date(props.createDate).toUTCString()}`}
          </span>
        </p>

        <p className="Review__content">
        {showSpoiler ? <details><summary>Spoiler</summary>{props.description}</details> : <div>{props.description}</div>}
        </p>
      </div>
      <ReviewFlags
        reviewId={props.reviewId}
        flaggedHelpful={props.flaggedHelpful}
        flaggedFunny={props.flaggedFunny}
        flaggedSpoiler={props.flaggedSpoiler}
        numHelpful={props.numHelpful}
        numFunny={props.numFunny}
        numSpoiler={props.numSpoiler}
      />
    </div>
  );
};

export default view(Review);
