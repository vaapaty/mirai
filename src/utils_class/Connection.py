import functools, threading, socketserver, http.server, socket, time
from utils_class import Console

__HTTP_SERVER_PORT__ = 8080

class FileServer(threading.Thread):
    def __init__(self, console: Console.Console):
        # Todo: Disable logs and put them to file, if anyone know how to make that, make pull requests^^
        self.handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory= '../bin/')
        threading.Thread.__init__(self)
        self.console = console
        self.http_port = __HTTP_SERVER_PORT__
    
    def run(self):
        with socketserver.TCPServer(('0.0.0.0', self.http_port), self.handler) as httpd:
            self.console.print_info(f'File server started on port: {self.http_port}')
            httpd.serve_forever()

class TcpConnection:
    def __init__(self, session: socket.socket, ip: str):
        self.colors = Console.Color()
        self.session = session
        self.ip = ip

    def kill_session(self, reason: str, send: bool= False):
        try:
            if send:
                self.send_packet([f'You have been get disconnected: {reason}'], True)
        
            self.session.close()
            return True
        except Exception as err:
            return False

    def send_packet(self, packets: list, new_line: bool= False, timeout: float= 0):
        err= False

        for packet in packets:
            packet = f'\r{self.colors.reset}{packet}\n' if new_line else f'{self.colors.reset}{packet}'

            try:
                self.session.send(packet.encode('utf-8'))
                time.sleep(timeout)
            except:
                err = True
                break
        
        return err
    
    def recv_packet(self, content: str= False):
        if content:
            self.send_packet([content])
        
        data = None
        while True:
            try:
                data = self.session.recv(1024).decode('utf-8').strip().split('\n')[0]
                if data not in ['\n', '', 'None', None, False, 'False']:
                    break

            except Exception as err:
                data = False
                break

        return data