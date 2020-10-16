import { view } from "@risingstack/react-easy-state";
import React from "react";
import "./video.scss";

type VideoProps = {
  videoId: string;
  site: "YouTube" | "Vimeo";
  frameBorder?: number;
  onClose: () => void;
};

const Video = (props: VideoProps & { className?: string }) => {
  if (props.site === "YouTube") {
    var youtubeLink =
      "https://www.youtube.com/embed/" + props.videoId + "?autoplay=1";
    return (
      <div className={`Video ${(props.className || "").trim()}`}>
        <iframe
          className="Video__iframe"
          title="Youtube Trailer"
          allowFullScreen
          frameBorder={props.frameBorder || 0}
          src={youtubeLink}
        ></iframe>
      </div>
    );
  }
  //TO DO: VIMEO
  else {
    return <div></div>;
  }
};

export default view(Video);
