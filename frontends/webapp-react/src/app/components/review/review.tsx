import { Rating } from "@material-ui/lab";
import { view } from "@risingstack/react-easy-state";
import React from "react";
import { Link } from "react-router-dom";
import ReviewFlags from "src/app/components/review-flags";
import "./review.scss";

export type ReviewProps = {
  reviewId: string;
  description: string;
  username: string;
  movieTitle?: string;
  movieYear?: string;
  movieId?: string;
  showMovie?: boolean;
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
  hideFlags?: boolean;
};

const Review = (props: ReviewProps & { className?: string }) => {
  const showSpoiler = props.containsSpoiler || (props.numSpoiler || 0) > 9;
  const authorSpoiler = props.containsSpoiler;
  return (
    <div className={`Review ${(props.className || "").trim()}`}>
      <Link to={`/user/${props.username}`}>
        <img
          className="Review__user-avatar"
          src={props.profileImage}
          width={60}
          alt=""
        />
      </Link>
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
          <Link to={`/user/${props.username}`}>{props.username}</Link>{" "}
          {props.showMovie && (
            <span className="Review__meta-reviews">reviews</span>
          )}
          {props.showMovie && (
            <Link to={`/movie/${props.movieId}`}>
              {props.movieTitle} ({props.movieYear})
            </Link>
          )}
          <span className="Review__date">
            posted at {`${new Date(props.createDate).toUTCString()}`}
          </span>
        </p>

        <div className="Review__content">
          {showSpoiler ? (
            <details>
              <summary>
                {authorSpoiler
                  ? "May contain spoilers"
                  : props.numSpoiler +
                    " people think this review contains spoiler"}
              </summary>
              {props.description}
            </details>
          ) : (
            <div>{props.description}</div>
          )}
        </div>
      </div>
      {!props.hideFlags && (
        <ReviewFlags
          reviewId={props.reviewId}
          flaggedHelpful={props.flaggedHelpful}
          flaggedFunny={props.flaggedFunny}
          flaggedSpoiler={props.flaggedSpoiler}
          numHelpful={props.numHelpful}
          numFunny={props.numFunny}
          numSpoiler={props.numSpoiler}
        />
      )}
    </div>
  );
};

export default view(Review);
