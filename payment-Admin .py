import time
import board
import busio
import firebase_admin
from firebase_admin import credentials, db
from adafruit_pn532.i2c import PN532_I2C

# Initialize Firebase with Realtime Database
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://smart-cart-d2954-default-rtdb.firebaseio.com/'
})

def read_nfc():
    print("Please tap the card...")
    i2c = busio.I2C(board.SCL, board.SDA)
    pn532 = PN532_I2C(i2c, debug=False)
    ic, ver, rev, support = pn532.firmware_version
    print("Found PN532 with firmware version: {0}.{1}".format(ver, rev))
    pn532.SAM_configuration()

    while True:
        uid = pn532.read_passive_target(timeout=0.5)
        if uid is not None:
            print("NFC tag detected!")
            print("UID:", [hex(i) for i in uid])
            return bytes(uid)
        else:
            print(".", end="")
            time.sleep(1)

def check_balance(card_id):
    card_id_str = card_id.hex()
    balance_ref = db.reference('balances/' + card_id_str)
    balance = balance_ref.get()
    if balance is not None:
        print("Balance:", balance)
    else:
        print("Card not found or balance not available.")

def add_money(card_id):
    amount = float(input("Enter the amount to be added: "))
    card_id_str = card_id.hex()
    balance_ref = db.reference('balances/' + card_id_str)
    current_balance = balance_ref.get()
    new_balance = current_balance + amount if current_balance is not None else amount
    balance_ref.set(new_balance)
    print("Amount added successfully.")

def main():
    while True:
        print("\nOptions:")
        print("1. Check Balance")
        print("2. Add Money")
        print("3. Exit")

        choice = input("Enter your choice (1/2/3): ")

        if choice == "1":
            card_id = read_nfc()
            check_balance(card_id)
        elif choice == "2":
            card_id = read_nfc()
            add_money(card_id)
        elif choice == "3":
            print("Exiting the program. Goodbye!")
            break
        else:
            print("Invalid choice. Please choose again.")

if __name__ == "__main__":
    main()
