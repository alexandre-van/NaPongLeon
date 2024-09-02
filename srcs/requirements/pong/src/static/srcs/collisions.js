
function det(a, b, c, d) {
	return a * d - b * c;
}

function onSegment(xi, yi, xj, yj, xk, yk) {
	return (Math.min(xi, xj) <= xk && xk <= Math.max(xi, xj)) && (Math.min(yi, yj) <= yk && yk <= Math.max(yi, yj));
}

function isPointOnSegment(px, py, x1, y1, x2, y2) {
	return onSegment(x1, y1, x2, y2, px, py);
}

function checkCollisions(xA, yA, xB, yB, xC, yC, xD, yD) {
	const d1 = det(xB - xA, yB - yA, xC - xA, yC - yA);
    const d2 = det(xB - xA, yB - yA, xD - xA, yD - yA);
    const d3 = det(xD - xC, yD - yC, xA - xC, yA - yC);
    const d4 = det(xD - xC, yD - yC, xB - xC, yB - yC);

    if ((d1 * d2 <= 0) && (d3 * d4 <= 0)) {
        const denom = det(xB - xA, yB - yA, xD - xC, yD - yC);
        if (denom === 0) {
            if (onSegment(xA, yA, xB, yB, xC, yC) || onSegment(xA, yA, xB, yB, xD, yD) ||
                onSegment(xC, yC, xD, yD, xA, yA) || onSegment(xC, yC, xD, yD, xB, yB)) {
                return { croise: true, point: null };
            } else {
                return { croise: false, point: null };
            }
        } else {
            const t = det(xC - xA, yC - yA, xD - xC, yD - yC) / denom;
            const u = det(xC - xA, yC - yA, xB - xA, yB - yA) / denom;
            if (0 <= t && t <= 1 && 0 <= u && u <= 1) {
                const intersectionX = xA + t * (xB - xA);
                const intersectionY = yA + t * (yB - yA);
                return { croise: true, point: { x: intersectionX, y: intersectionY } };
            } else {
                return { croise: false, point: null };
            }
        }
    } else {
        return { croise: false, point: null };
    }
}

export { checkCollisions };