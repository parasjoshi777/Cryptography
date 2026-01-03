import math

# ---------- Helper Functions ----------

def transpose(text, key):
    n = len(key)
    matrix = [list(text[i:i+n]) for i in range(0, len(text), n)]

    # Pad last row with X if short
    for row in matrix:
        if len(row) < n:
            row += ['X'] * (n - len(row))

    # Sort columns by key
    ordered = sorted(list(enumerate(key)), key=lambda x: x[1])

    ciphertext = ""
    for idx, _ in ordered:
        for row in matrix:
            ciphertext += row[idx]

    return ciphertext


def transpose_decrypt_with_rows(cipher, key, rows):
    n = len(key)
    mat = [[''] * n for _ in range(rows)]

    ordered = sorted(list(enumerate(key)), key=lambda x: x[1])

    idx = 0
    for col_pos, _ in ordered:
        for r in range(rows):
            mat[r][col_pos] = cipher[idx]
            idx += 1

    return "".join("".join(row) for row in mat)


# ---------- Main Encryption / Decryption ----------

def double_transposition_encrypt(text, row_key, col_key):
    return transpose(transpose(text, row_key), col_key)


def double_transposition_decrypt(cipher, row_key, col_key, orig_len=None):
    try:
        # Step 1: reverse column transposition
        n2 = len(col_key)
        r2 = len(cipher) // n2
        stepA_padded = transpose_decrypt_with_rows(cipher, col_key, r2)

        # Step 2: reverse row transposition
        n1 = len(row_key)

        if orig_len is not None:
            r1 = math.ceil(orig_len / n1)
            stepA_effective = stepA_padded[: r1 * n1]
            plaintext_padded = transpose_decrypt_with_rows(stepA_effective, row_key, r1)
            return plaintext_padded[:orig_len]
        else:
            r1 = len(stepA_padded) // n1
            plaintext_padded = transpose_decrypt_with_rows(stepA_padded, row_key, r1)
            return plaintext_padded.rstrip('X')

    except Exception as e:
        return f"Decryption error: {e}"


# ---------- Demo Menu (Optional) ----------

def main():
    print("\nDouble Transposition Cipher")
    text = input("Enter text: ")
    row_key = input("Enter row key (e.g., 3142): ")
    col_key = input("Enter col key (e.g., 2413): ")

    encrypted = double_transposition_encrypt(text, row_key, col_key)
    print("\nEncrypted:", encrypted)

    decrypted = double_transposition_decrypt(encrypted, row_key, col_key, orig_len=len(text))
    print("Decrypted:", decrypted)


if __name__ == "__main__":
    main()
