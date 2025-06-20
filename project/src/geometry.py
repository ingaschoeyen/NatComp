import numpy as np

Point = list[float]

# Uniform distribution
def get_uniform(n: int, dimension: int = 2, low: int = -1, high: int = 1):
    return [[np.random.uniform(low, high) for _ in range(dimension)] for _ in range(n)]

# Normal (Gaussian) distribution
def get_normal(n: int, dimension: int = 2, mu: float = 0, sigma: float = 1):
    return [[np.random.normal(mu, sigma) for _ in range(dimension)] for _ in range(n)]

# TODO Cluster distribution
# Generate the population in a number of clusters which are similar (close)
# Simulates how parties (clusters) are composed of similarly thinking, but distinct, candidates (points),
# or how the voters are divided into similarly thinking groups
def get_cluster(n: int, dimension: int = 2):
    pass

# Calculate euclidean distance between two points in space
def distance_euclid(p1 : Point, p2 : Point):
    return np.linalg.norm(np.array(p1) - np.array(p2))

# Distance between one point and multiple others given a specific distance measure
def point_distances(base_point : Point, points : list[Point], dist_metric = distance_euclid):
    return [dist_metric(base_point, other_point) for other_point in points]

# Returns the index of the goal_point closest the base_point for every point in base_points
def closest_points(base_points : list[Point], goal_points : list[Point], dist_metric = distance_euclid):
    return [np.argmin(point_distances(base_point, goal_points, dist_metric)) for base_point in base_points]

def radius_relative(base_point : list[Point], goal_points : list[Point], closest_w : float, furthest_w : float, dist_metric = distance_euclid):
    distances = point_distances(base_point, goal_points, dist_metric)
    closest, furthest = min(distances), max(distances)
    return (closest * closest_w + furthest * furthest_w) / 2


def compute_norm_entropy(results: list[float]):
    M = len(results)
    if M == 0:
        return 0.0
    norm_entropy = 0.0
    for result in results:
        norm_entropy += result * np.log(result) if result > 0 else 0
    norm_entropy = -norm_entropy / np.log(M)
    return norm_entropy