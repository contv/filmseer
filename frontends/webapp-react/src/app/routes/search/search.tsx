import { view } from "@risingstack/react-easy-state";
import React from "react";
import { useParams } from "react-router-dom";
import Filter from "src/app/components/filter";
import MovieItem from "src/app/components/movie-item/movie-item";
import movieLogo from "src/app/components/movie-item/movie-logo.png";
import Pagination from "src/app/components/pagination";
import TileList from "src/app/components/tile-list";
import { api, useUpdateEffect } from "src/utils";
import "./search.scss";

export type SearchItem = {
  id: string;
  title: string;
  releaseYear: number;
  genres: string[];
  imageUrl?: string;
  averageRating: number;
  numVotes: number;
  cumulativeRating: number;
};

type Handle<T> = T extends React.ForwardRefExoticComponent<
  React.RefAttributes<infer T2>
>
  ? T2
  : {
      refresh: () => void;
    } | null;

const SearchPage = (props: { className?: string }) => {
  const { searchString } = useParams<{ searchString?: string }>();
  const [movies, setMovies] = React.useState<SearchItem[]>([]);
  const [isSearching, setIsSearching] = React.useState<Boolean>(true);
  const [hasError, setHasError] = React.useState<Boolean>(false);
  const [genreFilter, setGenreFilter] = React.useState<string>();
  const [directorFilter, setDirectorFilter] = React.useState<string>();
  const [yearFilter, setYearFilter] = React.useState<string>();
  const [descending, setDescending] = React.useState<Boolean>(true);
  const [filters, setFilters] = React.useState<Array<any>>();
  const [sortBy, setSortBy] = React.useState<string>("relevance");
  const [totalPages, setTotalPages] = React.useState<number>(0);
  let paginationHandle: Handle<typeof Pagination>;

  // This is an UGLY approach, but a CSS reader is even worse
  // UPDATE THIS WHEN YOU MODIFY SCSS
  // const perPage = (
  //   CONTAINER_MAX_WIDTH + GRID_GAP
  // ) / (ITEM_MAX_WIDTH + GRID_GAP) * NUMBER_OF_ROWS
  const perPage =
    Math.floor((document.body.clientWidth * 0.8 + 24) / (150 + 24)) * 4;

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

  useUpdateEffect(() => {
    paginationHandle && paginationHandle.refresh();
  }, [
    searchString,
    genreFilter,
    directorFilter,
    sortBy,
    descending,
    yearFilter,
  ]);

  return (
    <div className={`SearchPage ${(props.className || "").trim()}`}>
      <h3>Search results for "{searchString}"</h3>
      {filters && (
        <div className="SearchPage__filters">
          {filters.map((filter) => (
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
      )}
      {filters && (
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
      )}
      {isSearching || hasError ? (
        isSearching ? (
          <div>Searching...</div>
        ) : (
          <div>An error occurred, please try again.</div>
        )
      ) : movies ? (
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
      ) : (
        <div>Sorry, we couldn't find any results.</div>
      )}
      <div className="SearchPage__pagination-wrapper">
        <Pagination
          className={
            `SearchPage__pagination` +
            (isSearching || hasError ? "SearchPage__pagination--hidden" : "")
          }
          ref={(c) => {
            paginationHandle = c;
          }}
          displayType="numbered"
          dataType="callback"
          dataCallback={async (page) => {
            setIsSearching(true);
            let res;
            try {
              res = await api({
                path: "/movies/",
                method: "GET",
                params: {
                  keywords: searchString,
                  genres: genreFilter,
                  directors: directorFilter,
                  years: yearFilter,
                  per_page: perPage,
                  page: page,
                  sort: sortBy,
                  desc: descending,
                },
              });
            } catch (e) {
              setIsSearching(false);
              setHasError(true);
              return [];
            }
            setIsSearching(false);
            if (res.code !== 0) {
              setHasError(true);
              return [];
            } else {
              setHasError(false);
              setFilters(res.data.filters);
              setTotalPages(res.data.total);
              return res.data.movies;
            }
          }}
          renderCallback={(data) => {
            setMovies(data as SearchItem[]);
          }}
          total={totalPages}
        />
      </div>
    </div>
  );
};

export default view(SearchPage);
