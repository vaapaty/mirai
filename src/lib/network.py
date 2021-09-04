import socket

class Network:
    def __init__(self, socket_session: socket.socket):
        self.sock = socket_session
    
    def close_socket(self):
        self.sock.close()

    def send_packet(self, content: str):
        try:
            self.sock.send(content.encode('utf-8'))
            return True
        except:
            return False
    
    def bulk_send_packet(self, packets: list):
        res = None
        for packet in packets:
            packet = f'\r\033[0m{packet}\n'

            res = self.send_packet(packet)
        
        return res

    def recv_packet(self):
        # Optimization ?
        data = None
        while True:
            try:
                data = self.sock.recv(1024).decode('utf-8').strip().split('\n')[0]
                if data not in ['\n', '', 'None', None, False, 'False']:
                    break

            except Exception:
                data = False
                break

        return data
