import * as THREE from '../../.js/three.module.js';
import { scene } from '../scene.js';

function createBorders(data) {
    const borderGeometry = new THREE.BoxGeometry(data.size.x + data.wallWidth * 2, data.wallWidth, data.size.z);
    const sideBorderGeometry = new THREE.BoxGeometry(data.wallWidth, data.size.y, data.size.z);

    const borderMaterial = new THREE.MeshStandardMaterial({ color: 0xffffff });

    const borderTop = new THREE.Mesh(borderGeometry, borderMaterial);
    const borderBottom = new THREE.Mesh(borderGeometry, borderMaterial);
    const borderLeft = new THREE.Mesh(sideBorderGeometry, borderMaterial);
    const borderRight = new THREE.Mesh(sideBorderGeometry, borderMaterial);

    borderTop.position.set(0, data.size.y / 2 + data.wallWidth / 2, data.size.z / 2);
    borderBottom.position.set(0, -data.size.y / 2 - data.wallWidth / 2, data.size.z / 2);
    borderLeft.position.set(-data.size.x / 2 - data.wallWidth / 2, 0, data.size.z / 2);
    borderRight.position.set(data.size.x / 2 + data.wallWidth / 2, 0, data.size.z / 2);

    scene.add(borderTop);
    scene.add(borderBottom);
    scene.add(borderLeft);
    scene.add(borderRight);
}


function createDashedLine(data) {
    const points = [];
    const numberOfPoints = data.size.y/4;
    const lineLength = data.size.y;
    const step = lineLength / numberOfPoints;
    for (let i = -lineLength / 2; i <= lineLength / 2; i += step) {
      points.push(new THREE.Vector3(0, i, 0));
    }
    const lineGeometry = new THREE.BufferGeometry().setFromPoints(points);
    const lineMaterial = new THREE.LineDashedMaterial({
      color: 0xffffff ,
      dashSize: 0.5,
      gapSize: 0.5
    });
    const dashedLine = new THREE.Line(lineGeometry, lineMaterial);
    dashedLine.computeLineDistances();
    scene.add(dashedLine);
}

export { createBorders, createDashedLine };
