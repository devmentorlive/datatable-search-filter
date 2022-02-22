import React from 'react';

export default function Datatable({ data }) {
  // Guard clause to ensure there is a 1st row
  // Object.keys(data[0]) pulls out all of the keys from the json for our headers
  const columns = data[0] && Object.keys(data[0]);
  // return an html table
  return (
    // cellPadding & cellSpacing for table can't be controlled via .css
    <table cellPadding={0} cellSpacing={0}>
      {/* Generate table headers dynamically via our json attributes */}
      <thead>
        <tr>
          {/* Guard clause (data[0]) to ensure there is >= 1 row
              Pull keys out of first row to use as headings*/}
          {data[0] && columns.map((heading) => <th>{heading}</th>)}
        </tr>
      </thead>
      <tbody>
        {/* Iterate over each row of data */}
        {data.map((row) => (
          <tr>
             {/* Iterate over each column of data */}
            {columns.map((column) => (
              // get at individual cells
              <td>{row[column]}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
