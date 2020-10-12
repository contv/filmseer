import { view } from "@risingstack/react-easy-state";
import React from "react";
import { useParams } from "react-router-dom";
import state from "src/app/states";
import "./user.scss";

const UserPage = (props: {className?: string}) => {
  const { username } = useParams<{ username?: string }>();
  return (
    <div className={`UserPage ${(props.className || "").trim()}`}>
      User Profile {state.loggedIn ? "Logged in" : "Not Logged in"}{" "}
      {!username ? "My Profile" : username + "'s Profile"}
    </div>
  );
};

export default view(UserPage);
