import { store } from "@risingstack/react-easy-state";
import { ReactNode } from "react";

const notifications: ({
  id: number;
  text: ReactNode;
  time: number;
  level: "warning" | "error" | "info";
  className?: string;
  timeoutHandler?: number;
  expired?: boolean;
} | null)[] = [];

const state = {
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
  notifications: notifications,
};

export default store(state);
