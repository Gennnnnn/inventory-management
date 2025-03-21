import tkinter as tk
import json
import os

class InventoryManagement:
    def __init__(self, root):
        """Initialize the inventory management application"""
        self.root = root
        self.root.title("Furniture Inventory Management")
        self.root.configure(bg="#efebe2")
        self.root.attributes("-fullscreen", True)

        # Define color palette
        self.BG_COLOR = "#efebe2"
        self.BTN_COLOR = "#ce2a22"
        self.TEXT_COLOR = "#242222"

        # JSON File Path
        self.inventory_dir = r"C:\inventory"
        self.json_file = os.path.join(self.inventory_dir, "inventory.json")

        # Ensure directory exists
        os.makedirs(self.inventory_dir, exist_ok=True)

        # Load or initialize inventory
        self.inventory = self.load_inventory()
      
        # Dictionary to store item labels for updating
        self.item_labels = {}

        # Build UI
        self.create_ui()
        
    def load_inventory(self):
        """Load inventory from JSON file or create a default one if it doesn't exist"""
        if os.path.exists(self.json_file):
            with open(self.json_file, "r") as file:
                return json.load(file)
        else:
            default_inventory = {
                "Hammer": 10,
                "Screwdriver": 15,
                "Saw": 7,
                "Wood Planks": 20,
                "Nails (Box)": 50,
                "Varnish Can": 8
            }
            self.save_inventory(default_inventory)
            return default_inventory
    
    def save_inventory(self, data=None):
        """Save inventory data to JSON file"""
        if data is None:
            data = self.inventory
        with open(self.json_file, "w") as file:
            json.dump(data, file, indent=4)

    def create_ui(self):
        """Create the user interface"""
        # Title Label
        title_label = tk.Label(self.root, text="Inventory Management", font=("Arial", 24, "bold"),
                            bg=self.BG_COLOR, fg=self.TEXT_COLOR)
        title_label.pack(pady=20)

        # Create a frame for inventory items
        frame = tk.Frame(self.root, bg=self.BG_COLOR)
        frame.pack(pady=10)

        # Generate UI for inventory items
        for item, qty in self.inventory.items():
            item_frame = tk.Frame(frame, bg=self.BG_COLOR)
            item_frame.pack(fill="x", padx=40, pady=5)

            item_label = tk.Label(item_frame, text=f"{item}: {qty}", font=("Arial", 18), bg=self.BG_COLOR, fg=self.TEXT_COLOR)
            item_label.pack(side="left", padx=10)

            self.item_labels[item] = item_label

            btn_minus = tk.Button(item_frame, text="-", font=("Arial", 16, "bold"), bg=self.BTN_COLOR, fg="#fff",
                                command=lambda i=item: self.update_quantity(i, -1), width=5, height=2)
            btn_minus.pack(side="right", padx=5)

            btn_plus = tk.Button(item_frame, text="+", font=("Arial", 16, "bold"), bg=self.BTN_COLOR, fg="#fff",
                                command=lambda i=item: self.update_quantity(i, 1), width=5, height=2)
            btn_plus.pack(side="right", padx=5)

        # Exit button
        exit_btn = tk.Button(self.root, text="Exit", font=("Arial", 16, "bold"), bg="#424242", fg="#fff",
                            command=self.root.destroy, width=10, height=2)
        exit_btn.pack(pady=20)

        # Export button
        export_btn = tk.Button(self.root, text="Export to TXT", font=("Arial", 16, "bold"),
                               bg="#424242", fg="#fff", command=self.export_to_txt,
                               width=15, height=2)
        export_btn.pack(pady=10)

    def update_quantity(self, item, change):
        """Update the inventory quantity when + or - button is pressed"""
        if item in self.inventory:
            self.inventory[item] = max(0, self.inventory[item] + change)
            self.item_labels[item].config(text=f"{item}: {self.inventory[item]}")
            self.save_inventory()
    
    def export_to_txt(self):
        """Export inventory data to a TXT file formatted as Key = Value"""
        txt_file = os.path.join(self.inventory_dir, "inventory.txt")
        with open(txt_file, "w") as file:
            for item, qty in self.inventory.items():
                file.write(f"{item} = {qty}\n")

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryManagement(root)
    root.mainloop()