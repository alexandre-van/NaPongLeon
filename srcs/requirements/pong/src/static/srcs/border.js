import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.136.0/build/three.module.js';
import scene from './scene.js';

let borderTop, borderBottom, borderLeft, borderRight;

const arenaLength = 80;
const arenaWidth = 60;
const wallWidth = 1;
const wallHeight = 2;

function createBorders() {
    const borderGeometry = new THREE.BoxGeometry(arenaLength + wallWidth * 2, wallWidth, wallHeight);
    const sideBorderGeometry = new THREE.BoxGeometry(wallWidth, arenaWidth, wallHeight);

    const borderMaterial = new THREE.MeshStandardMaterial({ color: 0x00ff00 });

    borderTop = new THREE.Mesh(borderGeometry, borderMaterial);
    borderBottom = new THREE.Mesh(borderGeometry, borderMaterial);
    borderLeft = new THREE.Mesh(sideBorderGeometry, borderMaterial);
    borderRight = new THREE.Mesh(sideBorderGeometry, borderMaterial);

    borderTop.position.set(0, arenaWidth / 2 + wallWidth / 2, 1);
    borderBottom.position.set(0, -arenaWidth / 2 - wallWidth / 2, 1);
    borderLeft.position.set(-arenaLength / 2 - wallWidth / 2, 0, 1);
    borderRight.position.set(arenaLength / 2 + wallWidth / 2, 0, 1);

    scene.add(borderTop);
    scene.add(borderBottom);
    scene.add(borderLeft);
    scene.add(borderRight);
}


function createDashedLine() {
    const points = [];
    const numberOfPoints = arenaWidth/10;
    const lineLength = arenaWidth;
    const step = lineLength / numberOfPoints;
    for (let i = -lineLength / 2; i <= lineLength / 2; i += step) {
      points.push(new THREE.Vector3(0, i, 0));
    }
    const lineGeometry = new THREE.BufferGeometry().setFromPoints(points);
    const lineMaterial = new THREE.LineDashedMaterial({
      color: 0x00ff00,
      dashSize: 0.5,
      gapSize: 0.5
    });
    const dashedLine = new THREE.Line(lineGeometry, lineMaterial);
    dashedLine.computeLineDistances();
    scene.add(dashedLine);
}


createBorders();
createDashedLine();

export { borderTop, borderBottom, borderLeft, borderRight, arenaLength, arenaWidth, wallWidth };