# knighted/cli.py
import sys
import os
import argparse
from knightcrypt.obfuscation import KnightObfuscator
from knightcrypt.utils import print_banner, log_info, log_success, log_warning, log_error

def main():
    parser = argparse.ArgumentParser(description="KnightCrypt - Advanced Python Encryption")
    parser.add_argument("file", help="Python file to encrypt")
    parser.add_argument("-k", "--key", default="secret", help="Encryption key")
    parser.add_argument("-o", "--output", help="Output filename (optional)")
    parser.add_argument("-l", "--level", choices=["low", "medium", "high"], default="high", help="Obfuscation level")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        log_error(f"File not found: {args.file}")
        sys.exit(1)
        
    print_banner()
    
    obfuscator = KnightObfuscator(key=args.key, level=args.level)
    enc_path = obfuscator.encrypt_file(args.file, args.output)
    
    # Generate wrapper
    wrapper_name = os.path.splitext(args.file)[0] + "_run.py"
    obfuscator.generate_wrapper(enc_path, wrapper_name)
    
    log_success(f"Encrypted {args.file} -> {enc_path}")
    log_success(f"Generated wrapper: {wrapper_name}")
    log_info(f"Run your app with: python {wrapper_name}")
    
    # Display stats
    if hasattr(obfuscator, 'obfuscation_stats'):
        log_info(f"Obfuscation Stats: {obfuscator.obfuscation_stats}")

if __name__ == "__main__":
    main()
