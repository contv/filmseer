import { view } from "@risingstack/react-easy-state";
import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import Filter from "src/app/components/filter";
import MovieItem from "src/app/components/movie-item/movie-item";
import TileList from "src/app/components/tile-list";
import movieLogo from "src/app/components/movie-item/movie-logo.png"
import { api } from "src/utils";
import "./search.scss";

type SearchItem = {
  id: string;
  title: string;
  releaseYear: number;
  genres: string[];
  imageUrl?: string;
  averageRating: number;
  numRatings: number;
  numReviews: number;
};

const groupItems = (group: any, size: any, length: any) =>
  group
    .reduce(
      (prev: any, _: any, index: any, original: any) =>
        index % size === 0
          ? prev.concat([original.slice(index, index + size)])
          : prev,
      []
    )
    .filter((_: any, index: any) => index < length);

const SearchPage = (props: { className?: string }) => {
  const { searchString } = useParams<{ searchString?: string }>();
  const [groupedResults, setGroupedResults] = useState<
    Array<Array<SearchItem>>
  >();
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
    console.log(event.target.value);
    setDirectorFilter(event.target.value);
  };

  const updateGenre = (event: any) => {
    setGenreFilter(event.target.value);
  };

  const getParamUpdater = (name: string) => {
    if (name === "Genre") {
      return updateGenre;
    }
    if (name === "Directors") {
      return updateDirector;
    } else {
      return updateYears;
    }
  };

  useEffect(() => {
    api({
      path: `/movie/?keywords=${searchString}${
        genreFilter ? `&genres=${encodeURI(genreFilter)}` : ""
      }${
        directorFilter ? `&directors=${encodeURI(directorFilter)}` : ""
      }${
        yearFilter ? `&years=${yearFilter}` : ""
      }&per_page=80&page=1&sort=${sortBy}&desc=${descending}`,
      method: "GET",
    }).then((res) => {
      if (res.code !== 0) {
        setHasError(true);
      } else {
        console.log(res.data)
        const grouped = groupItems(res.data.movies, 8, 10);
        setGroupedResults(grouped);
        setFilters(res.data.filters);
      }
    });
  }, [searchString, genreFilter, directorFilter, sortBy, descending, yearFilter]);

  if (groupedResults && filters) {
    return (
      <div className={`SearchPage ${(props.className || "").trim()}`}>
        <h3>Search results for "{searchString}"</h3>
        <div className="Search__filters">
          {filters &&
            filters.map((filter) => (
              <Filter
                key={filter.key}
                filterKey={filter.key}
                name={filter.name}
                type={filter.type}
                selections={filter.selections}
                updateSearchParams={getParamUpdater(filter.name)}
              />
            ))}
        </div>
        <div className="Search__sort">
          <label htmlFor="sort">Sort by</label>
          <select
            name="sort"
            onChange={(event) => setSortBy(event.target.value)}
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
          >
            <option value="descending">Descending</option>
            <option value="ascending">Ascending</option>
          </select>
        </div>
        {groupedResults &&
          groupedResults.map((group) => (
            <TileList
              items={group.map((movie) => (
                <div className="Search__item">
                  <MovieItem
                    movieId={movie.id}
                    year={movie.releaseYear}
                    title={movie.title}
                    genres={movie.genres.map((g) => ({
                      id: `${g}-${movie.id}`,
                      text: g,
                    }))}
                    imageUrl={movie.imageUrl || movieLogo}
                    cumulativeRating={78}
                    numRatings={20}
                    numReviews={3}
                  />
                </div>
              ))}
            />
          ))}
      </div>
    );
  }
  return <div>No results for this page.</div>;
};

export default view(SearchPage);
