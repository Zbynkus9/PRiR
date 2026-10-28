from multiprocessing import Pool
from PIL import Image
import numpy as np
from scipy.signal import convolve2d

kernel = np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]])


def image_spliter(image_array):
    tiles = []
    M = image_array.shape[0] // 2
    N = image_array.shape[1] // 2

    for x in range(0, M * 2, M):
        for y in range(0, N * 2, N):
            tiles.append(image_array[x : x + M, y : y + N])

    return tiles


def image_merger(tiles):
    top_half = np.hstack((tiles[0], tiles[1]))
    bottom_half = np.hstack((tiles[2], tiles[3]))
    merged_image = np.vstack((top_half, bottom_half))
    return merged_image


def process_tile(tile):
    processed = convolve2d(tile, kernel, mode="same", boundary="symm")
    return processed


if __name__ == "__main__":
    image_pil = Image.open("./logo.png").convert("L")

    image_data = np.array(image_pil)

    tiles = image_spliter(image_data)

    with Pool(4) as p:
        processed_tiles = p.map(process_tile, tiles)

    final_image_data = image_merger(processed_tiles)

    final_image_data = np.clip(final_image_data, 0, 255).astype(np.uint8)
    final_image = Image.fromarray(final_image_data)
    final_image.save("./logo_processed.png")
