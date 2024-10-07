import { Outlet } from 'react-router-dom';
import Navigation from '../components/Navigation';

export default function DefaultLayout() {
    return (
        <div className="layout">
            <header>
                <Navigation />
            </header>
            <main>
                <Outlet />
            </main>
        </div>
    );
}
