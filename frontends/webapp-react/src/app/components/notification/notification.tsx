import { view } from "@risingstack/react-easy-state";
import React from "react";
import { CSSTransition } from "react-transition-group";
import state from "src/app/states";
import "./notification.scss";

type NotificationProps = {};

const Notification = (props: NotificationProps & { className?: string }) => {
  return (
    state.notifications && (
      <div className={`Notification ${(props.className || "").trim()}`}>
        {state.notifications.map((value) => {
          return (
            value && (
              <CSSTransition
                key={`${value.id}`}
                in={!value.expired}
                timeout={300}
                classNames="Notification__item-transition"
              >
                <div
                  className={`Notification__item Notification__item--${
                    value.level
                  } ${(value.className || "").trim()}`}
                >
                  {value.text}
                </div>
              </CSSTransition>
            )
          );
        })}
      </div>
    )
  );
};

export default view(Notification);
