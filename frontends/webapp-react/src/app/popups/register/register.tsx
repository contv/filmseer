import { view } from "@risingstack/react-easy-state";
import React from "react";
import state from "src/app/states";
import { api, ApiError } from "src/utils";
import "./register.scss";

type RegisterProps = {
  onClose: () => void;
};

const Register = (props: RegisterProps & { className?: string }) => {
  const username = React.useRef(null);
  const password = React.useRef(null);
  const passwordRepeat = React.useRef(null);
  const acceptEula = React.useRef(null);
  const [hasError, setHasError] = React.useState(false);
  const [message, setMessage] = React.useState({ code: 0, message: "" });
  const [exceptions, setExceptions] = React.useState<string[]>([]);
  const submitRegister = async (event: React.MouseEvent<HTMLButtonElement>) => {
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
          code: 1101,
        });
      }
      if (
        ((username.current || { value: "" }).value || "").toString().trim()
          .length < 3
      ) {
        throw new ApiError({
          message: "Username should have at least 3 characters",
          code: 1102,
        });
      }
      if (
        ((username.current || { value: "" }).value || "").toString().trim()
          .length > 16
      ) {
        throw new ApiError({
          message: "Username should not have more than 16 characters",
          code: 1103,
        });
      }
      if (
        ((username.current || { value: "" }).value || "")
          .toString()
          .match(/[^a-z0-9_]/i) !== null
      ) {
        throw new ApiError({
          message: "Username can only have A-Z, a-z, underscores and 0-9",
          code: 1104,
        });
      }
      if (
        ((password.current || { value: "" }).value || "").toString().length <= 0
      ) {
        throw new ApiError({
          message: "Password should not be empty",
          code: 1111,
        });
      }
      if (
        ((password.current || { value: "" }).value || "").toString().length < 6
      ) {
        throw new ApiError({
          message: "Password should have at least 6 characters",
          code: 1112,
        });
      }
      if (
        ((password.current || { value: "" }).value || "").toString().length >=
        21
      ) {
        throw new ApiError({
          message: "Password should be less than 21 characters",
          code: 1113,
        });
      }
      if (
        (passwordRepeat.current || { value: NaN }).value !==
        (password.current || { value: NaN }).value
      ) {
        throw new ApiError({ message: "Passwords don't match", code: 1121 });
      }
      if ((acceptEula.current || { checked: false }).checked) {
        throw new ApiError({ message: "You must accept our EULA", code: 1131 });
      }
      await api({
        path: "/user",
        method: "POST",
        body: {
          username: (username.current || { value: "" }).value,
          password: (password.current || { value: "" }).value,
        },
      });
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
    <div className={`Register ${(props.className || "").trim()}`}>
      <form action="" method="POST" className="Register__form">
        <div className="Register__form-field">
          <label htmlFor="username" className="Register__form-label">
            Username
          </label>
          <input
            type="text"
            name="username"
            ref={username}
            className="Register__form-input"
            placeholder="Your username"
          />
        </div>
        <div className="Register__form-field">
          <label htmlFor="password" className="Register__form-label">
            Password
          </label>
          <input
            type="password"
            name="password"
            ref={password}
            className="Register__form-input"
            placeholder="Your password"
          />
        </div>
        <div className="Register__form-field">
          <label htmlFor="password-repeat" className="Register__form-label">
            Repeat Password
          </label>
          <input
            type="password"
            name="password-repeat"
            ref={passwordRepeat}
            className="Register__form-input"
            placeholder="Repeat your password"
          />
        </div>
        <div className="Register__form-field Register__form-field--checkbox">
          <input
            type="checkbox"
            name="eula"
            ref={acceptEula}
            className="Register__form-input Register__form-input--checkbox"
          />
          <label
            htmlFor="eula"
            className="Register__form-label Register__form-label--checkbox"
          >
            I accept the EULA.
          </label>
        </div>

        {hasError ? (
          <ul className="Register__form-messages">
            <li
              className={`Register__form-message ${
                message.code > 0
                  ? "Login__form-message--error"
                  : "Login__form-message--success"
              }`}
              key="message"
            >
              {message.message} ({message.code})
            </li>
            {exceptions.map((value) => (
              <li className="Register__form-message Register__form-message--error">
                {value}
              </li>
            ))}
          </ul>
        ) : null}
        <div className="Register__form-actions">
          <button className="Register__form-button" onClick={submitRegister}>
            Register
          </button>
          <button
            className="Register__form-button"
            onClick={(event) => {
              event.preventDefault();
              event.stopPropagation();
              event.nativeEvent.stopImmediatePropagation();
              (username.current || { value: "" }).value = "";
              (password.current || { value: "" }).value = "";
              (passwordRepeat.current || { value: "" }).value = "";
              (acceptEula.current || { checked: false }).checked = false;
            }}
          >
            Clear
          </button>
        </div>
      </form>
    </div>
  );
};

export default view(Register);
