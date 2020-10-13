import { view } from "@risingstack/react-easy-state";
import React from "react";
import state from "src/app/states";
import { api, ApiError } from "src/utils";
import "./login.scss";

type LoginProps = {
  onClose: () => void;
};

const Login = (props: LoginProps & { className?: string }) => {
  const username = React.useRef(null);
  const password = React.useRef(null);
  const [hasError, setHasError] = React.useState(false);
  const [message, setMessage] = React.useState({ code: 0, message: "" });
  const [exceptions, setExceptions] = React.useState<string[]>([]);
  const submitLogin = async (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
    event.stopPropagation();
    event.nativeEvent.stopImmediatePropagation();
    try {
      if (state.loggedIn) {
        await api({ path: "/session", method: "DELETE" });
        state.loggedIn = false;
      }
      if (
        ((username.current || { value: "" }).value || "").toString().trim()
          .length <= 0
      ) {
        throw new ApiError({
          message: "Username should not be empty",
          code: 1001,
        });
      }
      if (
        ((password.current || { value: "" }).value || "").toString().length <= 0
      ) {
        throw new ApiError({
          message: "Password should not be empty",
          code: 1011,
        });
      }
      await api({
        path: "/session",
        method: "POST",
        body: {
          username: (username.current || { value: "" }).value,
          password: (password.current || { value: "" }).value,
        },
      });
      state.loggedIn = true;
      props.onClose();
    } catch (error) {
      if (!(error instanceof ApiError)) {
        throw error;
      }
      setHasError(error.code !== 0);
      setMessage({ code: error.code, message: error.message });
      setExceptions(error.exceptions.map((e) => `${e.message} (${e.code})`));
    }
  };

  return (
    <div className={`Login ${(props.className || "").trim()}`}>
      <form action="" method="POST" className="Login__form">
        <div className="Login__form-field">
          <label htmlFor="username" className="Login__form-label">
            Username
          </label>
          <input
            type="text"
            name="username"
            ref={username}
            className="Login__form-input"
            placeholder="Your username"
          />
        </div>
        <div className="Login__form-field">
          <label htmlFor="password" className="Login__form-label">
            Password
          </label>
          <input
            type="password"
            name="password"
            ref={password}
            className="Login__form-input"
            placeholder="Your password"
          />
        </div>
        {(hasError || message.message) ? (
          <ul className="Login__form-messages">
            <li
              className={`Login__form-message ${
                message.code > 0
                  ? "Login__form-message--error"
                  : "Login__form-message--success"
              }`}
              key="message"
            >
              {message.message} {message.code > 0 ? `(${message.code})` : ""}
            </li>
            {exceptions.map((value, index) => (
              <li
                className="Login__form-message Login__form-message--error"
                key={"exception-" + index.toString()}
              >
                {value}
              </li>
            ))}
          </ul>
        ) : null}
        <div className="Login__form-actions">
          <button className="Login__form-button" onClick={submitLogin}>
            Sign In
          </button>
        </div>
      </form>
    </div>
  );
};

export default view(Login);
