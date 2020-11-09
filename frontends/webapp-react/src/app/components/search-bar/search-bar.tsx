import "./search-bar.scss";
import AutoSuggest from "react-autosuggest";
import React from "react";
import { Search } from "react-feather";
import { themeable } from 'react-themeable-ts';


import axios from "axios";
import { view } from "@risingstack/react-easy-state";
import AutosuggestHighlightMatch from "autosuggest-highlight/match"
import AutosuggestHighlightParse from "autosuggest-highlight/parse"

type SearchBarProps = {
  type: string;
  height?: number;
  width?: number;
  onSearch: (text: string) => void;
  onChose: (movieId: string) => void;
};

const SearchBar = (props: SearchBarProps & { className?: string }) => {
  const [value, setValue] = React.useState("");
  const [suggestions, setSuggestions] = React.useState<[]>([]);

  const getSuggestionValue = (suggestion: any) => {
    return JSON.parse(JSON.stringify(suggestion))["title"];
  };
  const theme = {
    container:                'SearchBar__container',
    containerOpen:            'SearchBar__container--open',
    input:                    'SearchBar__input',
    inputOpen:                'SearchBar__input--open',
    inputFocused:             'SearchBar__input--focused',
    suggestionsContainer:     'SearchBar__suggestions-container',
    suggestionsContainerOpen: 'SearchBar__suggestions-container--open',
    suggestionsList:          'SearchBar__suggestions-list',
    suggestion:               'SearchBar__suggestion',
    suggestionFirst:          'SearchBar__suggestion--first',
    suggestionHighlighted:    'SearchBar__suggestion--highlighted',
    sectionContainer:         'SearchBar__section-container',
    sectionContainerFirst:    'SearchBar__section-container--first',
    sectionTitle:             'SearchBar__section-title'
    };
  
  const renderSuggestion = (suggestion: any) => {
    const title = JSON.parse(JSON.stringify(suggestion))["title"];
    const image = JSON.parse(JSON.stringify(suggestion))["image"];
    const year = JSON.parse(JSON.stringify(suggestion))[
      "release_date"
    ].substring(0, 4);
    const suggestionText = title + " (" + year + ")"
    const matches = AutosuggestHighlightMatch(suggestionText, value);
    const parts = AutosuggestHighlightParse(suggestionText, matches);
    return (
      <div className="suggestion-content">
        {image && (
          <img
            src={image}
            width={36}
            height={48}
            style={{ marginRight: "5px" }}
          ></img>
        )}
      <span className="name">
        {
          parts.map((part, index) => {
            const className = part.highlight ? 'SearchBar__highlight' : "";

            return (
              <span className={className} key={index}>{part.text}</span>
            );
          })
        }
      </span>
      </div>
    );
  };

  const fetchSuggestion = (value: string) => {
    setValue(value);
    
    const results: [] = [];
    axios
      .post("http://ec2-3-25-228-117.ap-southeast-2.compute.amazonaws.com:2900/movie/_search", {
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
        _source: ["movie_id", "title", "release_date", "image"],
        sort: ["_score"],
      })
      .then((res) => {
        const results = res.data.hits.hits.map(
          (h: { _source: any }) => h._source
        );
        setSuggestions(results);
      });
  };

  function handleClick() {
    props.onSearch(value);
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
          onSuggestionsFetchRequested={({ value }) => fetchSuggestion(value)}
          onSuggestionSelected={(_, { suggestion, suggestionValue, method }) => {
            setValue(suggestionValue);
            props.onChose(JSON.parse(JSON.stringify(suggestion))["movie_id"])
          }}
          getSuggestionValue={(suggestion) => getSuggestionValue(suggestion)}
          renderSuggestion={(suggestion) => renderSuggestion(suggestion)}
          inputProps={{
            placeholder: "Search...",
            value: value,
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
