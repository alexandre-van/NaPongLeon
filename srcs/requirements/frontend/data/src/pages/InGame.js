import { useNavigate, useLocation } from "react-router-dom";
import LeaveButton from "../components/LeaveButton.js";
import { useEffect } from "react";


export default function InGame() {
    const navigate = useNavigate();
    const location = useLocation();
    
    const { gameService, gameId } = location.state || {}; // Récupérer les données transmises via navigation

      useEffect(() => {
        try {
            if (gameService && gameId) {
          
                const existingIframe = document.querySelector('#gameFrame');
                if (existingIframe) {
                    existingIframe.remove(); // Nettoyer toute iframe existante
                }
            
                const iframe = document.createElement('iframe');
                iframe.id = "gameFrame";
                iframe.src = `${gameService}/?gameId=${gameId}`;
                iframe.style.position = "fixed";
                iframe.style.top = "56px";
                iframe.style.left = "-1%";
                iframe.style.width = "102%";
                iframe.style.height = "95%";
                iframe.style.border = "none";
                iframe.style.zIndex = "999";
                iframe.scrolling = "no";
                iframe.sandbox = "allow-scripts allow-same-origin";
                // Ajouter l'iframe au DOM
                document.body.appendChild(iframe)
            }

        } catch (error) {
            console.error("Error during iframe setup:", error);
            navigate("/pong");
        }
      
        return () => {
            const iframe = document.querySelector('#gameFrame');
            if (iframe) {
                iframe.remove();
            }
        };
    }, [gameId]);
  

    const Cancel = async () => {
        const iframe = document.querySelector('#gameFrame');
        if (iframe) {
            iframe.contentWindow.postMessage('stop_game', '*');
            await new Promise(resolve => setTimeout(resolve, 100));
            iframe.remove();
        }
        navigate("/pong");
    };

    return (
        <div>
            <h1 className="wait">Wait for the game to load</h1>
            <LeaveButton />
        </div>
    );
}
