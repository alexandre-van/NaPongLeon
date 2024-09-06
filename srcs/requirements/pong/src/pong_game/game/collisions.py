
def det(a, b, c, d):
    return a * d - b * c

def on_segment(xi, yi, xj, yj, xk, yk):
    return (min(xi, xj) <= xk <= max(xi, xj)) and (min(yi, yj) <= yk <= max(yi, yj))

def is_point_on_segment(px, py, x1, y1, x2, y2):
    return on_segment(x1, y1, x2, y2, px, py)

def check_collisions(xA, yA, xB, yB, xC, yC, xD, yD):
    d1 = det(xB - xA, yB - yA, xC - xA, yC - yA)
    d2 = det(xB - xA, yB - yA, xD - xA, yD - yA)
    d3 = det(xD - xC, yD - yC, xA - xC, yA - yC)
    d4 = det(xD - xC, yD - yC, xB - xC, yB - yC)

    if (d1 * d2 <= 0) and (d3 * d4 <= 0):
        denom = det(xB - xA, yB - yA, xD - xC, yD - yC)
        if denom == 0:
            if (on_segment(xA, yA, xB, yB, xC, yC) or 
                on_segment(xA, yA, xB, yB, xD, yD) or 
                on_segment(xC, yC, xD, yD, xA, yA) or 
                on_segment(xC, yC, xD, yD, xB, yB)):
                return {'cross': True, 'point': None}
            else:
                return {'cross': False, 'point': None}
        else:
            t = det(xC - xA, yC - yA, xD - xC, yD - yC) / denom
            u = det(xC - xA, yC - yA, xB - xA, yB - yA) / denom
            if 0 <= t <= 1 and 0 <= u <= 1:
                intersection_x = xA + t * (xB - xA)
                intersection_y = yA + t * (yB - yA)
                return {'cross': True, 'point': {'x': intersection_x, 'y': intersection_y}}
            else:
                return {'cross': False, 'point': None}
    else:
        return {'cross': False, 'point': None}
