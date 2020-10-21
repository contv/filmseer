import { view } from "@risingstack/react-easy-state";
import React from "react";
import "./browse_by.scss";

type BrowseByProps = {
    Genre?:object
    Director?: object;
    Year?:object
};

const BrowseBy = (props:BrowseByProps  & { className?: string }) => {
    function handleClick() {

    }
    return <div className="BrowseBy">
        <div className="dropdown">
            <button className="dropbtn">Browse By</button>
            <div className="dropdown-content">
                <div className="box">
                    <input type="checkbox" id="checkbox1"/><label htmlFor="checkbox1"> Genre</label>
                </div>
                <div className="line"></div>
                <div className="box">
                    <input type="checkbox" id="checkbox2"/><label htmlFor="checkbox2"> Year</label>
                </div>
                <div className="line"></div>
                <div className="box">
                    <input type="checkbox" id="checkbox3"/><label htmlFor="checkbox3"> Director</label>
                </div>
                <div className="line"></div>
            </div>
        </div>
        <div className="dropdown">
            <button className="dropbtn">Genre</button>
            <div className="dropdown-content">
                <div><button className="content" onClick={handleClick}>Genre_1</button></div>
                <div><button className="content" onClick={handleClick}>Genre_2</button></div>
                <div><button className="content" onClick={handleClick}>Genre_3</button></div>
            </div>
        </div>
        <div className="dropdown">
            <button className="dropbtn">Year</button>
            <div className="dropdown-content">
                <div><button className="content" onClick={handleClick}>2015</button></div>
                <div><button className="content" onClick={handleClick}>2016</button></div>
                <div><button className="content" onClick={handleClick}>2017</button></div>
            </div>
        </div>
        <div className="dropdown">
            <button className="dropbtn">Director</button>
            <div className="dropdown-content">
                <div><button className="content"onClick={handleClick}>Director_1</button></div>
                <div><button className="content"onClick={handleClick}>Director_2</button></div>
                <div><button className="content"onClick={handleClick}>Director_3</button></div>
            </div>
        </div>
    </div>;
};

export default view(BrowseBy);