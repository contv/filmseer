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
import { baseUrl } from "src/utils";
import "./app.scss";
import Notification from "./components/notification";
import SearchBar from "./components/search-bar";
import UserMenu from "./components/user-menu";
import logo from "./logo.svg";
import HomePage from "./routes/home";
import MovieDetailPage from "./routes/movie";
import SearchPage from "./routes/search";
import SettingsPage from "./routes/settings";
import UserPage from "./routes/user";

const App = () => {
  const [searchTerm, setSearchTerm] = useState<string>();
  const [suggestionTerm, setSuggestionTerm] = useState<string>();
  const [field, setField] = useState<string>();
  const performSearch = (text: string) => {
    setSearchTerm(encodeURI(text));
  };

  const performSelectSuggestion = (text: string) => {
    setSuggestionTerm(encodeURI(text));
  };

  const performSetField = (text: string) => {
    setField(text);
  };

  return (
    <StylesProvider injectFirst>
      <div className="App">
        <Router basename={new URL(baseUrl).pathname.replace(/\/+$/, "")}>
          <Notification />
          <header className="App__header Header">
            <Link to="/" className="Header__logo">
              <img src={logo} alt="FilmSeer" className="Header__logo-image" />
            </Link>
            <Switch>
              <Route
                path="/search/:searchField?/:searchString?"
                render={() => (
                  <SearchBar
                    type="header"
                    onSearch={(text) => performSearch(text)}
                    onSelectSuggestion={(text) => performSelectSuggestion(text)}
                    onField={(text) => performSetField(text)}
                    className="Header__search-bar"
                    height={48}
                  ></SearchBar>
                )}
              />
              <Route
                render={() => (
                  <SearchBar
                    type="header"
                    onSearch={(text) => performSearch(text)}
                    onSelectSuggestion={(text) => performSelectSuggestion(text)}
                    onField={(text) => performSetField(text)}
                    className="Header__search-bar"
                    height={48}
                  ></SearchBar>
                )}
              />
            </Switch>
            <UserMenu className="Header__user-menu" />
          </header>
          <article className="App__main Main">
            {searchTerm && (
              <Redirect to={{ pathname: `/search/${field}/${searchTerm}` }} />
            )}
            {suggestionTerm && (
              <Redirect to={{ pathname: `/movie/${suggestionTerm}` }} />
            )}
            <Switch>
              <Route path="/search/:searchField?/:searchString?">
                <SearchPage className="Main__search" />
              </Route>
              <Route path="/user/:username">
                <UserPage className="Main__user" />
              </Route>
              <Route path="/user">
                <UserPage className="Main__user Main__user-1" />
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
        <footer className="Footer">
          <a href="/" ><img src="/static/media/logo.5e491f07.svg" alt="FilmSeer" className="Footer__logo-image"/></a>
          <div className="Footer__authors">
            <h4>Authors</h4>
            <p className="Footer__author">Con Tieu-Vinh - z5245136</p>
            <p className="Footer__author">Daheng Wang - z5234730 </p>
            <p className="Footer__author">Mengfan Huang - z5148963</p>
            <p className="Footer__author">Minh Phuong Nguyen - z5234456</p>
            <p className="Footer__author">Tom Hagis - z5149234</p>
          </div>
        </footer>
      </div>
    </StylesProvider>
  );
};

export default view(App);
