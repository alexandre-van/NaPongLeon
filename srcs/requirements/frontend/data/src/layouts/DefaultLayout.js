import Navigation from '../components/Navigation'

export default function DefaultLayout({ children, navigate }) {
    return (
        <div className="layout">
            <header>
                <Navigation navigate={navigate} />
            </header>
            <main>
                {children}
            </main>
        </div>
    );
}