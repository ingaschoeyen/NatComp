

from PIL import Image, ImageTransform
import numpy as np
import sys
from matplotlib import pyplot as plt

# argv: input.png output.png

PALLETE_DEF = np.array([
    (175, 198, 114),
    (83, 20, 14),
    (185, 49, 40),
    (124, 148, 71)
])

def quantize(img, pallete = PALLETE_DEF):
    height, width, _ = np.array(img).shape
    img = np.array(img.getdata())

    distances = np.zeros((img.shape[0], len(pallete)))
    for i in range(len(pallete)):
        euc_dist = np.apply_along_axis(np.linalg.norm, axis=1, arr=img[:, :3] - PALLETE_DEF[i])
        distances[:, i] = euc_dist

    closest_colour = np.argmin(distances, axis=1)

    img = np.array([[pallete[closest_colour[row * width + col]] for row in range(height)] for col in range(width)], dtype=int) # width x height x 3
    # img = np.array([pallete[closest_colour[i]] for i in range(img.shape[0])]) # (width * height) x 3

    # print(img.shape)

    return img

def saveImg(img, outputPath):
    img = Image.fromarray(img.astype(np.uint8)).transpose(Image.Transpose.FLIP_LEFT_RIGHT).transpose(Image.Transpose.ROTATE_90)
    img.save(outputPath)

if __name__ == '__main__':
    saveImg(quantize(Image.open(sys.argv[1])), sys.argv[2])
