import React, { useEffect, useRef } from 'react';

export default function HagarrioPage() {
  // Utiliser useRef pour garder une référence à l'iframe
  const iframeRef = useRef(null);

  useEffect(() => {
    // Construire l'URL de l'iframe
    const gameServiceName = "hagarrio"; // Remplacez par le bon nom du service
    const gameUrl = `${location.origin}/api/${gameServiceName}/`;

    // Créer et configurer l'iframe
    const iframe = document.createElement('iframe');
    iframe.src = gameUrl;
    iframe.style.position = "fixed";                    // Fixe pour qu'il reste à la même position
    iframe.style.left = "0";                            // Aligner à gauche de la page
    iframe.style.width = "100%";                       // Largeur : 100% de la fenêtre
    iframe.style.height = "94.5%";                       // Hauteur : 100% de la fenêtre moins la hauteur de la barre
    iframe.style.border = "none";                       // Supprimer les bordures
    iframe.style.zIndex = "999";                       // Mettre l'iframe au premier plan
    iframe.sandbox = "allow-scripts allow-same-origin"; // Sécuriser l'iframe
    iframe.id = "gameFrame";


    // Sauvegarder la référence de l'iframe
    iframeRef.current = iframe;

    // Ajouter l'écouteur d'événements pour le postMessage
    const handleMessage = (event) => {
      // Vérifier l'origine du message si nécessaire
      // if (event.origin !== "votre_origine_attendue") return;

      if (event.data === 'refresh') {
        console.log("Refreshing iframe...");
        // Rafraîchir l'iframe en rechargeant son URL
        if (iframeRef.current) {
          iframeRef.current.src = iframeRef.current.src;
        }
      }
    };

    // Ajouter l'écouteur d'événements
    window.addEventListener('message', handleMessage);

    // Ajouter l'iframe au body
    document.body.appendChild(iframe);

    // Nettoyage : retirer l'iframe lorsque le composant est démonté
    return () => {
      window.removeEventListener('message', handleMessage);
      const existingIframe = document.querySelector('#gameFrame');
      if (existingIframe) {
        existingIframe.remove();
      }
    };
  }, []); // Le tableau vide [] signifie que l'effet ne s'exécute qu'au montage et au démontage

  return (
    <div>
    </div>
  );
}
