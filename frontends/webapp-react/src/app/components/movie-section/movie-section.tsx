import { view } from "@risingstack/react-easy-state";
import React from "react";
import "./movie-section.scss";

const MovieSection = (props: { children: React.ReactNode;  heading?: String}) => 
    <div className="MovieSection">
      {props.heading && <h2 className="MovieSection__Heading">{props.heading}</h2>}
      {props.children}
    </div>

export default view(MovieSection);
