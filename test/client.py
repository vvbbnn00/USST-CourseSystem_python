import socket

HOST = 'localhost'
PORT = 2333
ADDRESS = (HOST, PORT)


def connect(address):
    myClient = socket.socket()
    myClient.connect(address)
    cmd = '''socket 0.1
test_platform MacOS 0 1.0 a
null
status.get_server_status
{"message": "hello world"}'''
    myClient.send(cmd.encode())
    res = myClient.recv(1024)
    print(res.decode())
    myClient.close()


if __name__ == "__main__":
    connect(ADDRESS)
