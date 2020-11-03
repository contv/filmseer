import "./review-flags.scss";

import { ApiError, api } from "src/utils";

import Popup from "src/app/popups/popup-base";
import React from "react";
import funny from "./funny.svg";
import helpful from "./helpful.svg";
import spoiler from "./spoiler.svg";
import state from "src/app/states";
import { view } from "@risingstack/react-easy-state";

export type ReviewFlagsProps = {
  reviewId: string;
  flaggedHelpful?: boolean;
  flaggedFunny?: boolean;
  flaggedSpoiler?: boolean;
  numHelpful?: number;
  numFunny?: number;
  numSpoiler?: number;
  hideFlags?: boolean;
  hideStats?: boolean;
};

const ReviewFlags = (props: ReviewFlagsProps & { className?: string }) => {
  const [flaggedHelpful, setFlaggedHelpful] = React.useState(
    props.flaggedHelpful
  );
  const [flaggedFunny, setFlaggedFunny] = React.useState(props.flaggedFunny);
  const [flaggedSpoiler, setFlaggedSpoiler] = React.useState(
    props.flaggedSpoiler
  );

  const [numHelpful, setNumHelpful] = React.useState(props.numHelpful || 0);
  const [numFunny, setNumFunny] = React.useState(props.numFunny || 0);
  const [numSpoiler, setNumSpoiler] = React.useState(props.numSpoiler || 0);

  const [popupVisible, setPopupVisible] = React.useState(false);

  const clickHelpful = async (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
    event.stopPropagation();
    event.nativeEvent.stopImmediatePropagation();
    if (!state.loggedIn) {
      setPopupVisible(true);
    } else {
      try {
        const response = await api({
          path: "/review/" + props.reviewId + "/helpful",
          method: flaggedHelpful ? "DELETE" : "POST",
        });
        setNumHelpful(JSON.parse(JSON.stringify(response.data))["count"]);
        setFlaggedHelpful(!flaggedHelpful);
      } catch (error) {
        if (!(error instanceof ApiError)) {
          throw error;
        }
      }
    }
  };

  const clickFunny = async (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
    event.stopPropagation();
    event.nativeEvent.stopImmediatePropagation();
    if (!state.loggedIn) {
      setPopupVisible(true);
    } else {
      try {
        const response = await api({
          path: "/review/" + props.reviewId + "/funny",
          method: flaggedFunny ? "DELETE" : "POST",
        });
        setNumFunny(JSON.parse(JSON.stringify(response.data))["count"]);
        setFlaggedFunny(!flaggedFunny);
      } catch (error) {
        if (!(error instanceof ApiError)) {
          throw error;
        }
      }
    }
  };

  const clickSpoiler = async (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
    event.stopPropagation();
    event.nativeEvent.stopImmediatePropagation();
    if (!state.loggedIn) {
      setPopupVisible(true);
    } else {
      try {
        const response = await api({
          path: "/review/" + props.reviewId + "/spoiler",
          method: flaggedSpoiler ? "DELETE" : "POST",
        });
        setNumSpoiler(JSON.parse(JSON.stringify(response.data))["count"]);
        setFlaggedSpoiler(!flaggedSpoiler);
      } catch (error) {
        if (!(error instanceof ApiError)) {
          throw error;
        }
      }
    }
  };

  return (
    <div
      className={`ReviewFlags ${(
        props.className || ""
      ).trim()} ReviewFlags__outer`}
    >
      <button
        onClick={clickHelpful}
        className={
          "ReviewFlags__button" +
          (props.hideFlags ? " ReviewFlags__button--hide" : "")
        }
      >
        <img
          src={helpful}
          alt="Helpful"
          className={
            "ReviewFlags__image" +
            (flaggedHelpful ? "" : " ReviewFlags__image--grayscale")
          }
        />
        <span className="ReviewFlags__name">Helpful</span>
      </button>

      <button
        onClick={clickFunny}
        className={
          "ReviewFlags__button" +
          (props.hideFlags ? " ReviewFlags__button--hide" : "")
        }
      >
        <img
          src={funny}
          alt="Funny"
          className={
            "ReviewFlags__image" +
            (flaggedFunny ? "" : " ReviewFlags__image--grayscale")
          }
        />
        <span className="ReviewFlags__name">Funny</span>
      </button>

      <button
        onClick={clickSpoiler}
        className={
          "ReviewFlags__button" +
          (props.hideFlags ? " ReviewFlags__button--hide" : "")
        }
      >
        <img
          src={spoiler}
          alt="Spoiler"
          className={
            "ReviewFlags__image" +
            (flaggedSpoiler ? "" : " ReviewFlags__image--grayscale")
          }
        />
        <span className="ReviewFlags__name">Spoiler</span>
      </button>

      <div
        className={
          "ReviewFlags__numvote" +
          (props.hideStats ? " ReviewFlags__numvote--hide" : "")
        }
      >
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
          <div>Please login to express your opinion with this review</div>
        </Popup>
      ) : null}
    </div>
  );
};

export default view(ReviewFlags);
