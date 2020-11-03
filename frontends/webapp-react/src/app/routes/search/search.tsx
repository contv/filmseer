import { view } from "@risingstack/react-easy-state";
import React from "react";
import { useParams } from "react-router-dom";
import state from "src/app/states";
import "./search.scss";

const SearchPage = (props: { className?: string }) => {
  const { searchString } = useParams<{ searchString?: string }>();

  return (
    <div className={`SearchPage ${(props.className || "").trim()}`}>
      Search {searchString}
    </div>
  );
};

export default view(SearchPage);
