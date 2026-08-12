import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import DashboardPage from './pages/DashboardPage';
import AddCoursePage from './pages/AddCoursePage';
import CoursePage from './pages/CoursePage';

import LandingPage from './pages/LandingPage';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route element={<Layout />}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/add" element={<AddCoursePage />} />
          <Route path="/course/:id" element={<CoursePage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
