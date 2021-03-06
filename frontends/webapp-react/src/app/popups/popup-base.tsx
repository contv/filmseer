import { view } from "@risingstack/react-easy-state";
import React from "react";
import { X } from "react-feather";
import { CSSTransition } from "react-transition-group";
import "./popup.scss";

type PopupProps = {
  title?: React.ReactNode;
  transitionTimeMs?: number;
  closeOnBackground?: boolean;
  noPadding?: boolean;
  onClose: () => void;
};

const Popup: React.FC<PopupProps & { className?: string }> = (props) => {
  const [visible, setVisible] = React.useState(true);
  const nodeRef = React.useRef(null);
  return (
    <CSSTransition
      in={visible}
      nodeRef={nodeRef}
      timeout={Math.round(props.transitionTimeMs || 200)}
      classNames="Popup__wrapper-"
      onExited={() => props.onClose()}
      className={`Popup__wrapper ${(props.className || "").trim()}`}
    >
      <div>
        <div
          className="Popup__background"
          onClick={() => !props.closeOnBackground && setVisible(false)}
        ></div>
        <div className="Popup">
          <button
            className={
              "Popup__close-button" +
              (props.title ? "" : " Popup__close-button--no-title")
            }
            onClick={() => setVisible(false)}
          >
            <X size={34} />
          </button>
          {props.title ? (
            <div className="Popup__title">{props.title}</div>
          ) : null}
          <div
            className={
              "Popup__content" +
              (props.title ? "" : " Popup__content--no-title") +
              (props.noPadding ? " Popup__content--no-padding" : "")
            }
          >
            {React.Children.map(props.children, (child) => {
              if (React.isValidElement(child)) {
                return React.cloneElement(child, { onClose: props.onClose });
              }
            })}
          </div>
        </div>
      </div>
    </CSSTransition>
  );
};

export default view(Popup);
