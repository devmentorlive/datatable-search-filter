import React, {useState, useEffect} from "react";
import Datatable from "../datatable";

require("es6-promise").polyfill()
require("isomorphic-fetch")

export default function App() {
  const [data, setData] = useState([]);
  const [q, setQ] = useState("");
  // searchColumns enforces which table columns are queryable
  const [searchColumns, setSearchColumns] = useState(["course_name", "course_overview",])

  useEffect(() => {
    fetch("http://localhost:8000/courses/")
    .then((response) => response.json())
    .then((json) => setData(json));
  }, []);


// This function returns rows in the datatable that correspond with a search query
function search(rows) { 
  return rows.filter((row) =>

    // row.course_name.toLowerCase().indexOf(q.toLowerCase()) > -1 ||
    // row.course_overview.toLowerCase().indexOf(q.toLowerCase()) > -1

    // 'some' will return a row if any cell within a row matches with the search query
    searchColumns.some((column) =>
    // handle null && undefined cells
    hasData(row[column]) &&
    row[column].toString().toLowerCase().indexOf(q.toLowerCase()) > -1
    )
  );
}

function hasData(cell) {
  return (cell !== null && cell !== undefined)
}

const columns = data[0] && Object.keys(data[0]);
  return ( 
    <div>
      <div>
        {/* TODO: Use q.toLowerCase() here? */}
        <input type="text" value={q} onChange={(e) => setQ(e.target.value)} />
           {/* Iterate over columns */}
          {columns && columns.map((column) => (
          <label>
            {/* set columns included in searchColumns to checked */}
            <input type='checkbox' checked={searchColumns.includes(column)}
            onChange={(e) => {

             const checked = searchColumns.includes(column);
             // prev is previous state (checked or unchecked) of this column
             setSearchColumns((prev) => checked
             // remove the unchecked column from searchColumns
             ? prev.filter((sc) => sc !== column)
             // add the newly checked column to searchColumns
             // (return a new array with previous array elements and append the newly checked column)
             : [...prev, column]
             );
            }}
          />
            {column}
            </label>
          ))}
      </div>
      <div>
        {/* data prop of Datatable is wrapped by search function
            i.e. Datatable will only render data that matches our search query */}
        <Datatable data={search(data)} /> 
      </div>
    </div>
  );
}