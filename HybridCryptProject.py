"""
Interactive, chainable hybrid cipher tool.
Features:
- Menu of 6 algorithms:
  1) Caesar
  2) Affine
  3) Hill (2x2)
  4) Rail Fence
  5) DES (CBC)
  6) AES (CBC)

- User can choose algorithms in any order. After each encryption step they can exit or add another algorithm.
- Session (algorithm order + parameters + final ciphertext) is saved to `session.json` so decryption can be run later.
- Decryption automatically reverses the applied algorithms using stored parameters.

Notes:
- Classical ciphers operate on text strings. Modern ciphers (DES/AES) operate on bytes and their output (iv+ct) is base64-encoded to produce an ASCII string that can be fed into subsequent classical layers.
- AES key must be 16/24/32 bytes (the program enforces 16/24/32). DES key must be 8 bytes.
- Hill 2x2 matrix is validated for invertibility mod 26 before use.

Security: This is an educational tool only. Do NOT use for real secrets.

Dependencies: pycryptodome (pip install pycryptodome)

Run: python hybrid_dynamic.py
"""
import json
import os
import math
import base64
from Crypto.Cipher import AES, DES
from Crypto.Util.Padding import pad, unpad

SESSION_FILE = 'session.json'

# ----------------------------- Helpers -----------------------------

def to_b64(b: bytes) -> str:
    return base64.b64encode(b).decode('ascii')


def from_b64(s: str) -> bytes:
    return base64.b64decode(s.encode('ascii'))


def save_session(session: dict):
    with open(SESSION_FILE, 'w') as f:
        json.dump(session, f, indent=2)


def load_session() -> dict:
    with open(SESSION_FILE, 'r') as f:
        return json.load(f)

# ----------------------------- Classical Ciphers -----------------------------

class Caesar:
    @staticmethod
    def encrypt(text: str, shift: int) -> str:
        out = []
        for ch in text:
            if 'A' <= ch <= 'Z': out.append(chr((ord(ch)-65+shift)%26+65))
            elif 'a' <= ch <= 'z': out.append(chr((ord(ch)-97+shift)%26+97))
            else: out.append(ch)
        return ''.join(out)

    @staticmethod
    def decrypt(text: str, shift: int) -> str:
        return Caesar.encrypt(text, -shift)

