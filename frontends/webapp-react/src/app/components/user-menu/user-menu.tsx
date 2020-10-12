import { view } from "@risingstack/react-easy-state";
import React from "react";
import { Settings } from "react-feather";
import Login from "src/app/popups/login";
import TabPopup from "src/app/popups/popup-tabs";
import Register from "src/app/popups/register";
import state from "src/app/states";
import { api, apiEffect } from "src/utils";
import user from "./user-icon.svg";
import "./user-menu.scss";

const UserMenu = (props: {className?: string}) => {
  const [popupVisible, setPopupVisible] = React.useState(false);

  React.useEffect(
    apiEffect(
      { path: "/session" },
      (_wrapper) => {
        state.loggedIn = true;
      },
      (_error) => {
        state.loggedIn = false;
      }
    ),
    []
  );

  const doLogout = async () => {
    await api({ path: "/session", method: "DELETE" });
    state.loggedIn = false;
  };

  if (state.loggedIn) {
    return (
      <div className={`UserMenu ${(props.className || "").trim()}`}>
        <button className="UserMenu__icon">
          <img src={user} alt="Profile" className="UserMenu__profile-icon" />
        </button>
        <button className="UserMenu__icon">
          <Settings className="UserMenu__profile-icon" />
        </button>
        <button className="UserMenu__button" onClick={doLogout}>
          Sign out
        </button>
      </div>
    );
  } else {
    return (
      <div className={`UserMenu ${(props.className || "").trim()}`}>
      <button className="UserMenu__icon">
        <img src={user} alt="Profile" className="UserMenu__profile-icon" />
      </button>
      <button className="UserMenu__icon">
        <Settings className="UserMenu__profile-icon" size={1000} />
      </button>
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
