import Typography from "@material-ui/core/Typography";
import { ChatBubble } from "@material-ui/icons";
import BookmarkIcon from "@material-ui/icons/Bookmark";
import FlagIcon from "@material-ui/icons/Flag";
import VisibilityIcon from "@material-ui/icons/Visibility";
import { view } from "@risingstack/react-easy-state";
import React, { useEffect, useState } from "react";
import Stars from "src/app/components/stars";
import Popup from "src/app/popups/popup-base";
import state from "src/app/states";
import { api } from "src/utils";
import "./movie-interact.scss";

type MovieInteractProps = {
  movieId: string;
};

const MovieInteract = (props: MovieInteractProps) => {;
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
        <VisibilityIcon />
        <Typography variant="body2" display="inline">
          Watched
        </Typography>
      </div>
      <div>
        <BookmarkIcon
          onClick={onWishlist}
          style={{ fill: isWishlisted ? "green" : "black" }}
        ></BookmarkIcon>
        <Typography variant="body2" display="inline">
          {isWishlisted ? "Remove from Wishlist" : "Add to wishlist"}
        </Typography>
      </div>
      <div>
        <FlagIcon />
        <Typography variant="body2" display="inline">
          Flag inaccurate
        </Typography>
      </div>
      <div>
        <Typography variant="body2">Your rating</Typography>
        <Stars
          movieId={props.movieId}
          size="medium"
          votable={true}
        />
      </div>
      <div onClick={showPopupIfNotLoggedIn}>
        <ChatBubble/>
        <Typography variant="body2" display="inline">
          Post a review
        </Typography>
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
