

from PIL import Image
import numpy as np
import sys
from matplotlib import pyplot as plt
from quantization import quantize, saveImg, mse

# sys.argv: input.png output_file_name k n max_iter omega local_alpha global_alpha eps

# Palette from the assignment
PALETTE_ASS = np.array([
    (175, 198, 114),
    (83, 20, 14),
    (185, 49, 40),
    (124, 148, 71)
])

def PSOptimalPalette(img, height, width, k=4, n=10, omega=1, local_alpha=1, global_alpha=1, eps=120, max_iters=10):
    iter = 0
    global_best = np.zeros((k, 3))
    local_bests = np.zeros((n, k, 3))
    particles = np.random.random((n, k, 3)) * 255
    velocities = np.zeros((n, k, 3))
    global_quality = mse(img, quantize(img, global_best))
    init_local_quality = mse(img, quantize(img, local_bests[0]))
    local_qualities = [init_local_quality for _ in range(n)]
    glob_best_qualities = []
    glob_best_palettes = []

    # print("Iteration: ", end="", flush=True)

    while global_quality > eps and iter < max_iters:
        r1, r2 = np.random.random((n, k, 3)), np.random.random((n, k, 3))
        velocities = omega * velocities + local_alpha * r1 * (local_bests - particles) + global_alpha * r2 * (global_best - particles)

        particles += velocities
        particles = np.clip(particles, 0, 255)
        # particles %= 255

        for i in range(n):
            quality = mse(img, quantize(img, particles[i]))
            if quality < global_quality:
                global_best, global_quality = particles[i], quality
            if quality < local_qualities[i]:
                local_bests[i], local_qualities[i] = particles[i], quality

        # Print and save intermediate results
        iter += 1
        # print(iter, end=" ", flush=True)
        # print("global quality:", global_quality)
        glob_best_qualities.append(global_quality)
        if iter % 5 == 0:
            glob_best_palettes.append(global_best)
            saveImg(np.reshape(quantize(img, global_best), (height, width, 3)), "./gb-" + sys.argv[2] + "-" + str(iter))

    # print()
    # print("Final quality:", global_quality)
    saveStats(glob_best_qualities, k, n, omega, local_alpha, global_alpha)

    return global_best

def saveStats(glob_best_qualities, k, n, omega, local_alpha, global_alpha):
    fig, ax = plt.subplots()
    plt.plot([i + 1 for i in range(len(glob_best_qualities))], glob_best_qualities)
    plt.title("Final quality: %d" % glob_best_qualities[-1])
    plt.xlabel("Iteration")
    plt.ylabel("MSE")
    textstr = '\n'.join((
    r'k=%d' % (k, ),
    r'n=%d' % (n, ),
    r'$\omega=%.2f$' % (omega, ),
    r'$\alpha\mathrm{1}=%.2f$' % (local_alpha, ),
    r'$\alpha\mathrm{2}=%.2f$' % (global_alpha, )))

    # these are matplotlib.patch.Patch properties
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

    # place a text box in upper left in axes coords
    ax.text(0.78, 0.95, textstr, transform=ax.transAxes, fontsize=14,
            verticalalignment='top', bbox=props)

    plt.savefig(sys.argv[2] + ".stats.png")

# WIP Arguments for debugger
# sys.argv = ["quantize.py", "/home/jarom/school/NatComp/ass3/exercise_pso/image.png", "output.png", "5", "10", "10", "0.1", "0.1", "0.1", "100"]

if __name__ == '__main__':
    img = Image.open(sys.argv[1])
    height, width, _ = np.array(img).shape # image dimensions
    img = np.array(img.getdata())[:, :3] # convert to np array with shape (n, 3) == (points, channels)
    output_path = sys.argv[2]
    k, n, max_iter = [int(x) for x in sys.argv[3:6]]
    omega, local_alpha, global_alpha, eps = [float(x) for x in sys.argv[6:]]

    print(output_path, "started")

    opt_palette = PSOptimalPalette(img, height, width, k, n, omega, local_alpha, global_alpha, eps, max_iter)
    quantized = quantize(img, opt_palette)
    saveImg(np.reshape(quantized, (height, width, 3)), output_path)

    print(output_path, "finished")
