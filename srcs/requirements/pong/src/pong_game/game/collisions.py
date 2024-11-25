import numpy as np
from ..utils.logger import logger

def is_point_near_segment(point, segment_start, segment_end, radius):
    """
    Vérifie si un point est à une distance inférieure ou égale à `radius` d'un segment défini par `segment_start` et `segment_end`.
    """
    # Vecteurs
    seg_vec = segment_end - segment_start
    point_vec = point - segment_start

    # Projection scalaire
    seg_len_sq = np.dot(seg_vec, seg_vec)
    proj = np.dot(point_vec, seg_vec) / seg_len_sq if seg_len_sq != 0 else 0
    proj_clamped = np.clip(proj, 0, 1)

    # Point projeté sur le segment
    closest_point = segment_start + proj_clamped * seg_vec

    # Distance du point projeté au point initial
    distance_sq = np.sum((point - closest_point) ** 2)
    return distance_sq == radius ** 2

# Calculates the intersection point between the ball's trajectory and a segment with the ball's radius
def intersec_point(A, B, ball_pos, ball_dest, r):
	ball_dir = ball_dest - ball_pos  # Ball's direction vector
	seg_dir = B - A  # Segment direction vector
	
	# Check if the ball direction and segment are parallel
	if np.cross(seg_dir, ball_dir) == 0:
		return None, None

	t1 = np.cross((ball_pos - A), ball_dir) / np.cross(seg_dir, ball_dir)
	intersec = A + t1 * seg_dir  # Intersection point on the segment
	
	# Ensure the intersection is within the segment bounds
	if not (0 <= t1 <= 1):
		return None, None

	dist_ball_travel = np.linalg.norm(ball_dest - ball_pos)  # Total ball travel distance
	dist_to_intersec = np.linalg.norm(intersec - ball_pos)  # Distance to intersection
	
	# Check if the intersection is within the distance the ball will travel
	if dist_to_intersec > dist_ball_travel:
		return None, None

	# Calculate normal to the segment
	seg_normal = np.array([-seg_dir[1], seg_dir[0]])
	seg_normal /= np.linalg.norm(seg_normal)  # Normalize

	# Check if the ball is heading towards the segment
	to_dest = np.dot(ball_dest - intersec, seg_normal)
	if to_dest >= 0:
		return None, None

	# Compute contact point by adjusting for ball radius
	contact_point = intersec
	ball_center_contact = contact_point + seg_normal * r

	return ball_center_contact, contact_point

# Main function to get ball and padel collision position
def get_position_physic(ball_pos, ball_dest, r, pad):
    b_pos = np.array([ball_pos['x'], ball_pos['y']])
    b_dest = np.array([ball_dest['x'], ball_dest['y']])

    A = np.array([pad['A']['x'], pad['A']['y']])
    B = np.array([pad['B']['x'], pad['B']['y']])
    C = np.array([pad['C']['x'], pad['C']['y']])
    D = np.array([pad['D']['x'], pad['D']['y']])

    segments = [(A, B), (B, C), (C, D), (D, A)]
    for i, (start, end) in enumerate(segments):
        if is_point_near_segment(b_pos, start, end, r):
            logger.debug("in coll")
            return None  # Collision détectée avec le paddle

    # Check all four segments of the paddle for a potential collision
    contact_AB, point_AB = intersec_point(A, B, b_pos, b_dest, r)
    contact_BC, point_BC = intersec_point(B, C, b_pos, b_dest, r)
    contact_CD, point_CD = intersec_point(C, D, b_pos, b_dest, r)
    contact_DA, point_DA = intersec_point(D, A, b_pos, b_dest, r)

    # Store all potential contact points
    positions = [
        (contact_AB, point_AB, "AB"),
        (contact_BC, point_BC, "BC"),
        (contact_CD, point_CD, "CD"),
        (contact_DA, point_DA, "DA")
    ]

    # Filter out any segments without a valid intersection
    positions = [(c, p, name) for c, p, name in positions if c is not None]

    # Return the closest contact point, if any
    if positions:
        closest_contact, contact_point, segment_name = min(
            positions, key=lambda item: np.linalg.norm(item[0] - b_pos)
        )
        return {
            'center_at_contact': {'x': closest_contact[0], 'y': closest_contact[1]},
            'point_contact': {'x': contact_point[0], 'y': contact_point[1]},
            'segment': segment_name
        }
    else:
        return None

