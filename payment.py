import time
import board
import busio
import firebase_admin
from firebase_admin import credentials, db
from adafruit_pn532.i2c import PN532_I2C
import pyttsx3

# Initialize Firebase with Realtime Database
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://smart-cart-d2954-default-rtdb.firebaseio.com/'
})

# Initialize pyttsx3 engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Adjust speed (words per minute)
engine.setProperty('voice', 'english+f4')  # Adjust accent

def read_nfc():
    engine.say("Please tap the card...")
    engine.runAndWait()

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
        #engine.say("Card balance: " + str(balance))
        #engine.runAndWait()
        print("Balance:", balance)
        return balance
    else:
        engine.say("Card not found or balance not available.")
        engine.runAndWait()
        print("Card not found or balance not available.")
        return None

def deduct_amount(card_id, amount):
    card_id_str = card_id.hex()
    balance_ref = db.reference('balances/' + card_id_str)
    current_balance = balance_ref.get()
    if current_balance is not None and current_balance >= amount:
        new_balance = current_balance - amount
        balance_ref.set(new_balance)
        engine.say("Amount deducted successfully. New balance: " + str(new_balance),"Thank You")
        engine.say("Thank You")
        engine.runAndWait()
        print("Amount deducted successfully. New balance:", new_balance ,"Thank You")
        return True
    else:
        engine.say("Insufficient balance.")
        engine.runAndWait()
        print("Insufficient balance.")
        return False

def monitor_database():
    ref = db.reference('/')
    payment_ref = ref.child('cardPayment')

    while True:
        payment_status = payment_ref.child('payment').get()
        if payment_status == "true":
            amount_str = payment_ref.child('amount').get()
            if amount_str:
                amount = float(amount_str)  # Convert amount to float
                card_id = read_nfc()
                balance = check_balance(card_id)
                if balance is not None and balance >= amount:
                    if deduct_amount(card_id, amount):
                        # Payment successful
                        payment_ref.update({'payment': True})  # Update to boolean True
                        ref.update({'paymentReceived': True})  # Update to boolean True
                    else:
                        engine.say("Payment failed.")
                        engine.runAndWait()
                        print("Payment failed.")
                else:
                    engine.say("Payment failed due to insufficient balance.")
                    engine.runAndWait()
                    print("Payment failed due to insufficient balance.")
                    payment_ref.update({'payment': False})  # Update to boolean False
                    payment_ref.update({'lowBalance': True})  # Update to boolean True
            else:
                print("No amount specified.")

        time.sleep(5)  # Check every 5 seconds

def main():
    monitor_database()

if __name__ == "__main__":
    main()
