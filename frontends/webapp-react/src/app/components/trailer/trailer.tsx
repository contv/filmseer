import { view } from "@risingstack/react-easy-state";
import React from "react";
import TabPopup from "src/app/popups/popup-tabs";
import Video from "src/app/popups/video";
import state from "src/app/states";
import playbutton from "./playbutton.png";
import "./trailer.scss";

type TrailerProps = {
  height?: number;
  width?: number;
  site: "YouTube" | "Vimeo";
  videoId: string;
  autoPlay?: "0" | "1";
};

const Trailer = (props: TrailerProps & { className?: string }) => {
  const [popupVisible, setPopupVisible] = React.useState(false);
  var videoThumb;
  if (props.site === "YouTube") {
    videoThumb = "https://img.youtube.com/vi/" + props.videoId + "/0.jpg";
  } else {
    videoThumb = "https://vumbnail.com/" + props.videoId + ".jpg";
  }
  return (
    <div className={`Trailer ${(props.className || "").trim()} Trailer__outer`}>
      <img
        src={videoThumb}
        alt={videoThumb}
        className="Trailer__thumbnail"
        onClick={() => {
          state.videoPopupTab = "trailer";
          setPopupVisible(true);
        }}
      ></img>
      <div className="Trailer__inner">
        <img
          src={playbutton}
          alt="Play button"
          onClick={() => {
            state.videoPopupTab = "trailer";
            setPopupVisible(true);
          }}
        />
      </div>
      {popupVisible ? (
        <TabPopup
          tabs={{
            trailer: (
              <Video
                videoId={props.videoId}
                site={props.site}
                autoPlay={props.autoPlay}
                onClose={() => {
                  setPopupVisible(false);
                }}
              />
            ),
          }}
          onClose={() => {
            setPopupVisible(false);
          }}
          tabNames={{
            trailer: <span>Trailer</span>,
          }}
          currentTabStateName="videoPopupTab"
        />
      ) : null}
    </div>
  );
};

export default view(Trailer);
