import numpy as np
import math

# Rail Fence Cipher
def rail_fence_encrypt(text, rails):
    fence = [['\n' for _ in range(len(text))] for _ in range(rails)]
    dir_down, row, col = False, 0, 0

    for char in text:
        fence[row][col] = char
        col += 1
        if row == 0 or row == rails - 1:
            dir_down = not dir_down
        row += 1 if dir_down else -1

    return "".join(char for row in fence for char in row if char != '\n')

def rail_fence_decrypt(cipher, rails):
    fence = [['\n' for _ in range(len(cipher))] for _ in range(rails)]
    dir_down, row, col = None, 0, 0

    # Mark positions
    for i in range(len(cipher)):
        if row == 0:
            dir_down = True
        if row == rails - 1:
            dir_down = False
        fence[row][col] = '*'
        col += 1
        row += 1 if dir_down else -1

    # Fill fence
    index = 0
    for i in range(rails):
        for j in range(len(cipher)):
            if fence[i][j] == '*' and index < len(cipher):
                fence[i][j] = cipher[index]
                index += 1

    # Read result
    result, row, col = "", 0, 0
    for i in range(len(cipher)):
        if row == 0:
            dir_down = True
        if row == rails - 1:
            dir_down = False
        result += fence[row][col]
        col += 1
        row += 1 if dir_down else -1

    return result
