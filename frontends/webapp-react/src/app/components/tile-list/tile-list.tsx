import { view } from "@risingstack/react-easy-state";
import React from "react";
import "./tile-list.scss";

type TileListProps = {
  items: JSX.Element[];
  // You may change the flow direction by overriding its CSS
};

const TileList = (props: TileListProps & { className?: string }) => {
  return <ul className={`TileList ${(props.className || "").trim()}`}>
    {props.items.map((el) => <li className="TileList__item">{el}</li>)}
  </ul>;
};

export default view(TileList);