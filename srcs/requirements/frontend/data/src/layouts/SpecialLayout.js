import SpecialNavigation from "../components/SpecialNavigation";

export default function SpecialLayout({ children, navigate }) {
    return (
        <div className='layout'>
            <header>
                <SpecialNavigation navigate={navigate}/>
            </header>
            <main>
                {children}
            </main>
        </div>
    );
}