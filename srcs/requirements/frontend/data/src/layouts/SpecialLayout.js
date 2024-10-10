import { Outlet } from 'react-router-dom';
import SpecialNavigation from "../components/SpecialNavigation";

export default function SpecialLayout() {
  return (
    <div className="layout">
      <header>
        <SpecialNavigation />
      </header>
      <main>
        <Outlet />
      </main>
    </div>
  );
}
