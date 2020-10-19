import { view } from "@risingstack/react-easy-state";
import React from "react";
import "./genre-tile.scss";

type GenreTileProps = {
  id: string;
  text: string;
  onClick?: () => void;
};

const GenreTile = (props: GenreTileProps & { className?: string }) => {
  return (
    <li className={`GenreTile ${(props.className || "").trim()}`}>
      {props.text}
    </li>
  );
};

export default view(GenreTile);
