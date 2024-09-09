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
        // Default Layout
        <Route element={<DefaultLayout />} >
          <Route index element={<HomePage />} />
          <Route path="news" element={<NewsPage />} />
          <Route path="leaderboard" element={<Leaderboard />} />
          <Route path="game-modes" element={<GameModePage />} />
          <Route path="login" element={<LoginPage />} />
          <Route path="*" element={<HomePage />} />
        </Route>

        // Special Layout
        <Route element={<SpecialLayout />} >
          <Route path="register" element={<RegisterPage />} />
          <Route path="register-success" element={<RegisterSuccessPage />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;

/*import { useState } from 'react';
import HomePage from './pages/HomePage.js'
import AboutPage from './pages/AboutPage.js'
import './assets/App.css';
import GameModePage from './pages/GameModesPage.js';
import Leaderboard from './pages/LeaderboardPage.js';
import LoginPage from './pages/LoginPage.js';
import RegisterPage from './pages/RegisterPage.js';

function App() {
  const [currentPage, setCurrentPage] = useState('home');

  const navigate = (page) => {
    setCurrentPage(page);
  };

  const renderPage = () => {
    switch (currentPage) {
      case 'home':
        return <HomePage navigate={navigate} />;
      case 'about':
        return <AboutPage navigate={navigate} />;
      case 'game-modes':
        return <GameModePage navigate={navigate} />;
      case 'leaderboard':
        return <Leaderboard navigate={navigate} />;
      case 'login':
        return <LoginPage navigate={navigate} />;
      case 'register':
        return <RegisterPage navigate={navigate} />
      default:
        return <HomePage navigate={navigate} />;
    }
  };

  return (
    <div className="App">
      {renderPage()}
    </div>
  );
}

export default App;*/
