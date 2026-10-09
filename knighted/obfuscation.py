# knighted/obfuscator.py
import ast
import marshal
import os
import zlib
import random
import string
import struct
from knightcrypt.utils import log_info, log_success, log_warning

class VariableRenamer(ast.NodeTransformer):
    """Renames all variables to random hex strings."""
    def __init__(self):
        self.counter = 0
    
    def _new_name(self):
        name = f"_0x{self.counter:x}"
        self.counter += 1
        return name

    def visit_Name(self, node):
        if isinstance(node.ctx, (ast.Store, ast.Load)):
            new_node = ast.Name(id=self._new_name(), ctx=node.ctx)
            ast.copy_location(new_node, node)
            return new_node
        return node

    def visit_FunctionDef(self, node):
        # Rename function arguments too
        for arg in node.args.args:
            arg.arg = self._new_name()
        return self.generic_visit(node)

class StringEncryptor(ast.NodeTransformer):
    """Encrypts all string literals using XOR."""
    def __init__(self, key="default"):
        self.key = key
    
    def visit_Str(self, node):
        original_str = node.s
        encrypted_bytes = bytes([ord(c) ^ ord(self.key[i % len(self.key)]) for i, c in enumerate(original_str)])
        # Return a call to a helper function that decrypts at runtime
        # For simplicity, we'll just replace with a decrypted constant
        # In a real scenario, you'd generate a decryption function
        return ast.Constant(value=original_str) # Simplified for demo

class ControlFlowFlattener(ast.NodeVisitor):
    """
    Converts basic blocks into a switch-case style loop.
    This makes static analysis very difficult.
    """
    def __init__(self):
        self.blocks = []
        self.current_block_id = 0
    
    def visit_If(self, node):
        # Create two blocks: one for True, one for False
        true_block_id = self.current_block_id + 1
        false_block_id = self.current_block_id + 2
        
        self.blocks.append({
            'id': self.current_block_id,
            'type': 'if',
            'condition': ast.unparse(node.test),
            'true_target': true_block_id,
            'false_target': false_block_id,
            'body': [ast.dump(stmt) for stmt in node.body],
            'orelse': [ast.dump(stmt) for stmt in node.orelse]
        })
        
        self.current_block_id += 3
        self.visit_children(node)

    def visit_Assign(self, node):
        self.blocks.append({
            'id': self.current_block_id,
            'type': 'assign',
            'target': ast.unparse(node.targets[0]),
            'value': ast.unparse(node.value),
            'next': self.current_block_id + 1
        })
        self.current_block_id += 1

    def visit_children(self, node):
        for child in ast.iter_child_nodes(node):
            self.visit(child)

    def generate_switch_code(self):
        """Generates Python code for a switch-case loop."""
        code = "state = 0\nwhile True:\n"
        for block in self.blocks:
            indent = "    "
            if block['type'] == 'if':
                code += f"{indent}if state == {block['id']}:\n"
                code += f"{indent}    if {block['condition']}:\n"
                code += f"{indent}        state = {block['true_target']}\n"
                code += f"{indent}    else:\n"
                code += f"{indent}        state = {block['false_target']}\n"
            elif block['type'] == 'assign':
                code += f"{indent}if state == {block['id']}:\n"
                code += f"{indent}    {block['target']} = {block['value']}\n"
                code += f"{indent}    state = {block['next']}\n"
        code += "    break\n"
        return code

class KnightObfuscator:
    def __init__(self, key="default_key", level="high"):
        self.key = key
        self.level = level  # low, medium, high
        self.obfuscation_stats = {}

    def obfuscate_source(self, source_code):
        tree = ast.parse(source_code)
        
        # Step 1: Rename Variables
        renamer = VariableRenamer()
        tree = renamer.visit(tree)
        self.obfuscation_stats['variables_renamed'] = renamer.counter
        
        # Step 2: Encrypt Strings (Simplified)
        encryptor = StringEncryptor(key=self.key)
        tree = encryptor.visit(tree)
        
        # Step 3: Flatten Control Flow (if level is high)
        if self.level == "high":
            flattener = ControlFlowFlattener()
            flattener.visit(tree)
            switch_code = flattener.generate_switch_code()
            # Append the switch code to the end of the source
            source_code = source_code + "\n" + switch_code
            
        # Step 4: Add Opaque Predicates
        predicate = "if (hash(str(__name__)) % 2 == 0): pass\n"
        source_code = predicate + source_code
        
        return source_code

    def encrypt_file(self, input_path, output_path=None):
        if output_path is None:
            output_path = input_path.replace('.py', '_enc.kn')
            
        with open(input_path, 'r') as f:
            source = f.read()
            
        # Obfuscate
        obfuscated_source = self.obfuscate_source(source)
        
        # Compile to bytecode
        code_obj = compile(obfuscated_source, input_path, 'exec')
        
        # Marshal and Compress
        marshaled = marshal.dumps(code_obj)
        compressed = zlib.compress(marshaled)
        
        # Encrypt with XOR
        encrypted = bytes([b ^ ord(self.key[i % len(self.key)]) for i, b in enumerate(compressed)])
        
        # Write output with header
        header = len(self.key).to_bytes(2, 'big')
        key_bytes = self.key.encode('utf-8')
        
        with open(output_path, 'wb') as f:
            f.write(header)
            f.write(key_bytes)
            f.write(encrypted)
            
        return output_path

    def generate_wrapper(self, enc_filepath, wrapper_name="run_knight.py"):
        wrapper_content = '''
import sys
import os
from knightcrypt.runtime import load_and_run

def main():
    enc_path = os.path.join(os.path.dirname(__file__), "{enc_filename}")
    key = "{key}"
    try:
        load_and_run(enc_path, key)
    except Exception as e:
        print(f"[-] KnightCrypt Runtime Error: {{e}}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''.format(enc_filename=os.path.basename(enc_filepath), key=self.key)
        
        with open(wrapper_name, 'w') as f:
            f.write(wrapper_content)
