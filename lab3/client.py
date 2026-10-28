import numpy as np
import pickle
import socket
from scipy.signal import convolve2d


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


kernel = np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]])


def edge_filter(fragment):
    processed = convolve2d(fragment, kernel, mode="same", boundary="symm")
    return processed


def client_main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("localhost", 2040))
    fragment = receive_all(client_socket)
    processed_fragment = edge_filter(fragment)
    send_all(client_socket, processed_fragment)
    client_socket.close()
    print("Fragment przetworzony i wysłany z powrotem do serwera")


if __name__ == "__main__":
    client_main()
