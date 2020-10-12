import { view } from "@risingstack/react-easy-state";
import React from "react";
import { Search } from "react-feather";
import "./search-bar.scss";

type SearchBarProps = {
  type: string;
  height?: number;
  width?: number;
  onSearch: (text: string) => void;
};

const SearchBar = (props: SearchBarProps & { className?: string }) => {
  let textInput = React.useRef(null);
  function handleClick() {
    props.onSearch((textInput.current || { value: "" }).value);
  }
  function handleInput(event: React.KeyboardEvent<HTMLInputElement>) {
    if (event.key === "Enter") {
      props.onSearch((textInput.current || { value: "" }).value);
    }
  }
  return (
    <div
      className={`SearchBar ${(props.className || "").trim()}`}
      style={{
        width: props.width,
        height: props.height,
        gridTemplateColumns:
          "1fr " + (props.height ? props.height + "px" : "2em"),
      }}
    >
      <input
        type="text"
        name="search"
        className="SearchBar__input"
        ref={textInput}
        onKeyPress={handleInput}
        style={{
          width: props.width && props.width - (props.height || 0),
          height: props.height || "2em",
          fontSize: Math.round(((props.height || 0) / 60) * 14) * 2 || "1em",
        }}
      />
      <button
        className="SearchBar__button"
        onClick={handleClick}
        style={{
          width: props.height || "2em",
          height: props.height || "2em",
          ["--aspect-ratio" as any]: "1/1",
        }}
      >
        <Search size={Math.round(((props.height || 0) / 60) * 14) * 2 || "1em"} />
      </button>
    </div>
  );
};

export default view(SearchBar);
