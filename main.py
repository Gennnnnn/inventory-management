import subprocess
import time
import customtkinter as ctk

from InventoryManagement import InventoryManagement

def start_firebase_sync():
    """Start firebase_config.py as a separate process"""
    return subprocess.Popen(["python", "firebase_config.py"])

if __name__ == "__main__":
    try:
        # Start Firebase sync before launching the GUI
        firebase_process = start_firebase_sync()
        time.sleep(2)  # Give Firebase time to initialize

        # Run the GUI application
        root = ctk.CTk()
        app = InventoryManagement(root)  # Create an instance of the GUI class

        # Set the GUI update callback
        from firebase_config import set_gui_update_callback
        set_gui_update_callback(app.refresh_inventory_from_firebase)

        
        root.mainloop()  # Run the application
    finally:
        # Terminate Firebase sync process when GUI closes
        firebase_process.wait()
        print("🚀 Firebase process terminated")