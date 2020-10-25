import { view } from "@risingstack/react-easy-state";
import React from "react";
import { BrowserRouter as Router, Link, Route, Switch } from "react-router-dom";
import "./app.scss";
import SearchBar from "./components/search-bar";
import UserMenu from "./components/user-menu";
import logo from "./logo.svg";
import HomePage from "./routes/home";
import UserPage from "./routes/user";
import { StylesProvider } from "@material-ui/core/styles";
import MovieItem from "./components/movie-item"

const MovieItemProps = {
  movieId: 'ERGERTHR@#%!@',
  title: "The Hell's Evil",
  year: 2345,
  genres: [{id:"3454", text:'Historical'}, {id:"275", text:'Thriller'}, {id:"867", text:'New Age'}],
  imageUrl: "https://a.ltrbxd.com/resized/film-poster/5/7/7/5/5/5/577555-the-wolf-of-snow-hollow-0-230-0-345-crop.jpg?k=4918de4b9c",
  cumulativeRating: 5343,
  numRatings: 2666,
  numReviews: 345
};

const App = () => {
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
              onSearch={(text) => console.log("Searching", text)}
              className="Header__search-bar"
              height={48}
            ></SearchBar>
            <UserMenu className="Header__user-menu" />
          </header>

          <MovieItem {...MovieItemProps} />

          <article className="App__main Main">
            <Switch>
              <Route path="/user/:username?">
                <UserPage className="Main__user" />
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
