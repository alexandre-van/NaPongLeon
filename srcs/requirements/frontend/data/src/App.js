import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, useNavigate, useLocation, Navigate } from 'react-router-dom';

import ConnectedLayout from './layouts/ConnectedLayout.js';
import DefaultLayout from './layouts/DefaultLayout.js';
import SpecialLayout from './layouts/SpecialLayout.js';

import HomePage from './pages/HomePage.js';
import Formations from './pages/Formations.js';
import GameModePage from './pages/GameModesPage.js';
import Leaderboard from './pages/LeaderboardPage.js';
import LoginPage from './pages/LoginPage.js';
import NewsPage from './pages/NewsPage.js';
import { RegisterPage, RegisterSuccessPage } from './pages/RegisterPage.js';

import useAuth from './hooks/useAuth.js';

import ProtectedRoute from './components/ProtectedRoute.js';
//import './assets/App.css';

function AppContent() {
  const { isAuthenticated, user, loading, checkAuth } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    checkAuth();
  }, [location.pathname]);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
      <Routes>
        <Route element={isAuthenticated ? <ConnectedLayout /> : <DefaultLayout />} >
          <Route index element={<HomePage isAuthenticated={isAuthenticated} />} />
          <Route path="news" element={<NewsPage />} />
          <Route path="leaderboard" element={<Leaderboard />} />
          <Route path="game-modes" element={<GameModePage />} />
          <Route path="login" element={<LoginPage />} />
          <Route path="logout" element={<Navigate to="/" replace />} />
          <Route path="*" element={<HomePage />} />
        </Route>

        <Route element={<ProtectedRoute isAuthenticated={isAuthenticated} />} >
          <Route element={<ConnectedLayout />} >
            <Route path="formations" element={<Formations />} />
          </Route>
        </Route>

        <Route element={<SpecialLayout />} >
          <Route path="register" element={<RegisterPage />} />
          <Route path="register-success" element={<RegisterSuccessPage />} />
        </Route>
      </Routes>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;
