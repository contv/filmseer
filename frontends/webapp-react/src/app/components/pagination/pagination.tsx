/**
 * Pagination Component
 *
 * Example use case:
 * Suppose you have a <List>
 * Then, in the outer element that should place your <List>:
 * <List />
 * <Pagination
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
import React from "react";
import "./pagination.scss";

type PaginationProps = {
  displayType: "numbered" | "dotted" | "loadmore";
  dataType: "slice" | "callback";
  dataCallback?: (page: number) => object[];
  renderCallback: (data: object[]) => void; // only the data in the page
  total: number; // 0 for "loadmore"
  current?: number; // undefined means 1
  onCurrentChange?: (newCurrent: number, oldCurrent: number) => void; // to change parent state
};

const Pagination = (props: PaginationProps & { className?: string }) => {
  return <div className={`Pagination ${(props.className || "").trim()}`}></div>;
};

export default view(Pagination);
