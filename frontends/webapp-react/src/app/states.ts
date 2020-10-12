import { store } from "@risingstack/react-easy-state";

const state: {[key: string]: any} = {
  _loggedIn:
    (localStorage.getItem("loggedIn") || "").toLowerCase().trim() === "true",
  get loggedIn(): boolean {
    return !!state._loggedIn;
  },
  set loggedIn(value: boolean) {
    localStorage.setItem("loggedIn", (!!value).toString());
    state._loggedIn = !!value;
  },
  userMenuPopupTab: "login",
};

export default store(state);
