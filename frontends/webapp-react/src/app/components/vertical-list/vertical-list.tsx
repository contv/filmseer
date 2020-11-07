import { view } from "@risingstack/react-easy-state";
import React from "react";
import "./vertical-list.scss";

type VerticalListProps = {
  items: JSX.Element[];
};

const VerticalList = (props: VerticalListProps & { className?: string }) => {
  return (
    <ul className={`VerticalList ${(props.className || "").trim()}`}>
      {props.items.map((el, index) => (
        <li className="VerticalList__item" key={`${index}`}>
          {el}
        </li>
      ))}
    </ul>
  );
};

export default view(VerticalList);
