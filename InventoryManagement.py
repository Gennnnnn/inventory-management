import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import json
import os
import tkinter.messagebox as msgbox
import subprocess
import datetime

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
        # frame = tk.Frame(self.root, bg=self.BG_COLOR)
        # frame.pack(pady=10)

        # Generate UI for inventory items
        # for item, qty in self.inventory.items():
        #     item_frame = tk.Frame(frame, bg=self.BG_COLOR)
        #     item_frame.pack(fill="x", padx=40, pady=5)

        #     item_label = tk.Label(item_frame, text=f"{item}: {qty}", font=("Arial", 18), bg=self.BG_COLOR, fg=self.TEXT_COLOR)
        #     item_label.pack(side="left", padx=10)

        #     self.item_labels[item] = item_label

        #     btn_minus = tk.Button(item_frame, text="-", font=("Arial", 16, "bold"), bg=self.BTN_COLOR, fg="#fff",
        #                         command=lambda i=item: self.update_quantity(i, -1), width=5, height=2)
        #     btn_minus.pack(side="right", padx=5)

        #     btn_plus = tk.Button(item_frame, text="+", font=("Arial", 16, "bold"), bg=self.BTN_COLOR, fg="#fff",
        #                         command=lambda i=item: self.update_quantity(i, 1), width=5, height=2)
        #     btn_plus.pack(side="right", padx=5)

        # Create the scrollable inventory area
        self.create_scrollable_inventory()
        self.populate_inventory()

        # Create a frame for the buttons at the bottom right
        button_frame = tk.Frame(self.root, bg=self.BG_COLOR)
        button_frame.pack(side="bottom", anchor="se", padx=20, pady=20)

        # Exit button
        exit_btn = tk.Button(button_frame, text="Exit", font=("Arial", 16, "bold"),
                            bg="#ce2a22", fg="#fff", command=self.confirm_exit,
                            width=10, height=2)
        exit_btn.pack(side="right", padx=10, pady=10)

        # Export button
        export_btn = tk.Button(button_frame, text="Export to TXT", font=("Arial", 16, "bold"),
                               bg="#424242", fg="#fff", command=self.export_to_txt,
                               width=15, height=2)
        export_btn.pack(side="right", padx=10, pady=10)

    def confirm_exit(self):
        """Ask for confirmation before exiting the application"""
        if msgbox.askyesno("Exit Confirmation", "Are you sure you want to exit?"):
            self.root.destroy()
        
    def update_quantity(self, item, change):
        """Update the inventory quantity when + or - button is pressed"""
        if item in self.inventory:
            self.inventory[item] = max(0, self.inventory[item] + change)

            # Properly update the item label to show the quantity
            if item in self.item_labels:
                self.item_labels[item].config(text=f"{item}\nQty: {self.inventory[item]}")
            
            self.save_inventory()
    
    def export_to_txt(self):
        """Export inventory data to a TXT file with date/time, show a dialog, and open the folder"""
        now = datetime.datetime.now().strftime("%m-%d-%Y | %H:%M:%S")
        date_only = datetime.datetime.now().strftime("%m-%d-%Y")
        txt_file = os.path.join(self.inventory_dir, f"inventory_{date_only}.txt")

        # Write inventory data to the TXT file
        with open(txt_file, "w") as file:
            file.write(f"Exported on: {now.replace('_', ' ')}\n\n")
            for item, qty in self.inventory.items():
                file.write(f"{item} = {qty}\n")
        
        # Show dialog box after exporting
        msgbox.showinfo("Export Successful", f"Inventory exported to:\n{txt_file}")

        # Open the folder containing the exported file
        subprocess.Popen(f'explorer /select, "{txt_file}"')
    
    def create_scrollable_inventory(self):
        """Create a scrollable inventory grid with images, names, and buttons"""

        # Create a frame with a canvas and scrollbar
        container = tk.Frame(self.root, bg=self.BG_COLOR)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, bg=self.BG_COLOR, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)

        # Create a frame inside the canvas
        scroll_frame = tk.Frame(canvas, bg=self.BG_COLOR)
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Attach frame to canvas
        window = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.scroll_canvas = canvas
        self.scroll_frame = scroll_frame
        
    def populate_inventory(self):
        """Populate the inventory grid inside the scrollable frame"""
        columns = 2
        row, col = 0, 0

        # Create a wrapper frame to center the grid
        wrapper_frame = tk.Frame(self.scroll_frame, bg=self.BG_COLOR)
        wrapper_frame.pack(pady=20, fill="x", expand=True)

        # Center the grid using a parent frame
        center_frame = tk.Frame(wrapper_frame, bg=self.BG_COLOR)
        center_frame.pack(padx=110)

        # Configure column weights for even spacing
        for i in range(columns):
            center_frame.grid_columnconfigure(i, weight=1)

        for item, qty in self.inventory.items():
            item_frame = tk.Frame(center_frame, bg=self.BG_COLOR, padx=10, pady=10,
                                  highlightbackground="#424242", highlightthickness=2, bd=2, relief="solid")
            item_frame.grid(row=row, column=col, padx=40, pady=20, sticky="nsew")

            # Load Image
            image_path = os.path.join("assets", f"{item.lower().replace(' ', '_')}.jpg")
            if os.path.exists(image_path):
                img = Image.open(image_path).resize((300, 300))
                img = ImageTk.PhotoImage(img)
            else:
                img = tk.PhotoImage(width=100, height=100)

            item_img = tk.Label(item_frame, image=img, bg=self.BG_COLOR)
            item_img.image = img
            item_img.pack()

            item_label = tk.Label(item_frame, text=f"{item}\nQty: {qty}", font=("Arial", 30), bg=self.BG_COLOR)
            item_label.pack()

            btn_frame = tk.Frame(item_frame, bg=self.BG_COLOR)
            btn_frame.pack()

            btn_minus = tk.Button(btn_frame, text="-", font=("Arial", 20), bg=self.BTN_COLOR, fg="#fff",
                                  command=lambda i=item: self.update_quantity(i, -1),
                                  width=3, height=1, borderwidth=2, relief="ridge")
            btn_minus.pack(side="left", padx=10, pady=5)

            btn_plus = tk.Button(btn_frame, text="+", font=("Arial", 20), bg=self.BTN_COLOR, fg="#fff",
                                 command=lambda i=item: self.update_quantity(i, 1),
                                 width=3, height=1, borderwidth=2, relief="ridge")
            btn_plus.pack(side="left", padx=10, pady=5)

            self.item_labels[item] = item_label

            col += 1
            if col >= columns:
                col = 0
                row += 1

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryManagement(root)
    root.mainloop()