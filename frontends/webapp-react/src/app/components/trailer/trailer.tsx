import { view } from "@risingstack/react-easy-state";
import React from "react";
import "./trailer.scss";
// @ts-ignore
import ModalVideo from 'react-modal-video';

type TrailerProps = {
  height?: number;
  width?: number;
  site: string;
  videoid: string;
};

const Trailer = (props: TrailerProps & { className?: string }) => {
  return (
    <div className={`Trailer ${(props.className || "").trim()}`}>
      
    </div>
  );
};

export default view(Trailer);
