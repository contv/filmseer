import { StylesProvider } from "@material-ui/core/styles";
import { view } from "@risingstack/react-easy-state";
import React, { useState } from "react";
import {
  BrowserRouter as Router,
  Link,
  Redirect,
  Route,
  Switch,
} from "react-router-dom";
import "./app.scss";
import SearchBar from "./components/search-bar";
import UserMenu from "./components/user-menu";
import logo from "./logo.svg";
import HomePage from "./routes/home";
import MovieDetailPage from "./routes/movie";
import SearchPage from "./routes/search";
import UserPage from "./routes/user";

const App = () => {
  const [searchTerm, setSearchTerm] = useState<string>();

  const performSearch = (text: string) => {
    setSearchTerm(encodeURI(text));
  };

  return (
    <StylesProvider injectFirst>
      <div className="App">
        <Router>
          <header className="App__header Header">
            <Link to="/" className="Header__logo">
              <img src={logo} alt="FilmSeer" className="Header__logo-image" />
            </Link>
            <SearchBar
              type="header"
              onSearch={(text) => performSearch(text)}
              className="Header__search-bar"
              height={48}
            ></SearchBar>
            <UserMenu className="Header__user-menu" />
          </header>
          <article className="App__main Main">
              {searchTerm && (<Redirect to={{ pathname: `/search/${searchTerm}`}}/>)}
            <Switch>
              <Route path="/search/:searchString?">
                <SearchPage className="Main__search" />
              </Route>
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
      </div>
    </StylesProvider>
  );
};

export default view(App);
