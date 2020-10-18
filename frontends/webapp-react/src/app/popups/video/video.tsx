import { view } from "@risingstack/react-easy-state";
import React from "react";
import "./video.scss";

type VideoProps = {
  videoId: string;
  site: "YouTube" | "Vimeo";
  frameBorder?: number;
  autoPlay?: boolean;
  onClose: () => void;
};

const Video = (props: VideoProps & { className?: string }) => {
  if (props.site === "YouTube") {
    let youtubeLink =
      "https://www.youtube.com/embed/" +
      props.videoId +
      "?autoplay=" +
      (props.autoPlay === undefined || props.autoPlay ? "1" : "0"); // if autoPlay is undefined, change it to true because trailer should play automatically
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
  } else {
    let vimeoLink =
      "https://player.vimeo.com/video/" +
      props.videoId +
      "?autoplay=" +
      (props.autoPlay === undefined || props.autoPlay ? "1" : "0"); // if autoPlay is undefined, change it to true because trailer should play automatically
    return (
      <div className={`Video ${(props.className || "").trim()}`}>
        <iframe
          className="Video__iframe"
          title="Vimeo Trailer"
          allowFullScreen
          frameBorder={props.frameBorder || 0}
          src={vimeoLink}
        ></iframe>
      </div>
    );
  }
};

export default view(Video);
