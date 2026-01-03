
def caesar_encrypt(text, key):
    result = ""
    for char in text:
        if char.isalpha():
            shift = 65 if char.isupper() else 97
            result += chr((ord(char) - shift + key) % 26 + shift)
        else:
            result += char
    return result


def caesar_decrypt(text, key):
    return caesar_encrypt(text, -key)


def main():
    while True:
        print("\n--- Caesar Cipher Menu ---")
        print("1. Encrypt")
        print("2. Decrypt")
        print("3. Exit")

        choice = input("Enter choice: ")

        if choice == '1':
            text = input("Enter text: ")
            key = int(input("Enter key (number): "))
            encrypted = caesar_encrypt(text, key)
            print("Encrypted text:", encrypted)

        elif choice == '2':
            text = input("Enter text: ")
            key = int(input("Enter key (number): "))
            decrypted = caesar_decrypt(text, key)
            print("Decrypted text:", decrypted)

        elif choice == '3':
            print("Goodbye!")
            break

        else:
            print("Invalid choice! Try again.")


if __name__ == "__main__":
    main()
