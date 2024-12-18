import { Link } from 'react-router-dom';
import logo from '../elements/logo.png'
import { useNavigate } from "react-router-dom";

export default function InGame() {
    const navigate = useNavigate();

    const Cancel = async () => {
      const iframe = document.querySelector('#gameFrame');
      if (iframe) {
          iframe.contentWindow.postMessage('stop_game', '*');
          await new Promise(resolve => setTimeout(resolve, 100));
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