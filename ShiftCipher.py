def decrypt_shift_cipher(cipher_text, shift):
    result = ""
    cipher_text = cipher_text.lower()

    for char in cipher_text:
        if char.isalpha():
            
            result += chr((ord(char) - ord('a') - shift) % 26 + ord('a'))
        else:
            result += char  
    return result

cipher_text = input("Enter the encrypted text: ")
shift = int(input("Enter the shift key: "))

plain_text = decrypt_shift_cipher(cipher_text, shift)
print("Decrypted text:", plain_text)