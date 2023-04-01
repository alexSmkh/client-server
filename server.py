import logging
import socket
import threading

from config import QUIT_EVENT, HOST, LOGS_PATH, PORT


logger = logging.getLogger(__file__)
USERS = {}


def broadcast(message: bytes, except_client_address: str) -> None:
    for address, user in USERS.items():
        if address != except_client_address:
            user['client'].send(message)


def register_user(client: socket.socket, address: str) -> str | None:
    nickname = client.recv(1024).decode()

    USERS[address] = {
        'nickname': nickname,
        'client': client,
    }

    broadcast(f'{nickname} joined!'.encode(), address)
    client.send('### You have successfully joined the chat ###'.encode())
    logger.info(f'{address}:{nickname} joined the chat')

    return nickname


def handle_connection(client: socket.socket, address: str) -> None:
    nickname = None

    try:
        nickname = register_user(client, address)

        while True:
            message = client.recv(1024).decode()

            if not message or message == QUIT_EVENT:
                logger.info(f'{address}:{nickname} left the chat')
                break

            logger.info(f'{address}:{nickname} send message: {message}')
            broadcast(f'{nickname}: {message}'.encode(), address)
    except (socket.error, ConnectionError):
        logger.exception('Error occurred')
    finally:
        client.close()
        if nickname is not None:
            logger.info(f'{address}:{nickname} disconnected.')
            del USERS[address]
            broadcast(f'### {nickname} left the chat ###'.encode(), address)


def main() -> None:
    logging.basicConfig(
        filename=LOGS_PATH,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
    )

    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((HOST, PORT))
        sock.listen()

        logger.info('The server is running')

        while True:
            client, address = sock.accept()
            address = f'{address[0]}:{address[1]}'
            thread = threading.Thread(
                target=handle_connection,
                args=(client, address),
            )
            thread.daemon = True
            thread.start()

    except KeyboardInterrupt:
        pass
    except (socket.error, ConnectionError):
        logger.exception('Error occurred')
    finally:
        for user in USERS.values():
            user['client'].close()

        if sock is not None:
            sock.close()

        logger.info('The server stopped')
        print('The server stopped')


if __name__ == '__main__':
    main()
