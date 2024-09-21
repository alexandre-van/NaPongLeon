import numpy as np

# Interpolates between two positions based on a ratio of time passed
def interp_pos(start, end, ratio):
	return start + ratio * (end - start)

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
	contact_point = intersec - seg_normal * r
	ball_center_contact = contact_point + seg_normal * r

	return ball_center_contact, contact_point

# Main function to get ball and padel collision position
def get_position_physic(ball_pos, ball_dest, r, pad, pad_dest):
	b_pos = np.array([ball_pos['x'], ball_pos['y']])
	b_dest = np.array([ball_dest['x'], ball_dest['y']])
	total_ball_dist = np.linalg.norm(b_dest - b_pos)  # Total distance ball will travel

	# Calculate the interpolated position of the padel based on ball travel ratio
	def calc_contact(p1_start, p2_start, p1_end, p2_end):
		travel_ratio = np.linalg.norm(b_dest - b_pos) / total_ball_dist
		p1_interp = interp_pos(np.array([p1_start['x'], p1_start['y']]), np.array([p1_end['x'], p1_end['y']]), travel_ratio)
		p2_interp = interp_pos(np.array([p2_start['x'], p2_start['y']]), np.array([p2_end['x'], p2_end['y']]), travel_ratio)
		return intersec_point(p1_interp, p2_interp, b_pos, b_dest, r)

	# Check all four segments of the padel for a potential collision
	contact_AB, point_AB = calc_contact(pad['A'], pad['B'], pad_dest['A'], pad_dest['B'])
	contact_BC, point_BC = calc_contact(pad['B'], pad['C'], pad_dest['B'], pad_dest['C'])
	contact_CD, point_CD = calc_contact(pad['C'], pad['D'], pad_dest['C'], pad_dest['D'])
	contact_DA, point_DA = calc_contact(pad['D'], pad['A'], pad_dest['D'], pad_dest['A'])

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
		closest_contact, contact_point, segment_name = min(positions, key=lambda item: np.linalg.norm(item[0] - b_pos))
		return {
			'center_at_contact': {'x': closest_contact[0], 'y': closest_contact[1]},
			'point_contact': {'x': contact_point[0], 'y': contact_point[1]},
			'segment': segment_name
		}
	else:
		return None
