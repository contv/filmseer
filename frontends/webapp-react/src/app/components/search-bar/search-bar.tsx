import "./search-bar.scss";

import AutoSuggest from "react-autosuggest";
import AutosuggestHighlightMatch from "autosuggest-highlight/match";
import AutosuggestHighlightParse from "autosuggest-highlight/parse";
import React from "react";
import { Search } from "react-feather";
import axios from "axios";
import { debounce } from "lodash";
import https from "https";
import { view } from "@risingstack/react-easy-state";

type SearchBarProps = {
  type: string;
  height?: number;
  width?: number;
  onSearch: (text: string) => void;
  onSelectSuggestion: (movieId: string) => void;
  debounceTime?: number;
  sizeSuggestion?: number;
};

const SearchBar = (props: SearchBarProps & { className?: string }) => {
  const [value, setValue] = React.useState("");
  const [suggestions, setSuggestions] = React.useState<[]>([]);

  const getSuggestionValue = (suggestion: any) => {
    return JSON.parse(JSON.stringify(suggestion))["title"];
  };

  const theme = {
    container: "SearchBar__container",
    containerOpen: "SearchBar__container--open",
    input: "SearchBar__input",
    inputOpen: "SearchBar__input--open",
    inputFocused: "SearchBar__input--focused",
    suggestionsContainer: "SearchBar__suggestions-container",
    suggestionsContainerOpen: "SearchBar__suggestions-container--open",
    suggestionsList: "SearchBar__suggestions-list",
    suggestion: "SearchBar__suggestion",
    suggestionFirst: "SearchBar__suggestion--first",
    suggestionHighlighted: "SearchBar__suggestion--highlighted",
    sectionContainer: "SearchBar__section-container",
    sectionContainerFirst: "SearchBar__section-container--first",
    sectionTitle: "SearchBar__section-title",
  };

  const renderSuggestion = (suggestion: any) => {
    const title = JSON.parse(JSON.stringify(suggestion))["title"];
    const image = JSON.parse(JSON.stringify(suggestion))["image"];
    const year = JSON.parse(JSON.stringify(suggestion))[
      "release_date"
    ].substring(0, 4);
    const suggestionText = title + " (" + year + ")";
    const matches = AutosuggestHighlightMatch(suggestionText, value);
    const parts = AutosuggestHighlightParse(suggestionText, matches);
    return (
      <div className="suggestion-content">
        {image && (
          <img src={image} className="SearchBar__sugesstion-poster" alt="poster"></img>
        )}
        <span className="name">
          {parts.map((part, index) => {
            const className = part.highlight ? "SearchBar__highlight" : "";

            return (
              <span className={className} key={index}>
                {part.text}
              </span>
            );
          })}
        </span>
      </div>
    );
  };

  const debouncedFetchSuggestions = React.useCallback(
    debounce(fetchSuggestions, props.debounceTime || 150),
    []
  );

  function fetchSuggestions(value: string) {
    const esUrl = ((process.env || {}).REACT_APP_ELASTICSEARCH_URL) || "https://localhost:2900";
    const useSSL = (((process.env || {}).REACT_APP_ELASTICSEARCH_USESSL) || false) as boolean;
    if (esUrl) {
      const agent = new https.Agent({  
        rejectUnauthorized: useSSL
      });
      
      axios
        .post(esUrl + "/movie/_search", {
          query: {
            multi_match: {
              query: value,
              fields: [
                "title^10",
                "description",
                "genres.name",
                "positions.people",
                "positions.char_name",
              ],
            },
          },
          size: props.sizeSuggestion || 8,
          _source: ["movie_id", "title", "release_date", "image"],
          sort: ["_score"],
        }, { httpsAgent: agent })
        .then((res) => {
          const results = res.data.hits.hits.map(
            (h: { _source: any }) => h._source
          );
          setSuggestions(results);
        });
    } else {
      setSuggestions([]);
    }
  }

  function handleClick() {
    props.onSearch(value);
  }

  function handleEnter(event: React.KeyboardEvent<any>) {
    if (event.key === "Enter") {
      handleClick();
    }
  }

  return (
    <div
      className={`SearchBar ${(props.className || "").trim()}`}
      style={{
        width: props.width,
        height: props.height,
        gridTemplateColumns:
          "1fr " + (props.height ? props.height + "px" : "2em"),
      }}
    >
      <div className="SearchBar__outer">
        <AutoSuggest
          suggestions={suggestions}
          theme={theme}
          onSuggestionsClearRequested={() => setSuggestions([])}
          onSuggestionsFetchRequested={({ value }) =>
            debouncedFetchSuggestions(value)
          }
          onSuggestionSelected={(_, { suggestion, suggestionValue }) => {
            setValue(suggestionValue);
            props.onSelectSuggestion(JSON.parse(JSON.stringify(suggestion))["movie_id"]);
          }}
          getSuggestionValue={(suggestion) => getSuggestionValue(suggestion)}
          renderSuggestion={(suggestion) => renderSuggestion(suggestion)}
          inputProps={{
            placeholder: "Search...",
            value: value,
            onKeyDown: (event) => {
              handleEnter(event);
            },
            onChange: (_, { newValue }) => {
              setValue(newValue);
            },
          }}
        />
      </div>

      <button
        className="SearchBar__button"
        onClick={handleClick}
        style={{
          width: props.height || "2em",
          height: props.height || "2em",
          ["--aspect-ratio" as any]: "1/1",
        }}
      >
        <Search
          size={Math.round(((props.height || 0) / 60) * 14) * 2 || "1em"}
        />
      </button>
    </div>
  );
};

export default view(SearchBar);
