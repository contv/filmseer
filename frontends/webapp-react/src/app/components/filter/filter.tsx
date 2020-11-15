import "./filter.scss";

import Autocomplete from '@material-ui/lab/Autocomplete';
import React from "react";
import TextField from '@material-ui/core/TextField';
import { view } from "@risingstack/react-easy-state";

type FilterProps = {
  filterKey: string;
  type: string;
  name: string;
  selections: { key: string; name: string }[];
};

const Filter = (props: FilterProps & { className?: string } & {updateSearchParams: any}) => {
  return (
    <div className={`GenreTile ${(props.className || "").trim()}`}>

    <Autocomplete
      multiple
      id="combo-box-demo"
      options={props.selections}
      getOptionLabel={(option) => option.name}
      renderInput={(params) => <TextField {...params} label={props.name} variant="outlined" />}
      onChange={ (event, values) => {props.updateSearchParams(values)} }
      getOptionSelected={(option, value) => option.name === value.name }
    />



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
    </div>
  );
};

export default view(Filter);
