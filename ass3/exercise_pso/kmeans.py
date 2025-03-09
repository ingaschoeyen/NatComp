from PIL import Image
import numpy as np
import sys
from sklearn.cluster import KMeans
from matplotlib import pyplot as plt
from quantization import quantize, saveImg, mse

# sys.argv: input.png output_path k

if __name__ == '__main__':
    img = Image.open(sys.argv[1])
    height, width, _ = np.array(img).shape # image dimensions
    img = np.array(img.getdata())[:, :3] # convert to np array with shape (n, 3) == (points, channels)
    k = int(sys.argv[3])
    output_path = sys.argv[2]

    print(output_path, "started")

    kmeans = KMeans(n_clusters=k, n_init="auto").fit(img)
    opt_palette = kmeans.cluster_centers_
    quantized = quantize(img, opt_palette)
    # quantized = KMeans(n_clusters=k, random_state=0, n_init="auto").fit_transform(img)
    saveImg(np.reshape(quantized, (height, width, 3)), sys.argv[2])

    print(output_path, "finished, quality:", mse(img, quantized))
