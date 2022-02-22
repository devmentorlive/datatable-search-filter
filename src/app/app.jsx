import React, { useState, useEffect } from 'react';

import Datatable from '../datatable';
import './styles.css';

// allows any browser to support promises via polyfill
require('es6-promise').polyfill();
// allows any browser to support fetch()
require('isomorphic-fetch');

/* React 'hooks' eliminate the need for es6 classes
 lifetime cycle functions (componentWIllMount(), componentDidMount(), etc.) are no longer needed
*/

export default function App() {
    //  [getter, setter]
    // for our data from the remote api
    const [data, setData] = useState([]);
    // for our search queries
    const [q, setQ] = useState('');
    // for specifying which columns to search in datatable
    const [searchColumns, setSearchColumns] = useState(
      []); // specify columns to search inside [] 

  useEffect(() => {
    // fetch the data from the remote api
    // fetch('https://swapi.dev/api/people')
    fetch('http://8000:localhost/events/')
    // handle the promise when response comes from server
    // turn the http response into json data
    .then((response) => response.json())
    // give app component access to json data
    .then((json) => setData(json.results));
  }, []);   // empty array ensures useEffect() will only fire once

  // function to filter datatable by user input
  function search(rows) {
    // 'filter' has to return all of the expressions to return a single value
    return rows.filter((row) =>
      // 'some' returns values that match any of the expressions in our specified search columns
      searchColumns.some(
        (column) =>
          row[column]
            // convert data cell to string
            .toString()
            // make data cell case-insensitive
            .toLowerCase()
            // indexOf will attempt to match user-inputted string to cell string
            // indexOf will return the first character index that matches
            .indexOf(q.toLowerCase()) > -1, // == -1 if there is no match 
      ),
    );
  }

  const columns = data[0] && Object.keys(data[0]);
  // return of function component in ReactJS is the render method
  return (
    <div>
      <div>
          {/* Input tag for query filter */}
        <input
          type='text'
          value={q}
          // e represents the event every time a character is typed into the query box
          onChange={(e) => setQ(e.target.value)}
        />
        {/* iterate over columns */}
        {columns &&
          columns.map((column) => (
            <label>
              <input
                type='checkbox'
                // Checked checkboxes will be queried in search
                // (Set columns specified in searchColumns [] to checked by default)
                checked={searchColumns.includes(column)}
                onChange={(e) => {
                  const checked = searchColumns.includes(column);
                  // if column was previously checked
                  setSearchColumns((prev) => checked
                    // then remove it from searchColumns
                    ? prev.filter((sc) => sc !== column)
                    // else add it to searchColumns
                    : [...prev, column],
                  );
                }}
              />
              {column}
            </label>
          ))}
      </div>
      <div>
        {/* wrap data prop with search function
            (Data in our state will be filtered through our search function before being passed to Datatable) */}
        <Datatable data={search(data)} />
      </div>
    </div>
  );
}
