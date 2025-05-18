import numpy as np

Point = list[float]

# Calculate euclidean distance between two points in space
def distance_euclid(p1 : Point, p2 : Point):
    return np.linalg.norm(np.array(p1) - np.array(p2))

# Distance between one point and multiple others given a specific distance measure
def point_distances(base_point : Point, points : list[Point], dist_metric = distance_euclid):
    return [dist_metric(base_point, other_point) for other_point in points]

# Returns the index of the goal_point closest the base_point for every point in base_points
def closest_points(base_points : list[Point], goal_points : list[Point], dist_metric = distance_euclid):
    return [np.argmin(point_distances(base_point, goal_points, dist_metric)) for base_point in base_points]
