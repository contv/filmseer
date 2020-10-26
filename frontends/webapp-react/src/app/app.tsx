import { view } from "@risingstack/react-easy-state";
import React from "react";
import { BrowserRouter as Router, Link, Route, Switch } from "react-router-dom";
import "./app.scss";
import SearchBar from "./components/search-bar";
import UserMenu from "./components/user-menu";
import logo from "./logo.svg";
import HomePage from "./routes/home";
import MovieDetailPage from "./routes/movie";
import UserPage from "./routes/user";
import BrowseBy from "./components/browse_by"

const App = () => {
  return (
    <div className="App">
      <Router>
        <header className="App__header Header">
          <Link to="/" className="Header__logo">
            <img src={logo} alt="FilmSeer" className="Header__logo-image" />
          </Link>
          <SearchBar
            type="header"
            onSearch={(text) => console.log("Searching", text)}
            className="Header__search-bar"
            height={48}
          ></SearchBar>
          <UserMenu className="Header__user-menu" />
        </header>
        <article className="App__main Main">
          <Switch>
            <Route path="/user/:username?">
              <UserPage className="Main__user" />
            </Route>
            <Route path="/movie/:movieId?">
              <MovieDetailPage className="Main__movie" />
            </Route>
            <Route path="/">
              <HomePage className="Main__home" />
            </Route>
          </Switch>
        </article>
      </Router>
        <BrowseBy/>

    </div>
  );
};

export default view(App);
