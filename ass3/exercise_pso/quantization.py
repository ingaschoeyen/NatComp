import numpy as np
from PIL import Image

# quantize a np array <img> using <palette>
def quantize(img, palette):
    distances = pointsDistances(img, palette)
    closest_colour = np.argmin(distances, axis=1)
    quantized = np.array([palette[closest_colour[i]] for i in range(img.shape[0])]) # (width * height) x 3
    return quantized

# Distance of each point in <img> to each colour in <palette>
def pointsDistances(img, palette):
    distances = np.zeros((img.shape[0], len(palette)))
    for i in range(len(palette)):
        square_diff = np.square(img - palette[i])
        norm = np.sum(square_diff, axis=1)
        distances[:, i] = norm
    return distances

# Save np array <img> produced by <quantize> as a file to <outputPath>
def saveImg(img, outputPath):
    img = Image.fromarray(img.astype(np.uint8))
    img.save(outputPath + ".png")

# Average of mean squared error
def mse(a, b):
    diff = a - b
    return np.average(np.sum(np.square(diff), axis=1))

pic = []
for r in range(0, 256, 4):
    for g in range(0, 256, 4):
        for b in range(0, 256, 4):
            pic.append((r, g, b))

# generate a baseline image
# x = lambda rgb : (rgb[0], rgb[1], rgb[2])
# saveImg(np.reshape(np.array(sorted(pic, key=x)), (512, 512, 3)), "baseline.png")
