#knighted/runtime.py - the most painful file i wrote because of lines 16-18 not having their respective library installed correctly
import sys
import os
import marshal
import zlib
import struct
import hashlib
import types
import traceback
import gc
import dis
import time
import platform
import subprocess
import ctypes
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from Crypto.Random import get_random_bytes
import threading
import atexit

class KnightRuntimeError(Exception):
    """Custom exception for KnightCrypt runtime errors."""
    pass

class KnightRuntime:
    # Magic bytes to identify valid KnightCrypt files
    MAGIC_HEADER = b'KNIGHT'
    VERSION = 1
    
    # Known debugger processes
    DEBUGGER_PROCESSES = ['devenv.exe', 'ida.exe', 'x64dbg.exe', 'ollydbg.exe', 'gdb', 'lldb']
    
    def __init__(self, encrypted_data: bytes, key: str):
        self.encrypted_data = encrypted_data
        self.key = key
        self.globals = {}
        self.locals = {}
        self._verify_integrity()
        self._check_debuggers()
        
    def _get_key_material(self, password: str) -> tuple:
        """Derives a 256-bit key and IV from the password using PBKDF2."""
        salt = b'somegoofyahhshi'  # Fixed salt for consistency in this demo; in production, store it separately or randomize
        pbkdf2 = hashlib.pbkdf2_hmac('sha256', 
                                     password.encode('utf-8'), 
                                     salt, 
                                     iterations=100000)
        return pbkdf2[:32], pbkdf2[32:44]  # 32 bytes key + 12 bytes IV
        
    def _verify_integrity(self):
        """Verifies the integrity of the runtime module itself."""
        # In a production scenario, you would hash the runtime.py file
        # and compare it against a known good hash embedded here.
        current_file = os.path.abspath(__file__)
        with open(current_file, 'rb') as f:
            content = f.read()
        current_hash = hashlib.sha256(content).hexdigest()
        expected_hash = "your_expected_hash_here"  # Replace with actual hash of this file
        if current_hash != expected_hash:
            raise KnightRuntimeError("Runtime integrity check failed: File may have been tampered with.")
        
    def _check_debuggers(self):
        """Checks for common debugger processes."""
        try:
            if platform.system() == "Windows":
                import psutil
                for proc in psutil.process_iter(['name']):
                    if proc.info['name'].lower() in [db.lower() for db in self.DEBUGGER_PROCESSES]:
                        raise KnightRuntimeError(f"Debugger detected: {proc.info['name']}")
            else:
                # For Linux/Mac, you might use /proc or other methods
                pass
        except ImportError:
            # If psutil is not available, skip this check
            pass
            
    def decrypt_payload(self) -> bytes:
        """
        Decrypts the payload using AES-256-GCM.
        
        Returns:
            bytes: Decrypted compressed marshaled code object.
            
        Raises:
            KnightRuntimeError: If decryption fails or integrity check fails.
        """
        if not self.encrypted_data:
            raise KnightRuntimeError("Empty encrypted data")
            
        try:
            # Extract header and ciphertext
            # Format: [MAGIC(6)] [VERSION(1)] [SALT(8)] [IV(12)] [TAG(16)] [CIPHERTEXT]
            if len(self.encrypted_data) < 6 + 1 + 8 + 12 + 16:
                raise KnightRuntimeError("Invalid file format: too short")
                
            magic = self.encrypted_data[:6]
            if magic != self.MAGIC_HEADER:
                raise KnightRuntimeError(f"Invalid magic header: {magic}")
                
            version = self.encrypted_data[6]
            if version != self.VERSION:
                raise KnightRuntimeError(f"Unsupported version: {version}")
                
            salt = self.encrypted_data[7:15]
            iv = self.encrypted_data[15:27]
            tag = self.encrypted_data[27:43]
            ciphertext = self.encrypted_data[43:]
            
            # Derive key from password and salt
            key, derived_iv = self._get_key_material(self.key)
            
            # Use the stored IV for GCM mode
            cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
            
            # Decrypt and verify tag
            plaintext = cipher.decrypt_and_verify(ciphertext, tag)
            
            return plaintext
            
        except ValueError as e:
            raise KnightRuntimeError(f"Decryption failed: Invalid key or corrupted data. {e}")
        except Exception as e:
            raise KnightRuntimeError(f"Unexpected error during decryption: {e}")
            
    def load_code_object(self, decrypted_data: bytes) -> types.CodeType:
        """
        Decompresses and loads the marshaled code object.
        
        Args:
            decrypted_data (bytes): Decrypted compressed data.
            
        Returns:
            types.CodeType: The compiled code object.
        """
        try:
            # Decompress zlib data
            decompressed = zlib.decompress(decrypted_data)
            
            # Load marshaled code object
            code_obj = marshal.loads(decompressed)
            
            if not isinstance(code_obj, types.CodeType):
                raise KnightRuntimeError("Invalid code object format")
                
            return code_obj
            
        except Exception as e:
            raise KnightRuntimeError(f"Failed to load code object: {e}")
            
    def execute(self, code_obj: types.CodeType) -> None:
        """
        Executes the code object in a controlled environment.
        
        Args:
            code_obj (types.CodeType): The code object to execute.
        """
        try:
            # Create a new frame for isolated execution
            frame = types.FrameType(
                code=code_obj,
                globals=self.globals,
                locals=self.locals
            )
            
            # Execute the code
            exec(code_obj, self.globals, self.locals)
            
        except Exception as e:
            print(f"[!] Execution Error: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            raise KnightRuntimeError(f"Execution failed: {e}")
            
    def run(self) -> None:
        """Main entry point to decrypt and execute the payload."""
        try:
            decrypted_data = self.decrypt_payload()
            code_obj = self.load_code_object(decrypted_data)
            self.execute(code_obj)
        except KnightRuntimeError as e:
            print(f"[!] KnightCrypt Runtime Error: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"[!] Unexpected Runtime Error: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            sys.exit(1)
        finally:
            self._cleanup_memory()
            
    def _cleanup_memory(self):
        """Clears sensitive data from memory."""
        # Clear globals and locals
        self.globals.clear()
        self.locals.clear()
        
        # Garbage collect
        gc.collect()
        
        # Optionally, overwrite encrypted data with zeros
        if hasattr(self, 'encrypted_data'):
            self.encrypted_data = b'\x00' * len(self.encrypted_data)

def load_and_run(filepath: str, key: str) -> None:
    """
    Convenience function to load and run an encrypted file.
    
    Args:
        filepath (str): Path to the encrypted .kn file.
        key (str): Decryption key.
    """
    try:
        with open(filepath, 'rb') as f:
            encrypted_data = f.read()
            
        runtime = KnightRuntime(encrypted_data, key)
        runtime.run()
        
    except FileNotFoundError:
        print(f"[!] File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"[!] I/O Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KnightRuntimeError as e:
        print(f"[!] KnightCrypt Runtime Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[!] Unexpected Error: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
