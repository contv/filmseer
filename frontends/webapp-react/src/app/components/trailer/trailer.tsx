import { view } from "@risingstack/react-easy-state";
import React from "react";
import Popup from "src/app/popups/popup-base";
import Video from "src/app/popups/video";
import playbutton from "./playbutton.png";
import "./trailer.scss";

type TrailerProps = {
  height?: number;
  width?: number;
  site: "YouTube" | "Vimeo";
  videoId: string;
  autoPlay?: boolean;
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
    <div
      className={`Trailer ${(props.className || "").trim()} Trailer__outer`}
      style={{
        width: props.width || 360,
        height: props.height || Math.round(((props.width || 360) / 16) * 9),
      }}
    >
      <img
        src={videoThumb}
        alt={videoThumb}
        className="Trailer__thumbnail"
        onClick={() => {
          setPopupVisible(true);
        }}
      ></img>
      <div className="Trailer__inner">
        <img
          src={playbutton}
          alt="Play button"
          onClick={() => {
            setPopupVisible(true);
          }}
        />
      </div>
      {popupVisible ? (
        <Popup noPadding={true}
          onClose={() => {
            setPopupVisible(false);
          }}
        >
          <Video
            videoId={props.videoId}
            site={props.site}
            autoPlay={props.autoPlay}
            onClose={() => {
              setPopupVisible(false);
            }}
          />
        </Popup>
      ) : null}
    </div>
  );
};

export default view(Trailer);