class Affine:
    @staticmethod
    def egcd(a,b):
        if a==0: return (b,0,1)
        g,y,x = Affine.egcd(b%a,a)
        return (g, x - (b//a)*y, y)

    @staticmethod
    def modinv(a,m):
        g,x,_ = Affine.egcd(a,m)
        if g != 1:
            raise ValueError('no modular inverse for a mod m')
        return x % m

    @staticmethod
    def encrypt(text: str, a: int, b: int) -> str:
        if math.gcd(a,26) != 1:
            raise ValueError('a must be coprime with 26')
        out = []
        for ch in text:
            if ch.isalpha():
                base = 65 if ch.isupper() else 97
                out.append(chr((a*(ord(ch)-base)+b)%26 + base))
            else:
                out.append(ch)
        return ''.join(out)

    @staticmethod
    def decrypt(text: str, a: int, b: int) -> str:
        a_inv = Affine.modinv(a,26)
        out = []
        for ch in text:
            if ch.isalpha():
                base = 65 if ch.isupper() else 97
                out.append(chr((a_inv*((ord(ch)-base)-b))%26 + base))
            else:
                out.append(ch)
        return ''.join(out)

class Hill2x2:
    @staticmethod
    def _nums(s: str):
        return [ord(c.upper())-65 for c in s if c.isalpha()]

    @staticmethod
    def _text(nums):
        return ''.join(chr(n%26 + 65) for n in nums)

    @staticmethod
    def _det2(m):
        return (m[0][0]*m[1][1] - m[0][1]*m[1][0]) % 26

    @staticmethod
    def _inv2(m):
        det = Hill2x2._det2(m)
        for x in range(26):
            if (det * x) % 26 == 1:
                det_inv = x
                break
        else:
            raise ValueError('matrix not invertible mod 26')
        a,b = m[0]
        c,d = m[1]
        return [[( d * det_inv) % 26, ((-b) * det_inv) % 26], [((-c) * det_inv) % 26, ( a * det_inv) % 26]]

    @staticmethod
    def encrypt(text: str, matrix) -> str:
        nums = Hill2x2._nums(text)
        if len(nums) % 2 == 1:
            nums.append(23)  # 'X'
        out = []
        for i in range(0, len(nums), 2):
            x1, x2 = nums[i], nums[i+1]
            y1 = (matrix[0][0]*x1 + matrix[0][1]*x2) % 26
            y2 = (matrix[1][0]*x1 + matrix[1][1]*x2) % 26
            out.extend([y1, y2])
        return Hill2x2._text(out)

    @staticmethod
    def decrypt(text: str, matrix) -> str:
        nums = Hill2x2._nums(text)
        inv = Hill2x2._inv2(matrix)
        out = []
        for i in range(0, len(nums), 2):
            y1, y2 = nums[i], nums[i+1]
            x1 = (inv[0][0]*y1 + inv[0][1]*y2) % 26
            x2 = (inv[1][0]*y1 + inv[1][1]*y2) % 26
            out.extend([x1, x2])
        return Hill2x2._text(out)

class RailFence:
    @staticmethod
    def encrypt(text: str, rails: int) -> str:
        if rails <= 1: return text
        fence = ['' for _ in range(rails)]
        r, d = 0, 1
        for ch in text:
            fence[r] += ch
            r += d
            if r == 0 or r == rails-1:
                d *= -1
        return ''.join(fence)

    @staticmethod
    def decrypt(text: str, rails: int) -> str:
        if rails <= 1: return text
        n = len(text)
        pattern = list(range(rails)) + list(range(rails-2,0,-1))
        cycle = len(pattern)
        counts = [0]*rails
        for i in range(n):
            counts[pattern[i%cycle]] += 1
        segs = []
        idx = 0
        for c in counts:
            segs.append(text[idx:idx+c])
            idx += c
        ptrs = [0]*rails
        out = []
        for i in range(n):
            r = pattern[i%cycle]
            out.append(segs[r][ptrs[r]])
            ptrs[r] += 1
        return ''.join(out)

# ----------------------------- Modern Ciphers (DES/AES in CBC) -----------------------------

class AESCBC:
    @staticmethod
    def encrypt(text: str, key: bytes) -> str:
        if len(key) not in (16,24,32):
            raise ValueError('AES key must be 16/24/32 bytes long')
        iv = os.urandom(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        ct = cipher.encrypt(pad(text.encode('utf-8'), AES.block_size))
        return to_b64(iv + ct)

    @staticmethod
    def decrypt(b64blob: str, key: bytes) -> str:
        blob = from_b64(b64blob)
        iv, ct = blob[:16], blob[16:]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        return pt.decode('utf-8')

class DESCBC:
    @staticmethod
    def encrypt(text: str, key: bytes) -> str:
        if len(key) != 8:
            raise ValueError('DES key must be 8 bytes long')
        iv = os.urandom(8)
        cipher = DES.new(key, DES.MODE_CBC, iv)
        ct = cipher.encrypt(pad(text.encode('utf-8'), DES.block_size))
        return to_b64(iv + ct)

    @staticmethod
    def decrypt(b64blob: str, key: bytes) -> str:
        blob = from_b64(b64blob)
        iv, ct = blob[:8], blob[8:]
        cipher = DES.new(key, DES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), DES.block_size)
        return pt.decode('utf-8')

# ----------------------------- Menu and Flow -----------------------------

ALGO_MENU = {
    '1': 'Caesar',
    '2': 'Affine',
    '3': 'Hill2x2',
    '4': 'RailFence',
    '5': 'DES',
    '6': 'AES'
}


def get_algo_choice() -> str:
    print('Choose algorithm:')
    for k,v in ALGO_MENU.items():
        print(f"  {k}. {v}")
    choice = input('Enter number: ').strip()
    if choice not in ALGO_MENU:
        print('Invalid choice')
        return get_algo_choice()
    return ALGO_MENU[choice]


def ask_params_for_algo(algo: str) -> dict:
    params = {}
    if algo == 'Caesar':
        params['shift'] = int(input('Enter shift (integer): '))
    elif algo == 'Affine':
        params['a'] = int(input("Enter 'a' (coprime with 26): "))
        params['b'] = int(input("Enter 'b' (integer): "))
    elif algo == 'Hill2x2':
        while True:
            vals = list(map(int, input('Enter 4 integers (a b c d) for 2x2 matrix: ').split()))
            if len(vals) != 4:
                print('Enter exactly 4 integers')
                continue
            matrix = [[vals[0], vals[1]], [vals[2], vals[3]]]
            det = Hill2x2._det2(matrix)
            if math.gcd(det,26) != 1:
                print('Matrix not invertible mod 26 — choose another matrix')
                continue
            params['matrix'] = matrix
            break
    elif algo == 'RailFence':
        params['rails'] = int(input('Enter number of rails (n): '))
    elif algo == 'DES':
        while True:
            key = input('Enter DES key (8 chars): ').encode('utf-8')
            if len(key) != 8:
                print('DES key must be exactly 8 bytes (8 chars).')
                continue
            params['key_b64'] = to_b64(key)
            break
    elif algo == 'AES':
        while True:
            key = input('Enter AES key (16/24/32 chars): ').encode('utf-8')
            if len(key) not in (16,24,32):
                print('AES key must be 16, 24 or 32 bytes long.')
                continue
            params['key_b64'] = to_b64(key)
            break
    return params


def apply_encrypt(algo: str, params: dict, text: str) -> str:
    # Each algorithm receives and returns a string for chaining.
    if algo == 'Caesar':
        return Caesar.encrypt(text, params['shift'])
    if algo == 'Affine':
        return Affine.encrypt(text, params['a'], params['b'])
    if algo == 'Hill2x2':
        return Hill2x2.encrypt(text, params['matrix'])
    if algo == 'RailFence':
        return RailFence.encrypt(text, params['rails'])
    if algo == 'DES':
        key = from_b64(params['key_b64'])
        return DESCBC.encrypt(text, key)
    if algo == 'AES':
        key = from_b64(params['key_b64'])
        return AESCBC.encrypt(text, key)
    raise ValueError('Unknown algorithm')


def apply_decrypt(algo: str, params: dict, text: str) -> str:
    if algo == 'Caesar':
        return Caesar.decrypt(text, params['shift'])
    if algo == 'Affine':
        return Affine.decrypt(text, params['a'], params['b'])
    if algo == 'Hill2x2':
        return Hill2x2.decrypt(text, params['matrix'])
    if algo == 'RailFence':
        return RailFence.decrypt(text, params['rails'])
    if algo == 'DES':
        key = from_b64(params['key_b64'])
        return DESCBC.decrypt(text, key)
    if algo == 'AES':
        key = from_b64(params['key_b64'])
        return AESCBC.decrypt(text, key)
    raise ValueError('Unknown algorithm')

# ----------------------------- User Flows -----------------------------

def encrypt_flow():
    print('== ENCRYPT MODE ==')
    current = input('Enter initial plaintext: ')
    session = {'steps': []}

    while True:
        algo = get_algo_choice()
        params = ask_params_for_algo(algo)
        try:
            new_text = apply_encrypt(algo, params, current)
        except Exception as e:
            print('Error during encryption:', e)
            continue
        # record step
        session['steps'].append({'algo': algo, 'params': params})
        print(f"Applied {algo}. Output (preview):{new_text[:200]}")
        current = new_text
        action = input("Type 'add' to chain another algorithm, 'exit' to finish encryption: ").strip().lower()
        if action == 'add':
            continue
        else:
            # finalize
            session['final_ciphertext'] = current
            save_session(session)
            print('Encryption complete.')
            print('Algorithms used: ' + ' -> '.join(s['algo'] for s in session['steps']))
            print('Final ciphertext (first 500 chars):')
            print(current[:500])
            print(f"Session saved to: {SESSION_FILE}")
            return


def decrypt_flow():
    print('== DECRYPT MODE ==')
    if not os.path.exists(SESSION_FILE):
        print('No session.json found. Please run encryption first or provide a session file named session.json')
        return
    session = load_session()
    ciphertext = input("Enter ciphertext to decrypt (leave empty to use stored one): ")
    if not ciphertext:
        ciphertext = session.get('final_ciphertext')
        if not ciphertext:
            print('No stored ciphertext in session file')
            return
    steps = session['steps']
    print('Decrypting using stored algorithm order (in reverse)...')
    current = ciphertext
    for step in reversed(steps):
        algo = step['algo']
        params = step['params']
        try:
            current = apply_decrypt(algo, params, current)
        except Exception as e:
            print(f'Error decrypting with {algo}:', e)
            return
        print(f'After {algo} -> preview: {current[:200]}')
    print('Decryption complete. Recovered plaintext:')
    print(current)

# ----------------------------- Main -----------------------------

def main():
    print('Hybrid Dynamic Cipher — interactive chaining tool')
    while True:
        mode = input("Choose mode: (E)ncrypt / (D)ecrypt / (Q)uit: ").strip().lower()
        if mode == 'e' or mode == 'encrypt':
            encrypt_flow()
        elif mode == 'd' or mode == 'decrypt':
            decrypt_flow()
        elif mode == 'q' or mode == 'quit':
            print('Goodbye')
            break
        else:
            print('Unknown option')

if __name__ == '__main__':
    main()
