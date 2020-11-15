import "./filter.scss";

import Autocomplete from "@material-ui/lab/Autocomplete";
import Popper from "@material-ui/core/Popper";
import React from "react";
import TextField from "@material-ui/core/TextField";
import { view } from "@risingstack/react-easy-state";

type FilterProps = {
  filterKey: string;
  type: string;
  name: string;
  selections: { key: string; name: string }[];
};

const Filter = (
  props: FilterProps & { className?: string } & { updateSearchParams: any }
) => {
  const PopperItem = function (props: any) {
    return (<Popper {...props} style={{ width: 'fit-content' }} />)
  }
  
  return (
    <div className={`GenreTile ${(props.className || "").trim()}`}>
      <Autocomplete
        multiple
        fullWidth
        PopperComponent = {PopperItem}
        options={props.selections}
        getOptionLabel={(option) => option.name}
        renderInput={(params) => (
          <TextField {...params} fullWidth label={props.name} variant="outlined" />
        )}
        onChange={(event, values) => {
          props.updateSearchParams(values);
        }}
        getOptionSelected={(option, value) => option.name === value.name}
      />
    </div>
  );
};

export default view(Filter);
