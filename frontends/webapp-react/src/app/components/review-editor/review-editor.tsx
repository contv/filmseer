import { Rating } from "@material-ui/lab";
import { view } from "@risingstack/react-easy-state";
import React from "react";
import "./review-editor.scss";

export type ReviewEditorProps = {
  reviewId?: string;
  description?: string;
  username?: string;
  profileImage?: string;
  createDate?: Date;
  rating?: number;
  flagSpoiler?: Boolean;
  numHelpful?: number;
  numFunny?: number;
  numSpoiler?: number;
  disable?: boolean;
};

const ReviewEditor = (props: ReviewEditorProps & { className?: string }) => {
  const [editable, setEditable] = React.useState(props.disable);
  const changeMode = async (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
    event.stopPropagation();
    event.nativeEvent.stopImmediatePropagation();
    setEditable(!editable);
  };
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
        <textarea
          className="ReviewEditor__textbox"
          disabled={editable}
        ></textarea>
      <div className="ReviewEditor__function">
        {
          <>
            <span>Your rating:</span>
            <Rating
              name="star-rating"
              className="ReviewEditor__rating"
              value={props.rating}
              precision={0.1}
              size="small"
              readOnly={editable}
            />
            <label className="ReviewEditor__spoiler">
              <input type="checkbox" id="spoiler" disabled={editable} />
              Mark as spoiler
            </label>
            <button onClick={changeMode}>{editable ? "Edit" : "Submit"}</button>
          </>
        }
      </div>
    </div>
  );
};

export default view(ReviewEditor);
