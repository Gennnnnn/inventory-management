import firebase_admin
from firebase_admin import credentials, db
import threading
import time

# Load firebase credentials
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://inventory-management-349a9-default-rtdb.firebaseio.com/"
})

print("✅ Firebase connected successfully")

# Create database reference
db_ref = db.reference("inventory")

# Function to check for real-time updates
def listen_for_updates():
    print("🔄 Listening for database updates...")

    last_data = db_ref.get() # Get initial data

    while True:
        time.sleep(2) # Poll every 2 seconds
        new_data = db_ref.get()

        if new_data != last_data:
            print("⚡ Data Changed:", new_data)
            last_data = new_data # Update the last known data
        
# Run the listener in a separate thread
listener_thread = threading.Thread(target=listen_for_updates, daemon=True)
listener_thread.start()