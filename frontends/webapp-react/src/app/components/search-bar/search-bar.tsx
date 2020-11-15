import FormControl from "@material-ui/core/FormControl";
import MenuItem from "@material-ui/core/MenuItem";
import Select from "@material-ui/core/Select";
import { view } from "@risingstack/react-easy-state";
import AutosuggestHighlightMatch from "autosuggest-highlight/match";
import AutosuggestHighlightParse from "autosuggest-highlight/parse";
import { debounce } from "lodash";
import React from "react";
import AutoSuggest from "react-autosuggest";
import { Search } from "react-feather";
import { useParams } from "react-router-dom";
import { api } from "src/utils";
import "./search-bar.scss";

type SearchBarProps = {
  type: string;
  height?: number;
  width?: number;
  onSearch: (text: string) => void;
  onSelectSuggestion: (movieId: string) => void;
  onField: (text: string) => void;
  debounceTime?: number;
  sizeSuggestion?: number;
};

type SuggestionItem = {
  id: string;
  releaseDate: string;
  imageUrl: string;
  title: string;
};

const SearchBar = (props: SearchBarProps & { className?: string }) => {
  const { searchString } = useParams<{ searchString?: string }>();
  const { searchField } = useParams<{ searchField?: string }>();
  const [value, setValue] = React.useState(searchString || "");
  const [suggestions, setSuggestions] = React.useState<SuggestionItem[]>([]);
  const [field, setField] = React.useState<string>(searchField || "all");
  const getSuggestionValue = (suggestion: SuggestionItem) => {
    return suggestion.title;
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

  const renderSuggestion = (suggestion: SuggestionItem) => {
    const title = suggestion.title;
    const image = suggestion.imageUrl;
    const year = suggestion.releaseDate.substring(0, 4);
    const suggestionText = title + " (" + year + ")";
    const matches = AutosuggestHighlightMatch(suggestionText, value);
    const parts = AutosuggestHighlightParse(suggestionText, matches);
    return (
      <div className="suggestion-content">
        {image && (
          <img
            src={image}
            className="SearchBar__sugesstion-poster"
            alt="poster"
          ></img>
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

  const fetchSuggestions = (value: string, field: string) => {
    api({
      path: `/movies/search-hint`,
      method: "GET",
      params: {
        keyword: value,
        limit: props.sizeSuggestion || 8,
        field: field || "all",
      },
    }).then((res) => {
      if (res.code !== 0) {
        setSuggestions([]);
      } else {
        setSuggestions(res.data.items);
      }
    });
  };

  const debouncedFetchSuggestions = React.useCallback(
    debounce(fetchSuggestions, props.debounceTime || 150),
    []
  );
  const handleClick = () => {
    props.onSearch(value);
    props.onField(field);
  };

  const handleEnter = (event: React.KeyboardEvent<any>) => {
    if (event.key === "Enter") {
      handleClick();
    }
  };

  return (
    <div
      className={`SearchBar ${(props.className || "").trim()}`}
      style={{
        width: props.width,
        height: props.height,
        gridTemplateColumns:
          "130px 1fr " + (props.height ? props.height + "px" : "2em"),
        gridTemplateRows: props.height + "px",
      }}
    >
      <div className="SearchBar__field">
        <FormControl variant="outlined">
          <Select
            name="searchBy"
            onChange={(event) => setField(event.target.value as string)}
            value={field}
            style={{ height: "100%" }}
          >
            <MenuItem value="all">All</MenuItem>
            <MenuItem value="title">Title</MenuItem>
            <MenuItem value="description">Description</MenuItem>
            <MenuItem value="people">People</MenuItem>
            <MenuItem value="genres">Genres</MenuItem>
          </Select>
        </FormControl>
      </div>
      <div className="SearchBar__outer">
        <AutoSuggest
          suggestions={suggestions}
          theme={theme}
          onSuggestionsClearRequested={() => setSuggestions([])}
          onSuggestionsFetchRequested={({ value }) =>
            debouncedFetchSuggestions(value, field)
          }
          onSuggestionSelected={(_, { suggestion, suggestionValue }) => {
            setValue(suggestionValue);
            props.onSelectSuggestion(suggestion.id);
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
