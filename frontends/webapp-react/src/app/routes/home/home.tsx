import { view } from "@risingstack/react-easy-state";
import React from "react";
import state from "src/app/states";
import "./home.scss";

const HomePage = (props: {className?: string}) => {
  return (
    <div className={`HomePage ${(props.className || "").trim()}`}>
      HomePage {state.loggedIn ? "Logged in" : "Not Logged in"}
    </div>
  );
};

export default view(HomePage);
