import { Link } from 'react-router-dom';

export default function ForcedLogoutPage() {
    return (
        <>
            <p>You've been forced to disconnect because you are connected in another browser</p>
            <Link to='/'>Go back to Home Page</Link>
        </>
    );
}