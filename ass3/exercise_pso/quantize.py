

from PIL import Image
import numpy as np
import sys
from matplotlib import pyplot as plt

# argv: input.png output.png k n max_iter omega local_alpha global_alpha eps

PALETTE_ASS = np.array([
    (175, 198, 114),
    (83, 20, 14),
    (185, 49, 40),
    (124, 148, 71)
])

def PSOptimalPalette(img, k=4, n=10, omega=1, local_alpha=1, global_alpha=1, eps=120, max_iters=10):

    # Init
    iter = 0
    global_best = np.zeros((k, 3))
    local_best = np.zeros((k, 3))
    particles = np.random.random((n, k, 3)) * 255
    velocities = np.zeros((n, k, 3))
    global_quality = np.average(pointsDistances(img, global_best))
    local_quality = np.average(pointsDistances(img, local_best))

    while global_quality > eps and iter < max_iters:
        r1, r2 = np.random.random((n, k, 3)), np.random.random((n, k, 3))
        velocities = omega * velocities + local_alpha * r1 * (local_best - particles) + global_alpha * r2 * (global_best - particles)

        particles += velocities
        particles %= 255

        for i in range(n):
            quality = np.average(pointsDistances(img, particles[i]))
            if quality < global_quality:
                global_best, global_quality = particles[i], quality
            if quality < local_quality:
                local_best, local_quality = particles[i], quality

        iter += 1
        print(iter)
        print("global quality:", global_quality)
        print(global_best)

    return global_best

def quantize(img, palette):
    height, width, _ = np.array(img).shape
    img = np.array(img.getdata())

    distances = pointsDistances(img, palette)
    closest_colour = np.argmin(distances, axis=1)

    img = np.array([[palette[closest_colour[row * width + col]] for row in range(height)] for col in range(width)], dtype=int) # width x height x 3
    # img = np.array([palette[closest_colour[i]] for i in range(img.shape[0])]) # (width * height) x 3

    return img

def pointsDistances(img, palette):
    distances = np.zeros((img.shape[0], len(palette)))
    for i in range(len(palette)):
        euc_dist = np.apply_along_axis(np.linalg.norm, axis=1, arr=img[:, :3] - palette[i])
        distances[:, i] = euc_dist
    return distances


def saveImg(img, outputPath):
    img = Image.fromarray(img.astype(np.uint8)).transpose(Image.Transpose.FLIP_LEFT_RIGHT).transpose(Image.Transpose.ROTATE_90)
    img.save(outputPath)

if __name__ == '__main__':
    img = Image.open(sys.argv[1])
    k, n, max_iter = [int(x) for x in sys.argv[3:6]]
    omega, local_alpha, global_alpha, eps = [float(x) for x in sys.argv[6:]]
    opt_palette = PSOptimalPalette(np.array(img.getdata()), k, n, omega, local_alpha, global_alpha, eps, max_iter)
    quantized = quantize(img, opt_palette)
    saveImg(quantized, sys.argv[2])
