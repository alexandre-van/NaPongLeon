import React, { useEffect } from 'react';

export default function HagarrioPage() {
  useEffect(() => {
    // Construire l'URL de l'iframe
    const gameServiceName = "hagarrio"; // Remplacez par le bon nom du service
    const gameUrl = `${location.origin}/api/${gameServiceName}/`;

    // Créer et configurer l'iframe
    const iframe = document.createElement('iframe');
    iframe.src = gameUrl;
    iframe.style.position = "fixed";        // Fixe pour qu'il reste à la même position
    iframe.style.top = "75px";                 // Aligner en haut de la page
    iframe.style.left = "0";                // Aligner à gauche de la page
    iframe.style.width = "100vw";           // Largeur : 100% de la fenêtre
    iframe.style.height = "93vh"; // Hauteur : 100% de la fenêtre moins la hauteur de la barre
    iframe.style.border = "none";           // Supprimer les bordures
    iframe.style.zIndex = "9999";           // Mettre l'iframe au premier plan
    iframe.sandbox = "allow-scripts allow-same-origin"; // Sécuriser l'iframe
    iframe.id = "gameFrame";

    // Ajouter l'iframe au body
    document.body.appendChild(iframe);

    // Nettoyage : retirer l'iframe lorsque le composant est démonté
    return () => {
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
