/**
 * Pagination Component
 *
 * Example use case:
 * Suppose you have a <List>
 * Then, in the outer element that should place your <List>:
 * <List />
 * <Pagination
 *   className="TheParent__the-content-name-pagination" // Any className you preferred
 *   displayType="numbered"
 *   dataType="callback"
 *   dataCallback={(page) => {
 *     // Do something to fetch the data array of this page
 *   }}
 *   renderCallback={(data) => {
 *     // Place the data inside your list
 *     // For "loadmore", data is a merged array with all fetched pages
 *   }}
 *   total={10} // The fetcher of total needs to be handled outside
 *   current={currentPage} // you can pass a current page number here
 *   onCurrentChange={(newI, oldI) => {
 *     // If you passed a state, you need to use this to sync the state
 *   }}
 * />
 */

import { view } from "@risingstack/react-easy-state";
import range from "lodash/range";
import React from "react";
import { ChevronLeft, ChevronRight } from "react-feather";
import { usePrevious, useUpdateEffect } from "src/utils";
import "./pagination.scss";
import firstIcon from "./to-first.svg";
import lastIcon from "./to-last.svg";

type PaginationProps = {
  displayType: "numbered" | "dotted" | "loadmore";
  dataType: "slice" | "callback";
  perPage?: number; // only for "slice"
  dataCallback?: (page?: number) => object[] | Promise<object[]>; // page will be omitted for "slice"
  renderCallback: (data: object[]) => void; // only the data in the page
  total: number; // 0 for "loadmore"
  current?: number; // undefined means 1
  onCurrentChange?: (newCurrent: number, oldCurrent: number) => void; // to change parent state
};

const Pagination = (props: PaginationProps & { className?: string }) => {
  const [current, setCurrent] = React.useState(props.current || 1);
  const [data, setData] = React.useState<object[]>([]);
  const prevPageNum = usePrevious(current);
  const pageInput = React.useRef<HTMLInputElement>(null);

  const handleCallbackData = (newData: object[]) => {
    if (props.displayType !== "loadmore") {
      setData(newData);
      props.renderCallback(newData);
    } else {
      // For "loadmore", newData needs to be merged with current data
      const mergedData = [...data, ...newData];
      setData(mergedData);
      props.renderCallback(mergedData);
    }
    if (pageInput.current !== null) {
      pageInput.current.value = current.toString();
    }
  };

  const handleSliceData = () => {
    if (props.displayType !== "loadmore") {
      props.renderCallback(
        data.slice(
          (current - 1) * (props.perPage || 1),
          current * (props.perPage || 1)
        )
      );
    } else {
      props.renderCallback(data.slice(0, current * (props.perPage || 1)));
    }
    if (pageInput.current !== null) {
      pageInput.current.value = current.toString();
    }
  };

  React.useEffect(() => {
    if (props.dataType === "slice" && props.dataCallback) {
      Promise.resolve(props.dataCallback()).then((data) => {
        setData(data);
        props.renderCallback(data.slice(0, props.perPage || 1));
      });
    } else if (props.dataType === "callback" && props.dataCallback) {
      Promise.resolve(props.dataCallback(current)).then(handleCallbackData);
    }
  }, []);

  useUpdateEffect(() => {
    if (props.dataType === "callback" && props.dataCallback) {
      Promise.resolve(props.dataCallback(current)).then(handleCallbackData);
    } else if (props.dataType === "slice" && props.dataCallback) {
      handleSliceData();
    }
    if (props.onCurrentChange) {
      props.onCurrentChange(current, prevPageNum || current);
    }
  }, [current]);

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === "Enter") {
      if (pageInput.current !== null) {
        setCurrent(parseInt(pageInput.current.value, 10));
      }
    }
  };

  const handlePaginatingFactory = (newPage: number) => {
    return (event: React.MouseEvent) => {
      event.stopPropagation();
      event.nativeEvent.stopImmediatePropagation();
      if (current !== newPage) {
        setCurrent(newPage);
      }
    };
  };

  if (props.displayType === "numbered") {
    return (
      <div className={`Pagination ${(props.className || "").trim()}`}>
        {current !== 1 ? (
          <button
            className="Pagination__button Pagination__first"
            onClick={handlePaginatingFactory(1)}
          >
            <img
              src={firstIcon}
              alt="first"
              className="Pagination__first-image Pagination__image"
            />
          </button>
        ) : (
          <button className="Pagination__button Pagination__first Pagination__button--disabled">
            <img
              src={firstIcon}
              alt="first"
              className="Pagination__first-image Pagination__image"
            />
          </button>
        )}
        {current - 1 > 1 ? (
          <button
            className="Pagination__button Pagination__prev"
            onClick={handlePaginatingFactory(Math.max(1, current - 1))}
          >
            <ChevronLeft className="Pagination__image" />
          </button>
        ) : (
          <button className="Pagination__button Pagination__prev Pagination__button--disabled">
            <ChevronLeft className="Pagination__image" />
          </button>
        )}
        {props.total > 1 ? (
          <input
            type="text"
            className="Pagination__input"
            onKeyPress={handleKeyPress}
            ref={pageInput}
          />
        ) : (
          <div className="Pagination__only-one">1</div>
        )}
        <div className="Pagination__total">
          {" "}
          of {props.total} {props.total > 1 ? "pages" : "page"}
        </div>
        {current + 1 < props.total ? (
          <button
            className="Pagination__button Pagination__next"
            onClick={handlePaginatingFactory(
              Math.min(props.total, current + 1)
            )}
          >
            <ChevronRight className="Pagination__image" />
          </button>
        ) : (
          <button className="Pagination__button Pagination__next Pagination__button--disabled">
            <ChevronRight className="Pagination__image" />
          </button>
        )}
        {current < props.total ? (
          <button
            className="Pagination__button Pagination__last"
            onClick={handlePaginatingFactory(props.total)}
          >
            <img
              src={lastIcon}
              alt="last"
              className="Pagination__last-image Pagination__image"
            />
          </button>
        ) : (
          <button className="Pagination__button Pagination__last Pagination__button--disabled">
            <img
              src={lastIcon}
              alt="first"
              className="Pagination__last-image Pagination__image"
            />
          </button>
        )}
      </div>
    );
  } else if (props.displayType === "dotted") {
    return (
      <div className={`Pagination ${(props.className || "").trim()}`}>
        {range(1, props.total + 1).map((i) => {
          return (
            <button
              className={
                "Pagination__dot" +
                (current === i ? " Pagination__dot--current" : "")
              }
              onClick={handlePaginatingFactory(i)}
            ></button>
          );
        })}
      </div>
    );
  } else if (props.displayType === "loadmore") {
    return (
      <div className={`Pagination ${(props.className || "").trim()}`}>
        <button
          className="Pagination__load-more"
          onClick={handlePaginatingFactory(current + 1)}
        >
          Load more...
        </button>
      </div>
    );
  } else {
    throw Error("Undefined displayType");
  }
};

export default view(Pagination);
