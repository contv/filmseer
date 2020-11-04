import Rating from "@material-ui/lab/Rating";
import { view } from "@risingstack/react-easy-state";
import React, { useState } from "react";
import { apiEffect, useUpdateEffect } from "src/utils";
import TabPopup from "src/app/popups/popup-tabs";
import Register from "src/app/popups/register";
import Login from "src/app/popups/login";
import state from "src/app/states";
import "./stars.scss";

type StarsProps = {
  id: string;
  movieId: string;
  size: "small" | "medium" | "large";
  votable: boolean;
  rating: number;
  setRating: Function;
};

const Stars = (props: StarsProps & { className?: string }) => {
  const [rating, setRating] = useState(props.rating || 0);
  const [prevRating, setPrevRating] = useState(props.rating || 0);
  const [hover, setHover] = useState(0);
  const [awaiting, setAwaiting] = useState(false);
  const [popupVisible, setPopupVisible] = useState(false);

  function handleClick() {
    if (!state.loggedIn) {
      setPopupVisible(true);
    } else {
      setRating(hover);
    }
  }

  useUpdateEffect(() => {
    if (props.votable && state.loggedIn) {
      let didCancel = false;
      const updateRatingAPI = apiEffect(
        {
          path: `/movie/${props.movieId}/rating`,
          method: "POST",
          params: { rating: rating },
        },
        (response) => {
          props.setRating(response.data.rating);
          setRating(response.data.rating);
          setPrevRating(response.data.rating);
          setAwaiting(false);
        },
        () => {
          setRating(prevRating);
          setAwaiting(false);
        },
        () => {
          return !didCancel;
        }
      );

      if (!awaiting) {
        setAwaiting(true);
        updateRatingAPI();
      }

      return () => {
        didCancel = true;
      };
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [rating]);

  return (
    <div className={`Stars ${(props.className || "").trim()}`}>
      <Rating
        name={props.id}
        value={props.rating}
        precision={props.votable ? 0.5 : 0.1} // Allow static variant to display smaller increments
        size={props.size}
        readOnly={!props.votable}
        onClick={handleClick}
        onChangeActive={(event, value) => setHover(value)}
      />
      {popupVisible ? (
        <TabPopup
          tabs={{
            login: (
              <Login
                onClose={() => {
                  setPopupVisible(false);
                }}
              />
            ),
            register: (
              <Register
                onClose={() => {
                  setPopupVisible(false);
                }}
              />
            ),
          }}
          tabNames={{
            login: <span>Sign In</span>,
            register: <span>Register</span>,
          }}
          onClose={() => {
            setPopupVisible(false);
          }}
          currentTabStateName="userMenuPopupTab"
        />
      ) : null}
    </div>
  );
};

export default view(Stars);
