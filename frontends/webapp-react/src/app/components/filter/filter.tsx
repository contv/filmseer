import { view } from "@risingstack/react-easy-state";
import React from "react";
import "./filter.scss";

type FilterProps = {
  filterKey: string;
  type: string;
  name: string;
  selections: { key: string; name: string }[];
};

const Filter = (props: FilterProps & { className?: string } & {updateSearchParams: any}) => {
  return (
    <div className={`GenreTile ${(props.className || "").trim()}`}>
      {props.type === "list" ? (
        <>
          <label htmlFor={props.filterKey} >
            {props.name}
          </label>
          <select name={props.filterKey} id={props.filterKey} onChange={props.updateSearchParams}>
            <option key="none" value={""}>Select a {props.filterKey}</option>
            {props.selections.map((selection) => (
              <option key={selection.key} value={selection.key}>
                {selection.name}
              </option>
            ))}
          </select>
        </>
      ) : null}
    </div>
  );
};

export default view(Filter);
