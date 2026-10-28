import pickle
import socket
import numpy as np
from PIL import Image


def split_image(image_array, n_clients):
    tiles = []
    step = image_array.shape[0] // n_clients

    for i in range(n_clients):
        if i == n_clients - 1:
            tiles.append(image_array[i * step :, :])
        else:
            tiles.append(image_array[i * step : (i + 1) * step, :])

    return tiles


def merge_image(tiles):
    merged_image = np.vstack(tiles)

    merged_image = np.clip(merged_image, 0, 255).astype(np.uint8)
    return Image.fromarray(merged_image)


def send_all(sock, data):
    data = pickle.dumps(data)
    sock.sendall(len(data).to_bytes(4, byteorder="big"))
    sock.sendall(data)


def receive_all(sock):
    length = int.from_bytes(sock.recv(4), byteorder="big")
    data = b""
    while len(data) < length:
        packet = sock.recv(4096)
        if not packet:
            break
        data += packet
    return pickle.loads(data)


def server_main(image_path, n_clients):
    image = Image.open(image_path).convert("L")
    image_array = np.array(image)

    fragments = split_image(image_array, n_clients)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind(("localhost", 2040))
    server_socket.listen(n_clients)
    print("Serwer nasłuchuje...")

    processed_fragments = []
    for i in range(n_clients):
        client_socket, client_adress = server_socket.accept()
        print(f"Połączono z klientem {i+1}: {client_adress}")

        send_all(client_socket, fragments[i])
        processed_fragment = receive_all(client_socket)
        processed_fragments.append(processed_fragment)

        client_socket.close()

    result_image = merge_image(processed_fragments)
    result_image.save("processed_image.png")
    print("Obraz przetworzony zapisany jako processed_image.png")


if __name__ == "__main__":
    server_main("/home/jakub/Documents/PRiR/lab3/logo.png", 4)
