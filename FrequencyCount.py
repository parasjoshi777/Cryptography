text = input("Enter the text:")
freq = {}
text = text.lower()
for char in text:
    if char.isalpha():
        if char in freq:
            freq[char]+= 1
        else:
            freq[char]= 1
    
print("\n Frequency count:")
for ch in freq:
    print(ch,"=", freq[ch])
    