/**
 * Example:
 *    <TableList
 *      header={{ foo: <i>foo</i>, bar: <u>bar</u>, baz: <b>baz</b> }}
 *      showHeader={true}
 *      rowsData={[
 *        { foo: 2, bar: 3, baz: 4, bac: 5 },
 *        { foo: 22, bar: 23, baz: 24, bac: 25 },
 *      ]}
 *      cellRenderer={(cellData) => <span>{cellData}</span>}
 *    />
 */
import { view } from "@risingstack/react-easy-state";
import range from "lodash/range";
import React from "react";
import "./table-list.scss";

type TableListProps<T extends object> = {
  header: {
    [key in keyof T]: React.ReactNode;
  };
  headerClassName?: {
    [key in keyof T]: string;
  };
  columnSizes?: {
    [key in keyof T]: string;
  };
  showHeader: boolean;
  rowsData: Array<{ [key in keyof T]: any } & { [key: string]: any }>;
  cellRenderer: (
    cellData: any,
    index: number,
    rowData: { [key in keyof T]: any } & { [key: string]: any }
  ) => React.ReactNode;
};

const TableList = <T extends object>(
  props: TableListProps<T> & { className?: string }
) => {
  const gridTemplates = {
    gridTemplateAreas:
      "'" +
      (props.showHeader
        ? Object.keys(props.header)
            .map((k) => `${k}-header`)
            .join(" ") + "'\n'"
        : "") +
      range(props.rowsData.length)
        .map((i) =>
          Object.keys(props.header)
            .map((k) => `${k}-${i}`)
            .join(" ")
        )
        .join("'\n'") +
      "'",
    gridTemplateColumns: props.columnSizes
      ? Object.keys(props.header)
          .map((key) =>
            props.columnSizes
              ? props.columnSizes[key as keyof T] || "1fr"
              : "1fr"
          )
          .join(" ")
      : "1fr ".repeat(Object.keys(props.header).length).trim(),
    gridTemplateRows: "auto",
  };
  console.log("grid", gridTemplates);
  return (
    <div
      className={`TableList ${(props.className || "").trim()}`}
      style={gridTemplates}
    >
      {props.showHeader
        ? (Object.entries(props.header) as [keyof T, React.ReactNode][]).map(
            ([cellName, cell]) => (
              <div
                className={`TableList__header TableList__header-${cellName} ${
                  props.headerClassName
                    ? props.headerClassName[cellName] || ""
                    : ""
                }`}
                style={{ gridArea: `${cellName}-header` }}
                key={`${cellName}-header`}
              >
                {cell}
              </div>
            )
          )
        : null}
      {props.rowsData.map((rowData, index) =>
        (Object.entries(rowData) as [keyof T, any][]).map(
          ([cellName, cellData]) =>
            Object.keys(props.header).includes(cellName as string) ? (
              <div
                className={`TableList__cell TableList__cell-${cellName}`}
                style={{ gridArea: `${cellName as string}-${index}` }}
                key={`${cellName as string}-${index}`}
              >
                {props.cellRenderer(cellData, index, rowData)}
              </div>
            ) : null
        )
      )}
    </div>
  );
};

export default view(TableList);
