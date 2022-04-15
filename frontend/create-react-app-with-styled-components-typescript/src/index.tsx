import * as React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Core from './Core';
import Sites from './Sites';
import Dashboard from './Dashboard';

ReactDOM.render(
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<Core />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/home" element={<Dashboard />} />
        <Route path="/sites" element={<Sites />} />
      </Route>
    </Routes>
  </BrowserRouter>,
  document.getElementById('root')
);
