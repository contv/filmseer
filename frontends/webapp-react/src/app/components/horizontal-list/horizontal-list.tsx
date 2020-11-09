import { view } from "@risingstack/react-easy-state";
import React from "react";
import "./horizontal-list.scss";

type HorizontalListProps = {
  items: JSX.Element[];
  itemClassName?: string;
};

const HorizontalList = (
  props: HorizontalListProps & { className?: string }
) => {
  return (
    <ul className={`HorizontalList ${(props.className || "").trim()}`}>
      {props.items.map((el) => (
        <li
          className={`HorizontalList__item ${(
            props.itemClassName || ""
          ).trim()}`}
        >
          {el}
        </li>
      ))}
    </ul>
  );
};

export default view(HorizontalList);
