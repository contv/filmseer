import { view } from "@risingstack/react-easy-state";
import React from "react";
import Typography from '@material-ui/core/Typography';
import "./genre-tile.scss";

type GenreTileProps = {
  text: string;
};

const GenreTile = (props: GenreTileProps & { className?: string }) => {
  return (
    <div className={`GenreTile ${(props.className || "").trim()}`}>
      <Typography variant="subtitle1" display="inline" >{props.text}</Typography>
    </div>
  );
};

export default view(GenreTile);
