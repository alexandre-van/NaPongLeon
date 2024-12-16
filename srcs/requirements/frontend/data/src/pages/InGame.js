import Avatar from '../components/Avatar.js';
import PlayButton from '../components/PlayButton.js';

import { Link } from 'react-router-dom';
import { useUser } from '../contexts/UserContext.js';
import FriendsList from '../components/FriendsList.js';
import logo from '../elements/logo.png'
import { useNavigate } from "react-router-dom";

export default function InGame() {
    const navigate = useNavigate();

    const Cancel = async () => {
        const iframe = document.querySelector('#gameFrame');
		if (iframe) {
			iframe.remove();
		}
        navigate("/");

	};


  return (
    <div>
      <div className="topnav">
        <Link className="active"><img className="logo" src={logo}/></Link>
        <button onClick={Cancel} >EXIT</button>
        <h1>Wait the game please</h1>
      </div>
    </div>
  );
}