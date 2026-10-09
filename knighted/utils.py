# knighted/utils.py
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_banner():
    print(f"{Colors.CYAN}{'='*50} {Colors.ENDC}")
    print(f"{Colors.HEADER}  KnightCrypt - Python Library for File Encryption {Colors.ENDC}")
    print(f"{Colors.CYAN}{'='*50} {Colors.ENDC}")
    print(f"{Colors.GREEN}[+] Welcome to KnightCrypt! {Colors.ENDC}")
    print(f"{Colors.YELLOW}[!] Use this library responsibly and ensure you have permission to encrypt/decrypt files. {Colors.ENDC}")
    print(f"{Colors.CYAN}{'='*50}{Colors.ENDC}")

def log_info(msg):
    print(f"{Colors.BLUE}[INFO]{Colors.ENDC} {msg}")

def log_success(msg):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.ENDC} {msg}")

def log_warning(msg):
    print(f"{Colors.YELLOW}[WARNING]{Colors.ENDC} {msg}")

def log_error(msg):
    print(f"{Colors.RED}[ERROR]{Colors.ENDC} {msg}")
