import { view } from "@risingstack/react-easy-state";
import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import Filter from "src/app/components/filter";
import MovieItem from "src/app/components/movie-item/movie-item";
import movieLogo from "src/app/components/movie-item/movie-logo.png";
import TileList from "src/app/components/tile-list";
import Pagination from "src/app/components/pagination";
import { api } from "src/utils";
import "./search.scss";

type SearchItem = {
  id: string;
  title: string;
  releaseYear: number;
  genres: string[];
  imageUrl?: string;
  averageRating: number;
  numVotes: number;
  cumulativeRating: number;
};

const SearchPage = (props: { className?: string }) => {
  const { searchString } = useParams<{ searchString?: string }>();
  const [movies, setMovies] = useState<SearchItem[]>([]);
  const [isSearching, setIsSearching] = useState<Boolean>(true);
  const [hasError, setHasError] = useState<Boolean>(false);
  const [genreFilter, setGenreFilter] = useState<string>();
  const [directorFilter, setDirectorFilter] = useState<string>();
  const [yearFilter, setYearFilter] = useState<string>();
  const [descending, setDescending] = useState<Boolean>(true);
  const [filters, setFilters] = useState<Array<any>>();
  const [sortBy, setSortBy] = useState<string>("relevance");

  const updateYears = (event: any) => {
    setYearFilter(event.target.value);
  };

  const updateDirector = (event: any) => {
    setDirectorFilter(event.target.value);
  };

  const updateGenre = (event: any) => {
    setGenreFilter(event.target.value);
  };

  const getParamUpdater = (key: string) => {
    if (key === "genre") {
      return updateGenre;
    }
    if (key === "director") {
      return updateDirector;
    }
    if (key === "year") {
      return updateYears;
    }
    return () => {};
  };

  useEffect(() => {
    !isSearching && setIsSearching(true);
    api({
      path: "/movies/",
      method: "GET",
      params: {
        keywords: searchString,
        genres: genreFilter,
        directors: directorFilter,
        years: yearFilter,
        per_page: 80,
        page: 1,
        sort: sortBy,
        desc: descending,
      },
    }).then((res) => {
      setIsSearching(false);
      if (res.code !== 0) {
        setHasError(true);
      } else {
        setMovies(res.data.movies as SearchItem[]);
        setFilters(res.data.filters);
      }
    });
  }, [
    searchString,
    genreFilter,
    directorFilter,
    sortBy,
    descending,
    yearFilter,
  ]);

  if (isSearching) {
    return <div>Searching...</div>;
  }

  if (hasError) {
    return <div>An error occurred, please try again.</div>;
  }

  
  return (
    <div className={`SearchPage ${(props.className || "").trim()}`}>
      <h3>Search results for "{searchString}"</h3>
      <div className="SearchPage__filters">
        {filters &&
          filters.map((filter) => (
            <Filter
              key={filter.key}
              filterKey={filter.key}
              name={filter.name}
              type={filter.type}
              selections={filter.selections}
              updateSearchParams={getParamUpdater(filter.key)}
            />
          ))}
      </div>
      <div className="SearchPage__sort">
        <label htmlFor="sort">Sort by</label>
        <select
          name="sort"
          onChange={(event) => setSortBy(event.target.value)}
          value={sortBy}
        >
          <option value="relevance">Relevance</option>
          <option value="rating">Rating</option>
          <option value="name">Name</option>
          <option value="year">Year</option>
        </select>
        <select
          name="order"
          onChange={(event) =>
            setDescending(event.target.value === "descending")
          }
          value={descending ? "descending" : "ascending"}
        >
          <option value="descending">Descending</option>
          <option value="ascending">Ascending</option>
        </select>
      </div>
      {movies ? (
        <TileList
          className="SearchPage__list"
          itemClassName="SearchPage__item"
          items={movies.map((movie) => (
            <MovieItem
              movieId={movie.id}
              year={movie.releaseYear}
              title={movie.title}
              genres={movie.genres.map((g) => ({
                id: `${g}-${movie.id}`,
                text: g,
              }))}
              imageUrl={movie.imageUrl || movieLogo}
              cumulativeRating={movie.cumulativeRating}
              numRatings={movie.numVotes}
              numReviews={0}
            />
          ))}
        />
      ) : <div>Sorry, we couldn't find any results.</div>}
    </div>
  );
};

export default view(SearchPage);
