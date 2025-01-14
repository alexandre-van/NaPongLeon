import { useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, useLocation, Navigate } from 'react-router-dom';

import { useUser, UserProvider } from './contexts/UserContext.js';
import { WebSocketProvider } from './contexts/WebSocketContext.js';

import ConnectedLayout from './layouts/ConnectedLayout.js';
import RedirectOnRefresh from './RedirectOnRefresh';

import HomePage from './pages/HomePage.js';
import Formations from './pages/Formations.js';
import PongPage from './pages/PongPage.js';
import GameHistory from './pages/GameHistoryPage.js';
import LoginPage from './pages/LoginPage.js';
import Login2FAPage from './pages/Login2FAPage.js';
import ForgotPasswordPage from './pages/ForgotPasswordPage.js';
import ResetPasswordPage from './pages/ResetPasswordPage.js';
import HagarrioPage from './pages/HagarrioPage.js';
import Auth42Success from './components/Auth42Success.js';
import UserPersonalizationPage from './pages/UserPersonalizationPage.js';
import { RegisterPage, RegisterSuccessPage } from './pages/RegisterPage.js';
import 'bootstrap/dist/css/bootstrap.min.css';
import '../src/App.css'
import Profile from './pages/Profile.js'

import ProtectedRoute from './components/ProtectedRoute.js';
import WaitMatchmaking from './pages/WaitMatchmaking.js';
import GameModeSelector from './pages/GameModePage.js';
import FriendsButton from './components/FriendsButton.js';
import NotifButton from './components/NotifButton.js';
import AIpong from './pages/AIpong.js';
import InGame from './pages/InGame.js';
import SocialPage from './pages/SocialPage.js';
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
          <Route path="pong/matchmaking" element={<WaitMatchmaking />} />
          <Route path="pong/ai-pong" element={<AIpong />} />
          <Route path="pong/ingame" element={<InGame />} />
          <Route path="pong/game-mode" element={<GameModeSelector />} />
          <Route path="hagarrio" element={<HagarrioPage />} />
          <Route path="gamehistory" element={<GameHistory />} />
          <Route path="logout" element={<Navigate to="/logout-success" replace />} />
          <Route path='login/success' element={<Auth42Success />} />
          <Route path="profile" element={<Profile/>}/>
          <Route path="social-network" element={<SocialPage />} />
          <Route path="reset-password" element={<ForgotPasswordPage />}/>
          <Route path="*" element={<HomePage />} />
        </Route>
        <Route element={isAuthenticated ? <ConnectedLayout /> : <ResetPasswordPage />} >
          <Route index element={<HomePage isAuthenticated={isAuthenticated} user={user} />} />
          <Route />
          <Route path="reset-password/:uid/:token" element={<ResetPasswordPage />}/>
        </Route>
        <Route element={<ProtectedRoute isAuthenticated={isAuthenticated} />} >
          <Route element={<ConnectedLayout />} >
            <Route path="formations" element={<Formations />} />
            <Route path="user-personalization" element={<UserPersonalizationPage />} />
          </Route>
        </Route>

        <Route>
          <Route path="login" element={<LoginPage />} />
          <Route path="login/2FA" element={<Login2FAPage />} />
          <Route path="forgot-password" element={<ForgotPasswordPage />}/>
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
          <RedirectOnRefresh />
          <AppContent />
          <div className="background"></div>
          <FriendsButton />
          <NotifButton />
        </WebSocketProvider>
      </UserProvider>
    </Router>
  );
}
export default App;
