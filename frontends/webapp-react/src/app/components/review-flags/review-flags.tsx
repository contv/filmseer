import { view } from "@risingstack/react-easy-state";
import React from "react";
import Popup from "src/app/popups/popup-base";
import state from "src/app/states";
import { api } from "src/utils";
import funny from "./funny.svg";
import helpful from "./helpful.svg";
import "./review-flags.scss";
import spoiler from "./spoiler.svg";

type ReviewFlagsProps = {
  reviewId: string;
  flaggedHelpful?: boolean;
  flaggedFunny?: boolean;
  flaggedSpoiler?: boolean;
  numHelpful?: number;
  numFunny?: number;
  numSpoiler?: number;
};

const ReviewFlags = (props: ReviewFlagsProps & { className?: string }) => {
  const [flagHelpful, setflagHelpful] = React.useState(props.flaggedHelpful);
  const [flagFunny, setflagFunny] = React.useState(props.flaggedFunny);
  const [flagSpoiler, setflagSpoiler] = React.useState(props.flaggedSpoiler);

  const [numHelpful, setNumHelpful] = React.useState(
    props.numHelpful ? props.numHelpful : 0
  );

  const [numFunny, setNumFunny] = React.useState(
    props.numFunny ? props.numFunny : 0
  );

  const [numSpoiler, setNumSpoiler] = React.useState(
    props.numSpoiler ? props.numSpoiler : 0
  );

  const [popupVisible, setPopupVisible] = React.useState(false);
  const clickHelpful = async (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
    event.stopPropagation();
    event.nativeEvent.stopImmediatePropagation();
    if (!state.loggedIn) {
      setPopupVisible(true);
    } else {
      if (!flagHelpful) {
        setNumHelpful(numHelpful + 1)
      } else {
        setNumHelpful(numHelpful - 1)
      }

      setflagHelpful(!flagHelpful);
      await api({
        path: "/review/" + props.reviewId + "/helpful",
        method: "POST",
      });
    }
  };

  return (
    <div
      className={`ReviewFlags ${(
        props.className || ""
      ).trim()} ReviewFlags__outer`}
    >
      <button onClick={clickHelpful} className="ReviewFlags__button">
        <img
          src={helpful}
          alt="Helpful"
          className={
            "ReviewFlags__img" +
            (flagHelpful ? "" : " ReviewFlags__img--grayscale")
          }
        />
        <span className="ReviewFlags__text">Helpful</span>
      </button>

      <button onClick={clickHelpful} className="ReviewFlags__button">
        <img
          src={funny}
          alt="Funny"
          className={
            "ReviewFlags__img" +
            (flagHelpful ? "" : " ReviewFlags__img--grayscale")
          }
        />
        <span className="ReviewFlags__text">Funny</span>
      </button>

      <button onClick={clickHelpful} className="ReviewFlags__button">
        <img
          src={spoiler}
          alt="Spoiler"
          className={
            "ReviewFlags__img" +
            (flagHelpful ? "" : " ReviewFlags__img--grayscale")
          }
        />
        <span className="ReviewFlags__text">Spoiler</span>
      </button>

      <div className="ReviewFlags__numvote">
        <div>{numHelpful} people think this review is helpful</div>
        <div>{numFunny} people think this review is funny</div>
        <div>{numSpoiler} people think this review is spoiler</div>
      </div>
      {popupVisible ? (
        <Popup
          onClose={() => {
            setPopupVisible(false);
          }}
        >
          <div>Please login to mark this review as helpful</div>
        </Popup>
      ) : null}
    </div>
  );
};

export default view(ReviewFlags);
