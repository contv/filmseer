import { view } from "@risingstack/react-easy-state";
import React from "react";
import "./video.scss";

type VideoProps = {
  videoId: string;
  site: "YouTube" | "Vimeo";
  frameBorder?: number;
  autoPlay?: "0" | "1";
  onClose: () => void;
};

const Video = (props: VideoProps & { className?: string }) => {
  if (props.site === "YouTube") {
    var youtubeLink =
      "https://www.youtube.com/embed/" +
      props.videoId +
      "?autoplay=" +
      (props.autoPlay || 1);
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
    var vimeoLink =
      "https://player.vimeo.com/video/" +
      props.videoId +
      "?autoplay=" +
      (props.autoPlay || 1);
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
