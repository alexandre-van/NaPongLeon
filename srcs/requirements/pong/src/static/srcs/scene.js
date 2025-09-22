import * as THREE from '../.js/three.module.js';
import { renderer, camera } from './renderer.js';

const scene = new THREE.Scene();
const loader = new THREE.TextureLoader();
const protocol = location.protocol;
const host = window.location.hostname;
const port = window.location.port;

loader.load(`${location.origin}/api/pong/static/pong/texture/sunset.jpg`, function (texture) {
	scene.background = texture;
});


function cleanup() {
	// Nettoyer les objets dans la scène
	scene.traverse(function (object) {
	  if (object instanceof THREE.Mesh) {
		// Libérer la géométrie et le matériau
		if (object.geometry) object.geometry.dispose();
  
		// Si le matériau est un matériau de type "Material"
		if (object.material && object.material.isMaterial) {
		  disposeMaterial(object.material);
		} else if (Array.isArray(object.material)) {
		  // Si plusieurs matériaux sont utilisés
		  object.material.forEach(disposeMaterial);
		}
	  }
	});
  
	// Libérer le renderer
	renderer.dispose();
  
	// Supprimer le canvas du DOM
	document.body.removeChild(renderer.domElement);
  
	// Libérer la caméra
	//camera = null;
}
  
function disposeMaterial(material) {
	// Libérer les différentes textures (si elles existent)
	if (material.map) material.map.dispose();
	if (material.lightMap) material.lightMap.dispose();
	if (material.bumpMap) material.bumpMap.dispose();
	if (material.normalMap) material.normalMap.dispose();
	if (material.specularMap) material.specularMap.dispose();
	if (material.envMap) material.envMap.dispose();
  
	// Libérer le matériau lui-même
	material.dispose();
}

export { scene, cleanup };