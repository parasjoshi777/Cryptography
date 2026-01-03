import numpy as np

# ------------------ Hill Cipher (2x2) ------------------

def hill_encrypt(text, key_matrix):
    text = text.upper().replace(" ", "")
    if len(text) % 2 != 0:
        text += "X"  # padding

    result = ""
    for i in range(0, len(text), 2):
        pair = np.array([[ord(text[i]) - 65], [ord(text[i+1]) - 65]])
        res = np.dot(key_matrix, pair) % 26
        result += chr(res[0][0] + 65) + chr(res[1][0] + 65)

    return result

def mod_inverse(a, m):
    """Return modular inverse of a mod m, if exists."""
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return None

def hill_decrypt(cipher, key_matrix):
    det = int(np.round(np.linalg.det(key_matrix))) % 26
    det_inv = mod_inverse(det, 26)

    if det_inv is None:
        return "Error: Key matrix not invertible modulo 26."

    # Compute adjoint matrix
    adj = np.round(det * np.linalg.inv(key_matrix)).astype(int) % 26
    inv_mat_
