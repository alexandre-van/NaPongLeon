import { Link } from 'react-router-dom';

export default function LogoutPage() {
  return (
    <>
      <p>You have successfully log out</p>
      <Link to='/'>Go back to Home Page</Link>
    </>
  );
}
