import "./search.scss";

import { api, useUpdateEffect } from "src/utils";

import Filter from "src/app/components/filter";
import FormControl from "@material-ui/core/FormControl";
import InputLabel from "@material-ui/core/InputLabel";
import MenuItem from "@material-ui/core/MenuItem";
import MovieItem from "src/app/components/movie-item/movie-item";
import Pagination from "src/app/components/pagination";
import React from "react";
import Select from "@material-ui/core/Select";
import TileList from "src/app/components/tile-list";
import movieLogo from "src/app/components/movie-item/movie-logo.png";
import { useParams } from "react-router-dom";
import { view } from "@risingstack/react-easy-state";

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
      refresh: (page?: number) => void;
    } | null;

const SearchPage = (props: { className?: string }) => {
  const { searchString } = useParams<{ searchString?: string }>();
  const { searchField } = useParams<{ searchField?: string }>();
  const [movies, setMovies] = React.useState<SearchItem[]>([]);
  const [isSearching, setIsSearching] = React.useState<Boolean>(true);
  const [hasError, setHasError] = React.useState<Boolean>(false);
  const [genreFilter, setGenreFilter] = React.useState<string>();
  const [directorFilter, setDirectorFilter] = React.useState<string>();
  const [yearFilter, setYearFilter] = React.useState<Array<string>>();
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
    console.log(event)
    setYearFilter((event || { name: "" }).name || "");
  };

  const updateDirector = (event: any) => {
    setDirectorFilter((event || { name: "" }).name || "");
  };

  const updateGenre = (event: any) => {
    setGenreFilter((event || { name: "" }).name || "");
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
  }, [sortBy, descending]);

  useUpdateEffect(() => {
    paginationHandle && paginationHandle.refresh(1);
  }, [searchString, searchField, genreFilter, directorFilter, yearFilter]);

  return (
    <div className={`SearchPage ${(props.className || "").trim()}`}>
      
      <div className="SearchPage__top">
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
            <FormControl style={{ marginRight: "20px" }}>
              <InputLabel>Sort by</InputLabel>
              <Select
                value={sortBy}
                onChange={(event) => setSortBy(event.target.value as string)}
              >
                <MenuItem value="relevance">Relevance</MenuItem>
                <MenuItem value="rating">Rating</MenuItem>
                <MenuItem value="name">Name</MenuItem>
                <MenuItem value="year">Year</MenuItem>
              </Select>
            </FormControl>

            <FormControl>
              <InputLabel>Order</InputLabel>
              <Select
                value={descending ? "descending" : "ascending"}
                onChange={(event) =>
                  setDescending((event.target.value as string) === "descending")
                }
              >
                <MenuItem value="descending">Descending</MenuItem>
                <MenuItem value="ascending">Ascending</MenuItem>
              </Select>
            </FormControl>
          </div>
        )}
      </div>

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
            const searchParams = new URLSearchParams("");
            searchParams.append("keywords", searchString || "");
            searchParams.append("field", searchField || "");
            searchParams.append("genres", genreFilter || "");
            searchParams.append("per_page", perPage.toString() || "32");
            searchParams.append("page", page?.toString() || "1");
            searchParams.append("sort", sortBy || "" );
            searchParams.append("desc", descending.toString() || "True");
            
            
            try {
              res = await api({
                path: "/movies/",
                method: "GET",
                params: {
                  keywords: searchString,
                  field: searchField,
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
              setTotalPages(1);
              return [];
            }
            setIsSearching(false);
            if (res.code !== 0) {
              setHasError(true);
              setTotalPages(1);
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
