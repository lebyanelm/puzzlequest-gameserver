from server import server_instance, socketio_server

if __name__ == '__main__':
    socketio_server.run(server_instance, port=4000)