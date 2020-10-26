import { view } from "@risingstack/react-easy-state";
import React from "react";
import "./horizontal-list.scss";

type HorizontalListProps = {
  items: JSX.Element[];
};

const HorizontalList = (props: HorizontalListProps & { className?: string }) => {
  return <ul className={`HorizontalList ${(props.className || "").trim()}`}>
    {props.items.map((el) => <li className="HorizontalList__item">{el}</li>)}
  </ul>;
};

export default view(HorizontalList);