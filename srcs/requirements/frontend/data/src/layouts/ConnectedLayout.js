import { Outlet } from 'react-router-dom';
import ConnectedNavigation from '../components/ConnectedNavigation.js';

export default function ConnectedLayout() {
  return (
    <div className="layout">
      <header>
        <ConnectedNavigation />
      </header>
      <main>
        <Outlet />
      </main>
    </div>
  );
}
