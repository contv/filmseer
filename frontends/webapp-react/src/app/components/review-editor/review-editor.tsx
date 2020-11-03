import "./review-editor.scss";

import { ApiError, api } from "src/utils";

import React from "react";
import ReviewFlags from "src/app/components/review-flags";
import Stars from "src/app/components/stars";
import { view } from "@risingstack/react-easy-state";

export type ReviewEditorProps = {
  reviewId: string;
  movieId: string;
  description?: string;
  username?: string;
  profileImage?: string;
  createDate?: Date;
  rating?: number;
  containsSpoiler?: Boolean;
  flaggedHelpful?: boolean;
  flaggedFunny?: boolean;
  flaggedSpoiler?: boolean;
  numHelpful?: number;
  numFunny?: number;
  numSpoiler?: number;
  disable?: boolean;
  hideFlags?: boolean;
  hideStats?: boolean;
};

const ReviewEditor = (props: ReviewEditorProps & { className?: string }) => {
  const [editable, setEditable] = React.useState(props.disable);
  const [spoiler, setSpoiler] = React.useState(props.containsSpoiler || false);
  const [createDate, setCreateDate] = React.useState(props.createDate);
  const [desc, setDesc] = React.useState(props.description);
  const reviewDesc = async (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setDesc(event.target.value);
  };
  const toogleSpoiler = () => {
    setSpoiler(!spoiler);
  };
  const changeMode = async (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
    event.stopPropagation();
    event.nativeEvent.stopImmediatePropagation();
    setEditable(!editable);
    if (!editable) {
      try {
        const response = await api({
          path: "/movie/" + props.movieId + "/review",
          method: editable ? "PUT" : "POST",
          body: {
            description: desc,
            contains_spoiler: spoiler,
          },
        });
        setCreateDate(JSON.parse(JSON.stringify(response.data))["create_date"])
      } catch (error) {
        if (!(error instanceof ApiError)) {
          throw error;
        }
      }
    }
  };

  if (props.username) {
    return (
      <div className={`ReviewEditor ${(props.className || "").trim()}`}>
        <a href={`/user/${props.username}`}>
          <img
            className="RevieweEditor__avatar"
            src={props.profileImage}
            width={60}
            alt=""
            title={props.username}
          />
        </a>
        <div className="ReviewEditor__middle">
          {createDate && (
            <span>
              You posted at{" "}
              {`${new Date(createDate || "").toUTCString()}`}
            </span>
          )}
          <textarea
            className="ReviewEditor__textbox"
            disabled={editable}
            defaultValue={props.description}
            value={desc}
            onChange={reviewDesc}
          ></textarea>
          <ReviewFlags
            reviewId={props.reviewId}
            flaggedHelpful={props.flaggedHelpful}
            flaggedFunny={props.flaggedFunny}
            flaggedSpoiler={props.flaggedSpoiler}
            numHelpful={props.numHelpful}
            numFunny={props.numFunny}
            numSpoiler={props.numSpoiler}
            hideFlags={props.hideFlags}
          />
        </div>
        <div className="ReviewEditor__function">
          {
            <>
              <span>Your rating:</span>
              <Stars
                movieId={props.movieId}
                rating={props.rating}
                size="small"
                votable={editable ? false : true}
              />
              <label className="ReviewEditor__spoiler">
                <input
                  type="checkbox"
                  id="spoiler"
                  disabled={editable}
                  checked={spoiler ? true : false}
                  onChange={toogleSpoiler}
                />
                Mark as spoiler
              </label>
              <button onClick={changeMode}>
                {editable ? "Edit" : "Submit"}
              </button>
            </>
          }
        </div>
      </div>
    );
  } else {
    return <div></div>;
  }
};

export default view(ReviewEditor);
