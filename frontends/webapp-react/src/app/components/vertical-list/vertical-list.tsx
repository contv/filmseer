import { view } from "@risingstack/react-easy-state";
import React from "react";
import "./vertical-list.scss";

type VerticalListProps = {
  items: JSX.Element[];
  itemClassName?: string;
};

const VerticalList = (props: VerticalListProps & { className?: string }) => {
  return (
    <ul className={`VerticalList ${(props.className || "").trim()}`}>
      {props.items.map((el, index) => (
        <li
          className={`VerticalList__item ${(props.itemClassName || "").trim()}`}
          key={`${index}`}
        >
          {el}
        </li>
      ))}
    </ul>
  );
};

export default view(VerticalList);
