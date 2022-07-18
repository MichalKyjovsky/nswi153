import { createRoot } from 'react-dom/client';
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Core from './Core';
import Sites from './Sites';
import Executions from "./Executions";
import Visualisation from "./Visualisation";

const container = document.getElementById('root');
if (container !== null) {
  const root = createRoot(container);
  root.render(
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Core />}>
          <Route path="/" element={<Sites />} />
          <Route path="/sites" element={<Sites />} />
          <Route path="/executions" element={<Executions />} />
          <Route path="/visualisation" element={<Visualisation />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
