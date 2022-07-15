import * as React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Core from './Core';
import Sites from './Sites';
import Executions from "./Executions";

ReactDOM.render(
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<Core />}>
        <Route path="/" element={<Sites />} />
        <Route path="/sites" element={<Sites />} />
        <Route path="/executions" element={<Executions />} />
      </Route>
    </Routes>
  </BrowserRouter>,
  document.getElementById('root')
);
