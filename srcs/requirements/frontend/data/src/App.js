import { useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, useLocation, Navigate } from 'react-router-dom';

import { useUser, UserProvider } from './contexts/UserContext.js';
import { WebSocketProvider } from './contexts/WebSocketContext.js';

import ConnectedLayout from './layouts/ConnectedLayout.js';
import DefaultLayout from './layouts/DefaultLayout.js';
import SpecialLayout from './layouts/SpecialLayout.js';

import HomePage from './pages/HomePage.js';
import ForcedLogoutPage from './pages/ForcedLogoutPage.js';
import Formations from './pages/Formations.js';
import PongPage from './pages/PongPage.js';
import Leaderboard from './pages/LeaderboardPage.js';
import LoginPage from './pages/LoginPage.js';
import HagarrioPage from './pages/HagarrioPage.js';
import Auth42Success from './components/Auth42Success.js';
import UserPersonalizationPage from './pages/UserPersonalizationPage.js';
import { RegisterPage, RegisterSuccessPage } from './pages/RegisterPage.js';
import 'bootstrap/dist/css/bootstrap.min.css';
import '../src/App.css'
import Profile from './pages/Profile.js'

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
        <Route element={isAuthenticated ? <ConnectedLayout /> : <LoginPage />} >
          <Route index element={<HomePage isAuthenticated={isAuthenticated} user={user} />} />
          <Route />
          <Route path="pong" element={<PongPage />} />
          <Route path="hagarrio" element={<HagarrioPage />} />
          <Route path="leaderboard" element={<Leaderboard />} />
          <Route path="logout" element={<Navigate to="/logout-success" replace />} />
          <Route path='login/success' element={<Auth42Success />} />
          <Route path="profile" element={<Profile/>}/>
          <Route path="*" element={<HomePage />} />
        </Route>

        <Route element={<ProtectedRoute isAuthenticated={isAuthenticated} />} >
          <Route element={<ConnectedLayout />} >
            <Route path="formations" element={<Formations />} />
            <Route path="user-personalization" element={<UserPersonalizationPage />} />
          </Route>
        </Route>

        <Route>
          <Route path="login" element={<LoginPage />} />
          <Route path="forced-logout" element={<ForcedLogoutPage />} />
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
