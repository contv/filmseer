import { view } from "@risingstack/react-easy-state";
import React from "react";
import "./stars.scss";

type StarsProps = {
  size: "small" | "medium" | "large";
  type: "static" | "votable"
  rating?: number;
  onClick?: () => void;
};

const Stars = (props: StarsProps & { className?: string }) => {
  return <div className={`Stars ${(props.className || "").trim()}`}></div>;
};

export default view(Stars);
