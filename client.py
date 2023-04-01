import os
import socket
import threading

from config import QUIT_EVENT, HOST, PORT


def read_messages(client: socket.socket, is_running: threading.Event) -> None:
    try:
        while is_running.is_set():
            message = client.recv(1024).decode()
            print(message)
    except (socket.error, ConnectionError, ConnectionResetError):
        print('### Connection lost ###')


def send_messages(client: socket.socket, is_running: threading.Event) -> None:
    try:
        nickname = input('### Choose your nickname: ')
        client.send(nickname.encode())

        while is_running.is_set():
            message = input('')
            client.send(message.encode())

            if message == QUIT_EVENT:
                is_running.clear()
                break
    except (socket.error, ConnectionError, ConnectionResetError):
        print('### Connection lost ###')


def main() -> None:
    client = None
    is_running = None

    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))

        is_running = threading.Event()
        is_running.set()

        read_msgs_thread = threading.Thread(
            target=read_messages,
            args=(client, is_running),
            daemon=True,
        )
        send_msgs_thread = threading.Thread(
            target=send_messages,
            args=(client, is_running),
            daemon=True,
        )

        read_msgs_thread.start()
        send_msgs_thread.start()

        read_msgs_thread.join()
        send_msgs_thread.join()

    except ConnectionRefusedError:
        print('### Connection refused ###')
    except KeyboardInterrupt:
        pass
    finally:
        print('### You have been disconnected ###')
        if client is not None:
            client.close()

        if is_running is not None and not is_running.is_set():
            os._exit(0)


if __name__ == '__main__':
    main()
