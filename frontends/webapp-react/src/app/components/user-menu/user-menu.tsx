import "./user-menu.scss";

import { api, apiEffect } from "src/utils";

import { Link } from "react-router-dom";
import Login from "src/app/popups/login";
import React from "react";
import Register from "src/app/popups/register";
import { Settings } from "react-feather";
import TabPopup from "src/app/popups/popup-tabs";
import state from "src/app/states";
import user from "./user-icon.svg";
import { view } from "@risingstack/react-easy-state";

const UserMenu = (props: { className?: string }) => {
  const [popupVisible, setPopupVisible] = React.useState(false);

  React.useEffect(
    apiEffect(
      { path: "/session" },
      (_wrapper) => {
        if (!state.loggedIn) {
          state.loggedIn = true;
          window.location.reload();
        }
      },
      (_error) => {
        if (state.loggedIn) {
          state.loggedIn = false;
          window.location.reload();
        }
      }
    ),
    []
  );

  const doLogout = async () => {
    await api({ path: "/session", method: "DELETE" });
    state.loggedIn = false;
    window.location.reload();
  };

  if (state.loggedIn) {
    return (
      <div className={`UserMenu ${(props.className || "").trim()}`}>
        <Link to="/user" className="UserMenu__icon">
          <img src={user} alt="Profile" className="UserMenu__profile-icon" />
        </Link>
        <Link to="/settings" className="UserMenu__icon">
          <Settings className="UserMenu__profile-icon" />
        </Link>
        <button className="UserMenu__button" onClick={doLogout}>
          Sign out
        </button>
      </div>
    );
  } else {
    return (
      <div className={`UserMenu ${(props.className || "").trim()}`}>
        <button
          className="UserMenu__button"
          onClick={() => {
            state.userMenuPopupTab = "register";
            setPopupVisible(true);
          }}
        >
          Register
        </button>
        <button
          className="UserMenu__button"
          onClick={() => {
            state.userMenuPopupTab = "login";
            setPopupVisible(true);
          }}
        >
          Sign In
        </button>
        {popupVisible ? (
          <TabPopup
            tabs={{
              login: (
                <Login
                  onClose={() => {
                    setPopupVisible(false);
                  }}
                />
              ),
              register: (
                <Register
                  onClose={() => {
                    setPopupVisible(false);
                  }}
                />
              ),
            }}
            tabNames={{
              login: <span>Sign In</span>,
              register: <span>Register</span>,
            }}
            onClose={() => {
              setPopupVisible(false);
            }}
            currentTabStateName="userMenuPopupTab"
          />
        ) : null}
      </div>
    );
  }
};

export default view(UserMenu);
