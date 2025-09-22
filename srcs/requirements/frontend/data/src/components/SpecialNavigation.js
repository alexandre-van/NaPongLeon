import { Link } from 'react-router-dom';

export default function SpecialNavigation() {
  return (
    <div role='nav' className="nav-container">
      <div className="main-nav">
        <Link to='/'>SPICE PON</Link>
      </div>
    </div>
  );
}
