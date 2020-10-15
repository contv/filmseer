import { view } from "@risingstack/react-easy-state";
import React from "react";
import "./section.scss";

const Section = (props: { children: React.ReactNode;  heading?: String}) => 
    <div className="Section">
      {props.heading && <h2 className="Heading">{props.heading}</h2>}
      {props.children}
    </div>

export default view(Section);
