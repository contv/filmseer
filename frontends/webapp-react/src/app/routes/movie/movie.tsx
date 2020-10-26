import { view } from "@risingstack/react-easy-state";
import React from "react";
import "./movie.scss";

const MovieDetailPage = (props: { className?: string }) => {
  return (
    <div className={`MovieDetailPage ${(props.className || "").trim()}`}/>
  )
}

export default view(MovieDetailPage);
