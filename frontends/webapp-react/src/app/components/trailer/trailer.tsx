import { view } from "@risingstack/react-easy-state";
import React from "react";
import "./trailer.scss";

type TrailerProps = {
  height?: number;
  width?: number;
  site: string;
  key: string;
};

const Trailer = (props: TrailerProps & { className?: string }) => {
  return (
    <div className={`Trailer ${(props.className || "").trim()}`}>
      
    </div>
  );
};

export default view(Trailer);
