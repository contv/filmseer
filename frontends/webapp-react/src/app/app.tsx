import "./app.scss";

import {
  Link,
  Redirect,
  Route,
  BrowserRouter as Router,
  Switch,
} from "react-router-dom";
import React, { useState } from "react";

import HomePage from "./routes/home";
import MovieDetailPage from "./routes/movie";
import SearchBar from "./components/search-bar";
import SearchPage from "./routes/search";
import SettingsPage from "./routes/settings";
import { StylesProvider } from "@material-ui/core/styles";
import UserMenu from "./components/user-menu";
import UserPage from "./routes/user";
import logo from "./logo.svg";
import { view } from "@risingstack/react-easy-state";

const App = () => {
  const [searchTerm, setSearchTerm] = useState<string>();
  const [suggestionTerm, setSuggestionTerm] = useState<string>();

  const performSearch = (text: string) => {
    setSearchTerm(encodeURI(text));
  };

  const performSelectSuggestion = (text: string) => {
    setSuggestionTerm(encodeURI(text));
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
              onSelectSuggestion={(text) => performSelectSuggestion(text)}
              className="Header__search-bar"
              height={48}
            ></SearchBar>
            <UserMenu className="Header__user-menu" />
          </header>
          <article className="App__main Main">
              {searchTerm && (<Redirect to={{ pathname: `/search/${searchTerm}`}}/>)}
              {suggestionTerm && (<Redirect to={{ pathname: `/movie/${suggestionTerm}`}}/>)}
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
              <Route path="/settings/:username?">
                <SettingsPage className="Main__settings" />
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
