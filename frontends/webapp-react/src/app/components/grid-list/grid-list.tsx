import { view } from "@risingstack/react-easy-state";
import React from "react";
import "./grid-list.scss";

type GridListProps = {
  items: JSX.Element[];
  // You may change the flow direction by overriding its CSS
};

const GridList = (props: GridListProps & { className?: string }) => {
  return <ul className={`GridList ${(props.className || "").trim()}`}>
    {props.items.map((el) => <li className="GridList__item">{el}</li>)}
  </ul>;
};

export default view(GridList);