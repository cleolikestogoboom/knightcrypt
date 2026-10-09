"""
Author: Sancho (@sanchoforza / @gloriasancho on Discord)
Version: 1.0.0
License: MIT
"""

__version__ = "1.0.0"
__author__ = "Sancho"
__discord__ = "@sanchoforza / @gloriasancho"
__license__ = "MIT"

# Import core classes for easy access
from knightcrypt.obfuscation import KnightObfuscator
from knightcrypt.cli import main as cli_main

# Optional: Expose key functions for programmatic use
def encrypt_file(input_path, output_path=None, key="default", level="low"):
    """
    Encrypts a Python file using KnightCrypt.
    
    Args:
        input_path (str): Path to the .py file to encrypt.
        output_path (str): Optional path for the encrypted output.
        key (str): Encryption key.
        level (str): Obfuscation level ('low', 'medium', 'high').
        
    Returns:
        str: Path to the generated encrypted file.
    """
    obf = KnightObfuscator(key=key, level=level)
    return obf.encrypt_file(input_path, output_path)

def decrypt_file(enc_path, key="default"):
    """
    Decrypts a KnightCrypt encrypted file.
    
    Args:
        enc_path (str): Path to the .kn encrypted file.
        key (str): Decryption key.
        
    Returns:
        str: The decrypted source code.
    """
    from knightcrypt.runtime import KnightRuntime
    runtime = KnightRuntime.from_file(enc_path, key)
    return runtime.decrypt_source()
 
__all__ = [
    "KnightObfuscator",
    "encrypt_file",
    "decrypt_file",
    "cli_main",
]
