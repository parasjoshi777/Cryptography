import os

books_file = "books.txt"
sales_file = "sales.txt"

def load_data():
    books = []
    sales = []

    if os.path.exists(books_file):
        with open(books_file, "r") as f:
            for line in f:
                data = line.strip().split(",")
                if len(data) == 3:
                    books.append([data[0], float(data[1]), int(data[2])])

    if os.path.exists(sales_file):
        with open(sales_file, "r") as f:
            for line in f:
                data = line.strip().split(",")
                if len(data) == 3:
                    sales.append([data[0], int(data[1]), float(data[2])])

    return books, sales

def save_data(books, sales):
    with open(books_file, "w") as f:
        for b in books:
            f.write(f"{b[0]},{b[1]},{b[2]}\n")

    with open(sales_file, "w") as f:
        for s in sales:
            f.write(f"{s[0]},{s[1]},{s[2]}\n")

def add_book(books):
    title = input("Enter book title: ")
    price = float(input("Enter price: "))
    quantity = int(input("Enter quantity: "))
    books.append([title, price, quantity])
    print(f"\n✅ Book '{title}' added successfully!\n")

def sell_book(books, sales):
    title = input("Enter book title to sell: ")
    for book in books:
        if book[0].lower() == title.lower():
            qty = int(input("Enter quantity to sell: "))
            if qty <= book[2]:
                book[2] -= qty
                amount = qty * book[1]
                sales.append([book[0], qty, amount])
                print(f"\n✅ Sold {qty} copies of '{book[0]}'.\n")
            else:
                print("\n❌ Not enough stock available.\n")
            return
    print("\n❌ Book not found in stock.\n")

def view_report(books, sales):
    print("\n--- STOCK REPORT ---")
    if not books:
        print("No books in stock.")
    else:
        for b in books:
            print(f"{b[0]} | Price: ₹{b[1]} | Stock: {b[2]}")

    print("\n--- SALES REPORT ---")
    if not sales:
        print("No sales yet.")
    else:
        total = 0
        for s in sales:
            print(f"{s[0]} | Qty: {s[1]} | Amount: ₹{s[2]}")
            total += s[2]
        print(f"Total Revenue: ₹{total}\n")

def main():
    books, sales = load_data()

    while True:
        print("📚 BOOKSTORE MENU")
        print("1. Add Book")
        print("2. Sell Book")
        print("3. View Report")
        print("4. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            add_book(books)
        elif choice == "2":
            sell_book(books, sales)
        elif choice == "3":
            view_report(books, sales)
        elif choice == "4":
            save_data(books, sales)
            print("Exiting... Data saved. Goodbye!")
            break
        else:
            print("❌ Invalid choice, try again.\n")

main()
