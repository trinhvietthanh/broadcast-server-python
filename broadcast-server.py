import argparse
import socket
import threading


HOST = '127.0.0.1'
PORT = 8081
clients = []
user_numbers = {}
user_count = 0


def handle_client(client_socket, client_address):
    global user_count
    user_count += 1
    user_number = user_count
    user_numbers[client_socket] = user_number
    print(f"New connection: User {user_number} ({client_address})")
    clients.append(client_socket)
    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                print(f"User {user_number}: {message}")
                broadcast_message(
                    f"User {user_number}: {message}", client_socket)

            else:
                break
    except Exception as e:
        print(f"Error handling User {user_number}: {e}")
    finally:
        print(f"User {user_number} disconnected.")
        clients.remove(client_socket)
        del user_numbers[client_socket]
        broadcast_message(
            f"User {user_number} has disconnected.", client_socket)

        client_socket.close()


def broadcast_message(message, source_client):
    for client in clients:
        if client != source_client:
            try:
                client.send(message.encode('utf-8'))
            except Exception as e:
                print(f"Error sending message to client: {e}")


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Server started on {HOST}:{PORT}")
    try:
        while True:
            client_socket, client_address = server_socket.accept()
            client_thread = threading.Thread(
                target=handle_client, args=(client_socket, client_address))
            client_thread.start()
    except KeyboardInterrupt:
        print("Server shutting down...")
    finally:
        server_socket.close()


def receive_messages(client_socket):
    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                print(message)
            else:
                break
    except Exception as e:
        print(f"Error receiving message: {e}")
    finally:
        client_socket.close()


def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    receive_thread = threading.Thread(
        target=receive_messages, args=(client_socket,))
    receive_thread.start()

    try:
        while True:
            message = input()
            if message:
                client_socket.send(message.encode('utf-8'))
    except KeyboardInterrupt:
        print("Client shutting down...")
    finally:
        client_socket.close()


def main():
    parser = argparse.ArgumentParser(description="Broadcast Server CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser('start', help='Start the server')
    subparsers.add_parser(
        'connect', help='Connect to the server as a client')
    args = parser.parse_args()

    if args.command == 'start':
        start_server()
    elif args.command == 'connect':
        start_client()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
