import { Outlet } from 'react-router-dom';
import ConnectedNavigation from '../components/ConnectedNavigation.js';
import FriendsList from '../components/FriendsList.js';

export default function ConnectedLayout() {
  return (
    <div className="layout">
      <header>
        <ConnectedNavigation />
      </header>
      <main>
        <Outlet />
      </main>
      <FriendsList />
    </div>
  );
}
