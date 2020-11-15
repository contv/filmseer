import Typography from "@material-ui/core/Typography";
import { view } from "@risingstack/react-easy-state";
import React from "react";
import { useHistory } from "react-router-dom";
import "./genre-tile.scss";
import { baseUrl } from "src/utils";

type GenreTileProps = {
  id: string;
  text: string;
};

const GenreTile = (props: GenreTileProps & { className?: string }) => {
  const history = useHistory();
  const searchByGenre = (event: React.MouseEvent) => {
    event.stopPropagation();
    event.preventDefault();
    event.nativeEvent.stopImmediatePropagation();
    event.nativeEvent.preventDefault();
    history.push(`${(new URL(baseUrl)).pathname}search/genres/${props.text}`);
  };
  return (
    <div
      className={`GenreTile ${(props.className || "").trim()}`}
      onClick={searchByGenre}
    >
      <Typography variant="body2" display="inline">
        {props.text}
      </Typography>
    </div>
  );
};

export default view(GenreTile);
