import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import DefaultLayout from './layouts/DefaultLayout.js';
import SpecialLayout from './layouts/SpecialLayout.js';
import HomePage from './pages/HomePage.js'
import GameModePage from './pages/GameModesPage.js';
import Leaderboard from './pages/LeaderboardPage.js';
import LoginPage from './pages/LoginPage.js';
import NewsPage from './pages/NewsPage.js';
import { RegisterPage, RegisterSuccessPage } from './pages/RegisterPage.js';
//import './assets/App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route element={<DefaultLayout />} >
          <Route index element={<HomePage />} />
          <Route path="news" element={<NewsPage />} />
          <Route path="leaderboard" element={<Leaderboard />} />
          <Route path="game-modes" element={<GameModePage />} />
          <Route path="login" element={<LoginPage />} />
          <Route path="*" element={<HomePage />} />
        </Route>

        <Route element={<SpecialLayout />} >
          <Route path="register" element={<RegisterPage />} />
          <Route path="register-success" element={<RegisterSuccessPage />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
