import { useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, useLocation, Navigate } from 'react-router-dom';

import { useUser, UserProvider } from './contexts/UserContext.js';
import { WebSocketProvider } from './contexts/WebSocketContext.js';

import ConnectedLayout from './layouts/ConnectedLayout.js';
import DefaultLayout from './layouts/DefaultLayout.js';
import SpecialLayout from './layouts/SpecialLayout.js';

import HomePage from './pages/HomePage.js';
import Formations from './pages/Formations.js';
import GameModePage from './pages/GameModesPage.js';
import Leaderboard from './pages/LeaderboardPage.js';
import LoginPage from './pages/LoginPage.js';
import LogoutPage from './pages/LogoutPage.js';
import NewsPage from './pages/NewsPage.js';
import Auth42Success from './components/Auth42Success.js';
import UserPersonalizationPage from './pages/UserPersonalizationPage.js';
import { RegisterPage, RegisterSuccessPage } from './pages/RegisterPage.js';


import ProtectedRoute from './components/ProtectedRoute.js';
//import './assets/App.css';

function AppContent() {
  const { user, isAuthenticated, loading, /*checkAuth*/ } = useUser();
  const location = useLocation();

  /*useEffect(() => {
    checkAuth();
  }, [location.pathname], checkAuth());*/

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
      <Routes>
        <Route element={isAuthenticated ? <ConnectedLayout /> : <DefaultLayout />} >
          <Route index element={<HomePage isAuthenticated={isAuthenticated} user={user} />} />
          <Route />
          <Route path="news" element={<NewsPage />} />
          <Route path="leaderboard" element={<Leaderboard />} />
          <Route path="game-modes" element={<GameModePage />} />
          <Route path="logout" element={<Navigate to="/logout-success" replace />} />
          <Route path='login/success' element={<Auth42Success />} />
          <Route path="*" element={<HomePage />} />
        </Route>

        <Route element={<ProtectedRoute isAuthenticated={isAuthenticated} />} >
          <Route element={<ConnectedLayout />} >
            <Route path="formations" element={<Formations />} />
            <Route path="user-personalization" element={<UserPersonalizationPage />} />
          </Route>
        </Route>

        <Route element={<SpecialLayout />} >
          <Route path="login" element={<LoginPage />} />
          <Route path="logout-success" element={<LogoutPage /> } />
          <Route path="register" element={<RegisterPage />} />
          <Route path="register-success" element={<RegisterSuccessPage />} />
        </Route>
      </Routes>
  );
}

function App() {
  return (
    <Router>
      <UserProvider>
        <WebSocketProvider>
          <AppContent />
        </WebSocketProvider>
      </UserProvider>
    </Router>
  );
}
export default App;
