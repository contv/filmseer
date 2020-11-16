import "./movie-interact.scss";

import React, { useEffect, useState } from "react";

import BookmarkIcon from "@material-ui/icons/Bookmark";
import { ChatBubble } from "@material-ui/icons";
import FlagIcon from "@material-ui/icons/Flag";
import Popup from "src/app/popups/popup-base";
import Stars from "src/app/components/stars";
import Typography from "@material-ui/core/Typography";
import VisibilityIcon from "@material-ui/icons/Visibility";
import { api } from "src/utils";
import state from "src/app/states";
import { view } from "@risingstack/react-easy-state";

type MovieInteractProps = {
  movieId: string;
  userRating: number;
  setUserRating: (newValue: number) => void;
};

const MovieInteract = (props: MovieInteractProps & {snapToReviews : any}) => {;
  const [isWishlisted, setIsWishlisted] = useState<Boolean>(false);
  const [popupVisible, setPopupVisible] = React.useState(false);

  const showPopupIfNotLoggedIn = () => {
    if (!state.loggedIn) {
      setPopupVisible(true)
    }
  };
  const onWishlist = () => {
    if (state.loggedIn) {
      if (!isWishlisted) {
        api({ path: `/wishlist/${props.movieId}`, method: "PUT" }).then(
          (res) => {
            if (res.code === 0) {
              setIsWishlisted(true);
            }
          }
        );
      } else {
        api({ path: `/wishlist/${props.movieId}`, method: "DELETE" }).then(
          (res) => {
            if (res.code === 0) {
              setIsWishlisted(false);
            }
          }
        );
      }
    } else {
      setPopupVisible(true)
    }
  };

  useEffect(() => {
    if (state.loggedIn) {
      api({ path: `/wishlist/${props.movieId}`, method: "GET" }).then((res) => {
        setIsWishlisted(res.data.added);
      });
    } else {
      setIsWishlisted(false);
    }

  }, [props.movieId]);

return (
    <>
      <div>
        <BookmarkIcon
          onClick={onWishlist}
          style={{ fill: isWishlisted ? "green" : "black" }}
        ></BookmarkIcon>
        <Typography variant="body2" display="inline">
          {isWishlisted ? "Remove from wishlist" : "Add to wishlist"}
        </Typography>
      </div>
      <div>
        <Typography variant="body2">Your rating</Typography>
        <Stars
          id="movie-interact-stars"
          movieId={props.movieId}
          size="medium"
          votable={true}
          rating={props.userRating}
          setRating={props.setUserRating}
        />
      </div>
      <div onClick={showPopupIfNotLoggedIn}>
        <a style={{textDecoration: "none"}} onClick={state.loggedIn && props.snapToReviews}>
        <ChatBubble/>
        <Typography variant="body2" display="inline">
          Post a review
        </Typography>
        </a>
      </div>
      {popupVisible ? (
        <Popup
          onClose={() => {
            setPopupVisible(false);
          }}
        >
          <div>You must be logged in to do that</div>
        </Popup>
      ) : null}
    </>
  );
};

export default view(MovieInteract);
