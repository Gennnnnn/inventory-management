import firebase_admin
import json
import os
import threading
import time

from tkinter import TclError
from firebase_admin import credentials, db

# Load firebase credentials
try:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://inventory-management-349a9-default-rtdb.firebaseio.com/"
    })
    print("✅ Firebase connected successfully")
except Exception as e:
    print(f"❌ Firebase connection failed: {e}")

# Create database reference
db_ref = db.reference("inventory")
amounts_ref = db.reference("amounts")
history_ref = db.reference("history")

# Define JSON file paths
inventory_path = os.path.join(os.getcwd(), "inventory", "inventory.json")
amounts_path = os.path.join(os.getcwd(), "inventory", "amounts.json")
history_path = os.path.join(os.getcwd(), "inventory", "history.json")

gui_update_callback = None  # Global variable to store the callback function

# Set the callback from the GUI
def set_gui_update_callback(callback):
    global gui_update_callback
    gui_update_callback = callback


def add_or_update_item(item_name, price, quantity, image):
    """Add a new item or update an existing one in Firebase"""
    item_ref = db_ref.child(item_name)
    item_ref.set({
        "name": item_name,
        "price": price,
        "quantity": quantity,
        "image": image
    })
    sync_inventory_from_firebase()
    print(f"✅ Item '{item_name}' addded/updated successfully")


def get_inventory():
    """Retrieve all inventory items from Firebase"""
    inventory = db_ref.get()
    if inventory:
        print("📦 Inventory Retrieved:")
        for item, data in inventory.items():
            print(f"{item}: {data}")
        return inventory
    else:
        print("⚠️ No inventory data found")
        return {}


def delete_item(item_name):
    """Delete an item from Firebase"""
    item_ref = db_ref.child(item_name)
    item_ref.delete()
    sync_inventory_from_firebase()
    print(f"❌ Item '{item_name}' deleted successfully")


def sync_inventory_from_firebase():
    """Fetch inventory data from Firebase and save it locally"""
    inventory_data = db_ref.get()   # Get inventory from Firebase

    if inventory_data:
        with open(inventory_path, "w") as file:
            json.dump(inventory_data, file, indent=4)
        print("✅ Synced inventory.json to Firebase")
    else:
        print("⚠️ No inventory data found in Firebase")


def sync_amounts_to_firebase():
    """Fetch amounts data from Firebase and save it locally"""
    # Create file if not existing
    if not os.path.exists(amounts_path):
        with open(amounts_path, "w") as file:
            json.dump({"total": 0, "entries": []}, file)
    
    with open(amounts_path, "r") as file:
        amounts_data = json.load(file)
    
    amounts_ref.set(amounts_data)
    print("✅ Synced amounts.json to Firebase")


def sync_history_to_firebase():
    """Fetch history data from Firebase and save it locally"""
    # Create file if not existing
    if not os.path.exists(history_path):
        with open(history_path, "w") as file:
            json.dump([], file)

    with open(history_path, "r") as file:
        history_data = json.load(file)

    history_ref.set(history_data if history_data else ["No history yet"])
    print("✅ Synced history.json to Firebase")


def poll_firebase_for_changes():
    """Poll Firebase every few seconds for updates"""
    while True:
        try:
            # Sync all data from Firebase
            sync_inventory_from_firebase()
            sync_amounts_to_firebase()
            sync_history_to_firebase()
            print("🔄 Polled and updated from Firebase")

            # Trigger GUI update safely
            safe_gui_update()  # Call the function to safely update the GUI
            time.sleep(3)
        except Exception as e:
            print(f"⚠️ Error while polling Firebase: {e}")


def safe_gui_update():
    if gui_update_callback and hasattr(gui_update_callback, 'winfo_exists') and gui_update_callback.winfo_exists():
        try:
            gui_update_callback()  # Perform the update safely
        except TclError as e:
            print(f"🚨 GUI update failed: {e}")
    else:
        print("⚠️ GUI update skipped - widget no longer exists.")


# Start the polling in a separate thread
threading.Thread(target=poll_firebase_for_changes, daemon=True).start()
print("🔄 Started polling for database updates...")
