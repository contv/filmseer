import { view } from "@risingstack/react-easy-state";
import React from "react";
import "./browse_by.scss";

type BrowseByProps = {
    Genre?:object
    Director?: object;
    Year?:object
};

const BrowseBy = (props:BrowseByProps  & { className?: string }) => {
    function handleClick_browse() {
    }
    function handleClick_year() {
    }
    function f1() {
    }
    return <div className="BrowseBy">
        <button className="dropbtn" id="BrowseByBtn" onMouseOver={f1} onClick={handleClick_browse}>Browse By</button>
        <div className="dropdown">
            <button className="dropbtn">Genre</button>
            <div className="dropdown-content">
                <div className="box">
                    <input type="checkbox" id="checkbox1"/><label htmlFor="checkbox1"> Genre_1</label>
                </div>
                <div className="line"></div>
                <div className="box">
                    <input type="checkbox" id="checkbox2"/><label htmlFor="checkbox2"> Genre_2</label>
                </div>
                <div className="line"></div>
                <div className="box">
                    <input type="checkbox" id="checkbox3"/><label htmlFor="checkbox3"> Genre_2</label>
                </div>
                <div className="line"></div>
            </div>
        </div>
        <div className="dropdown">
            <button className="dropbtn">Year</button>
            <div className="dropdown-content">
                <div><button className="content" onClick={handleClick_year}>2015</button></div>
                <div><button className="content" onClick={handleClick_year}>2016</button></div>
                <div><button className="content" onClick={handleClick_year}>2017</button></div>
            </div>
        </div>
        <div className="dropdown">
            <button className="dropbtn">Director</button>
            <div className="dropdown-content">
                <div>
                    <input className="Input" type="text"/>
                    <button className="btn2">OK</button>
                </div>
            </div>
        </div>
    </div>;
};

export default view(BrowseBy);