import { view } from "@risingstack/react-easy-state";
import React from "react";
import { X } from "react-feather";
import { CSSTransition } from "react-transition-group";
import state from "src/app/states";
import "./popup.scss";

type TabPopupProps = {
  tabs: {
    [key: string]: React.ReactElement<{
      onClose: () => void;
      [key: string]: any;
    }>;
  };
  tabNames?: {
    [key: string]: JSX.Element;
  };
  currentTabStateName: string;
  transitionTimeMs?: number;
  closeOnBackground?: boolean;
  onClose: () => void;
};

const TabPopup = (props: TabPopupProps & { className?: string }) => {
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
            className="Popup__close-button"
            onClick={() => setVisible(false)}
          >
            <X size={24} />
          </button>
          <ul className="Popup__tabs">
            {Object.keys(props.tabs).map((key) => (
              <li
                className={
                  key === state[props.currentTabStateName]
                    ? "Popup__tab Popup__tab--active"
                    : "Popup__tab"
                }
                onClick={() => {
                  state[props.currentTabStateName] = key;
                }}
                key={key}
              >
                {(props.tabNames || {})[key] || key}
              </li>
            ))}
          </ul>
          <div className="Popup__content">
            {state[props.currentTabStateName]
              ? React.cloneElement(
                  props.tabs[state[props.currentTabStateName]],
                  {
                    onClose: props.onClose,
                  }
                ) || null
              : null}
          </div>
        </div>
      </div>
    </CSSTransition>
  );
};

export default view(TabPopup);
