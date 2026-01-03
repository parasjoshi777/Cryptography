def mod_inverse_num(x, m):
    for a in range(1, m):
        if (x * a) % m == 1:
            return a
    return None

def mod_inverse_matrix_2x2(a, b, c, d, m=26):
    det = (a*d - b*c) % m
    det_inv = mod_inverse_num(det, m)
    if det_inv is None:
        return None
    
    return [[( d*det_inv) % m, (-b*det_inv) % m],
            [(-c*det_inv) % m, ( a*det_inv) % m]]

print("Enter 2x2 matrix:")
a = int(input("Enter a (top-left): "))
b = int(input("Enter b (top-right): "))
c = int(input("Enter c (bottom-left): "))
d = int(input("Enter d (bottom-right): "))

result = mod_inverse_matrix_2x2(a, b, c, d)

if result:
    print("Inverse matrix mod 26 is:")
    for row in result:
        print(row)
else:
    print("Matrix is not invertible modulo 26")