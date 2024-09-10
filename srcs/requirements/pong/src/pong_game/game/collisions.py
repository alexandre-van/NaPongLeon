<<<<<<< HEAD
import math

def get_vector_direction(start, end):
	return { 
		'x': end['x'] - start['x'],
		'y': end['y'] - start['y']
	}


def get_contact_point(ball_center, r, direction, wall):
	if direction['x'] > 0:
		t = (wall['x'] - (ball_center['x'] + r)) / direction['x']
	elif direction['x'] < 0:
		t = (wall['x'] - (ball_center['x'] - r)) / direction['x']
	else:
		return None
	contact = {
		'y': ball_center['y'] + direction['y'] * t,
		'x': wall['x']
	}
	if wall['y']['bottom'] <= contact['y'] <= wall['y']['top']:
		return (contact)
	else:
		return None
=======
def cross_product(v1, v2):
    return v1['x'] * v2['y'] - v1['y'] * v2['x']

def is_point_on_segment(p, seg_start, seg_end):
    """Vérifie si le point p est sur le segment défini par seg_start et seg_end."""
    return (min(seg_start['x'], seg_end['x']) <= p['x'] <= max(seg_start['x'], seg_end['x']) and
            min(seg_start['y'], seg_end['y']) <= p['y'] <= max(seg_start['y'], seg_end['y']))

def check_collisions(p1, p2, p3, p4):
    """Vérifie si les segments (p1, p2) et (p3, p4) se croisent et renvoie le point de croisement."""
    # Calcul des vecteurs des segments
    d1 = {'x': p2['x'] - p1['x'], 'y': p2['y'] - p1['y']}
    d2 = {'x': p4['x'] - p3['x'], 'y': p4['y'] - p3['y']}

    # Déterminer si les segments sont parallèles
    denominator = cross_product(d1, d2)
    if denominator == 0:
        return None  # Les segments sont parallèles et ne se croisent pas

    # Calcul des différences entre les points de départ des segments
    diff = {'x': p3['x'] - p1['x'], 'y': p3['y'] - p1['y']}

    # Calcul des paramètres t et u (position des points d'intersection)
    t = cross_product(diff, d2) / denominator
    u = cross_product(diff, d1) / denominator

    # Vérifier si t et u sont dans l'intervalle [0, 1] pour indiquer que les segments se croisent
    if 0 <= t <= 1 and 0 <= u <= 1:
        # Calculer le point de croisement
        intersection_point = {'x': p1['x'] + t * d1['x'], 'y': p1['y'] + t * d1['y']}

        # Vérifier que le point d'intersection est bien sur les segments
        if is_point_on_segment(intersection_point, p1, p2) and is_point_on_segment(intersection_point, p3, p4):
            return intersection_point
        else:
            return None  # Le point calculé n'est pas sur les segments

    return None  # Les segments ne se croisent pas
>>>>>>> 701bd7645a59dfe00177594a5322371256e1259a
