from colorama import Fore, Style, init; init()
import os, threading

class Console:
    def __init__(self):
        self.locker = threading.Semaphore(value= 1)

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def __lock_print(self, text: str, past: str, color: Fore):
        self.locker.acquire()
        print(f'[{color}{past}{Fore.RESET}] {text}.')
        self.locker.release()

    def loader_banner(self):
        self.clear()
        print(Style.BRIGHT + Fore.WHITE + '''
         _    _ _                     _           
        | |  | | |                   | |          
        | |__| | |     ___   __ _  __| | ___ _ __ 
        |  __  | |    / _ \ / _` |/ _` |/ _ \ '__|
        | |  | | |___| (_) | (_| | (_| |  __/ |   
        |_|  |_|______\___/ \__,_|\__,_|\___|_|    github.com/Its-Vichy/HBot
                ''' + Style.RESET_ALL + Fore.RESET)
    
    def print_success(self, text: str):
        self.__lock_print(text, '+', Fore.LIGHTGREEN_EX)
    
    def print_info(self, text: str):
        self.__lock_print(text, '%', Fore.LIGHTYELLOW_EX)