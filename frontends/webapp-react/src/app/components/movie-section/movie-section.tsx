import "./movie-section.scss";

import React from "react";
import { view } from "@risingstack/react-easy-state";

const MovieSection = (props: { children: React.ReactNode;  heading?: String}) => 
    <div className="MovieSection">
      {props.heading && <h2 className="MovieSection__Heading">{props.heading}</h2>}
      <div className="MovieSection__Child">{props.children}</div>
    </div>

export default view(MovieSection);
