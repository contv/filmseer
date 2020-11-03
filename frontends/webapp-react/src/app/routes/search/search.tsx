import { view } from "@risingstack/react-easy-state";
import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import Filter from "src/app/components/filter";
import MovieItem from "src/app/components/movie-item/movie-item";
import TileList from "src/app/components/tile-list";
import { api } from "src/utils";
import "./search.scss";

type SearchItem = {
  id: string;
  title: string;
  releaseYear: number;
  genres: { id: string; text: string }[];
  imageUrl?: string;
  cumulativeRating: number;
  numRatings: number;
  numReviews: number;
};

const groupItems = (group: any, size: any, length: any) =>
  group
    .reduce(
      (prev: any, current: any, index: any, original: any) =>
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
  const [yearRange, setYearRange] = useState<string>();
  const [filters, setFilters] = useState<Array<any>>();

  const updateYears = (event: any) => {
    setYearRange(event.target.value);
  };

  const updateDirector = (event: any) => {
    console.log(event.target.value)
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
      }&per_page=80&page=1&sort=relevance&desc=true`,
      method: "GET",
    }).then((res) => {
      if (res.code !== 0) {
        setHasError(true);
      } else {
        const grouped = groupItems(res.data.movies, 8, 10);
        setGroupedResults(grouped);
        setFilters(res.data.filters);
        console.log(res.data.filters);
      }
    });
  }, [searchString, genreFilter, directorFilter]);

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
                      id: g.id,
                      text: g.text,
                    }))}
                    imageUrl={movie.imageUrl}
                    cumulativeRating={9.2}
                    numRatings={2}
                    numReviews={2}
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
