import customtkinter as ctk
import json
import os
import datetime
import openpyxl
import shutil

from CTkMessagebox import CTkMessagebox
from PIL import Image, ImageDraw, ImageOps
from pathlib import Path
from customtkinter import filedialog


class InventoryManagement:
    """Manages inventory, tracks purchases, and handles UI interactions"""

    def refresh_inventory_from_firebase(self):
        """Refresh the inventory from the local JSON file after a Firebase update"""
        self.inventory = self.load_inventory()
        self.refresh_inventory_display()
        print("🔄 Inventory updated from Firebase")
    

    def __init__(self, root):
        """Initialize the inventory management application"""
        self.root = root
        self.root.title("Furniture Inventory Management")
        self.root.attributes("-fullscreen", True)

        # Apply Modern Theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Define color palette
        self.colors = {
            "bg": "#2b2b2b",    # Background Color
            "btn": "#1f6aa5",   # Button Color
            "text": "#ffffff"   # Text Color
        }

        # Define inventory directory (ensure it exists)
        self.inventory_dir = Path.cwd() / "inventory"
        self.inventory_dir.mkdir(exist_ok=True) # Creates directory if missing

        # Define file paths in a dictionary (easier management)
        self.file_paths = {
            "inventory": self.inventory_dir / "inventory.json",
            "amounts": self.inventory_dir / "amounts.json",
            "history": self.inventory_dir / "history.json",
            "export": self.inventory_dir
        }

        self.inventory = self.load_inventory()  # Load or initialize inventory
        self.item_labels = {}   # Dictionary to store item labels for updating
        self.quantity_vars = {} # Quantity for each items
        self.create_ui()    # Build UI
            
                
    def load_inventory(self):
        """Load inventory from JSON file or create a default one if it doesn't exist"""
        json_path = self.file_paths["inventory"]

        try:
            if json_path.exists():
                with json_path.open("r") as file:
                    inventory = json.load(file)

                    # Ensure the inventory is always a dictionary
                    if not isinstance(inventory, dict):
                        raise ValueError("Invalid inventory format")
                    
                    # Ensure all items have a quantity field
                    for item, data in inventory.items():
                        if isinstance(data, int):   # Convert old format (integer) to new dict format
                            inventory[item] = {"price": 100, "quantity": data} 
                        # elif isinstance(data, dict) and "quantity" not in data:
                        elif isinstance(data, dict):
                            inventory[item]["quantity"] = data.get("quantity", 0)
                            inventory[item]["price"] = data.get("price", 100)
            else:
                inventory = {}

        except (json.JSONDecodeError, ValueError):
            CTkMessagebox(
                title="Error", 
                message="Inventory file is corrupted or invalid. Resetting inventory", 
                icon="cancel")
            inventory = {}

        # Reset all quantities to 0 on startup
        for item in inventory.values():
            item["quantity"] = 0

        self.save_inventory(inventory)  # Save the updated inventory with reset quantities

        return inventory


    def save_inventory(self, data=None):
        """Save inventory data to JSON file safely"""
        if data is None:
            data = self.inventory
        
        json_path = self.file_paths["inventory"]

        try:
            json_path.parent.mkdir(parents=True, exist_ok=True) # Ensure directory exists before saving

            # Write to file safely with utf-8 encoding
            with json_path.open("w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)

        except (OSError, IOError) as e:
            CTkMessagebox(
                title="Error", 
                message=f"Failed to save inventory: {e}", 
                icon="cancel")


    def create_ui(self):
        """Create the user interface"""
        # Title Label
        title_label = ctk.CTkLabel(self.root, text="Inventory Management", 
                                   font=("Arial", 24, "bold"), text_color=self.colors["text"])
        title_label.pack(pady=20)

        saved_total = self.load_amount_data().get("total", 0)   # Load the saved total from JSON
        
        # Total Amount Label (Top Left)
        self.total_label = ctk.CTkLabel(self.root, text=f"Total: ₱ {saved_total}", 
                                        font=("Arial", 18, "bold"))
        self.total_label.place(x=20, y=20)

        self.create_button("Reset Total", self.reset_total, x=200, y=15, width=140, height=40)  # Reset Button

        # Create the scrollable inventory area
        self.create_scrollable_inventory()
        self.populate_inventory()

        # Bottom-right button frame
        button_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        button_frame.pack(side="bottom", anchor="se", padx=20, pady=20)

        # Add Buttons
        btn_history = ctk.CTkButton(self.root, text="View History", font=("Arial", 16, "bold"), fg_color=self.colors["btn"],
                                command=self.open_history_window,
                                width=140, height=50)
        btn_history.pack(padx=5, pady=5)

        self.create_button("Exit", self.confirm_exit, frame=button_frame, width=140, height=50)
        self.create_button("Export History", self.export_history_to_excel, frame=button_frame, width=180, height=50)

        add_button = ctk.CTkButton(master=self.root, font=("Arial", 18), text="➕ Add", width=140, height=50, command=self.create_add_window)
        add_button.place(x=1430, y=10)   

        edit_button = ctk.CTkButton(master=self.root, font=("Arial", 18), text="✏️ Edit", width=140, height=50, command=self.create_edit_window)
        edit_button.place(x=1590, y=10)   

        remove_button = ctk.CTkButton(master=self.root, font=("Arial", 18), text="❌ Remove", width=140, height=50, command=self.create_remove_window)
        remove_button.place(x=1750, y=10)


    def create_add_window(self):
        add_window = ctk.CTkToplevel(self.root)
        add_window.title("Add Equipment")
        add_window.geometry("400x400")
        add_window.attributes("-topmost", True)

        # Center the window dynamically
        add_window.update_idletasks()
        window_width, window_height = 400, 400
        screen_width = add_window.winfo_screenwidth()
        screen_height = add_window.winfo_screenheight()
        x_position = (screen_width // 2) - (window_width // 2)
        y_position = (screen_height // 2) - (window_height // 2)
        add_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        # Name Entry
        name_label = ctk.CTkLabel(add_window, text="Name:", font=("Arial", 16))
        name_label.pack(pady=5)
        name_entry = ctk.CTkEntry(add_window)
        name_entry.pack(pady=(5, 20))

        # Image Upload Button
        image_path = ctk.StringVar()

        def select_image():
            file_path = filedialog.askopenfilename(
                title="Select Image",
                filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")]
            )
            if file_path:
                # Copy the selected image to the assets folder
                destination = f"assets/{file_path.split('/')[-1]}"
                shutil.copy(file_path, destination)
                image_path.set(destination) # Update path to the copied location
                image_label.configure(text=file_path.split("/")[-1])    # Show the file name
        
        image_button = ctk.CTkButton(add_window, text="Upload Image", font=("Arial", 16), command=select_image)
        image_button.pack(pady=(15, 5))

        image_label = ctk.CTkLabel(add_window, text="No file selected", font=("Arial", 14))
        image_label.pack(pady=(5, 15))

        # Price Entry
        price_label =ctk.CTkLabel(add_window, text="Price:", font=("Arial", 16))
        price_label.pack(pady=5)
        price_entry = ctk.CTkEntry(add_window)
        price_entry.pack(pady=5)

        # Save Button
        save_button = ctk.CTkButton(add_window, text="Save", font=("Arial", 18), command=lambda: self.add_equipment(name_entry.get(), image_path.get(), price_entry.get(), add_window))
        save_button.pack(pady=40)

        # Cancel Button
        # cancel_button = ctk.CTkButton(add_window, text="Cancel", font=("Arial", 18))
        # cancel_button.pack(pady=40)
        
        
    def create_edit_window(self):
        edit_window = ctk.CTkToplevel(self.root)
        edit_window.title("Edit Equipment")
        edit_window.geometry("400x420")
        edit_window.attributes("-topmost", True)

        # Center the window dynamically
        edit_window.update_idletasks()
        window_width, window_height = 400, 420
        screen_width = edit_window.winfo_screenwidth()
        screen_height = edit_window.winfo_screenheight()
        x_position = (screen_width // 2) - (window_width // 2)
        y_position = (screen_height // 2) - (window_height // 2)
        edit_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")


        # Dropdown to select equipment
        name_label = ctk.CTkLabel(edit_window, text="Select Equipment:", font=("Arial", 16))
        name_label.pack(pady=5)

        equipment_names = list(self.inventory.keys())
        selected_name = ctk.StringVar(value=equipment_names[0] if equipment_names else "")

        dropdown = ctk.CTkOptionMenu(edit_window, variable=selected_name, values=equipment_names)
        dropdown.pack(pady=5)

        # Prefill Fields with Selected Equipment Data
        image_path = ctk.StringVar()
        new_name_var = ctk.StringVar()
        new_price_var = ctk.StringVar()

        def update_fileds(*args):
            """Updates the input fields based on the selected equipment"""
            selected_item = selected_name.get()
            if selected_item and selected_item in self.inventory:
                data = self.inventory[selected_item]
                new_name_var.set(selected_item)
                new_price_var.set(str(data.get("price", "")))
                image_path.set(data.get("image", ""))

                # Update Image Label
                image_label.configure(text=os.path.basename(image_path.get()) if image_path.get() else "No file selected")

        selected_name.trace_add("write", update_fileds)

        # New Name Entry (Prefilled)
        new_name_label = ctk.CTkLabel(edit_window, text="New Name:", font=("Arial", 16))
        new_name_label.pack(pady=5)
        new_name_entry = ctk.CTkEntry(edit_window, textvariable=new_name_var)
        new_name_entry.pack(pady=(5, 20))

        def select_image():
            file_path = filedialog.askopenfilename(
                title="Select Image",
                filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")]
            )
            if file_path:
                destination = os.path.join("assets", os.path.basename(file_path))

                try:
                    shutil.copy(file_path, destination)  # Copy image to assets

                    image_path.set(destination)  # Store image path
                    image_label.configure(text=os.path.basename(file_path))  # Update UI
                except Exception as e:
                    print(f"Error copying file: {e}")  # Debugging error

                
        image_button = ctk.CTkButton(edit_window, text="Upload Image", font=("Arial", 16), command=select_image)
        image_button.pack(pady=(15, 5))

        image_label = ctk.CTkLabel(edit_window, text="No file selected", font=("Arial", 16))
        image_label.pack(pady=(5, 15))
        
        # New Price Entry
        new_price_label = ctk.CTkLabel(edit_window, text="New Price:", font=("Arial", 16))
        new_price_label.pack(pady=5)
        new_price_entry = ctk.CTkEntry(edit_window, textvariable=new_price_var)
        new_price_entry.pack(pady=5)

        # Save Changes
        def save_changes():
            name = selected_name.get()
            new_name = new_name_var.get().strip()
            new_price = new_price_var.get().strip()
            new_image = image_path.get()

            if not new_name:
                CTkMessagebox(title="Error", message="Name cannot be empty!", icon="cancel")
                return

            try:
                new_price = float(new_price)
            except ValueError:
                CTkMessagebox(title="Error", message="Invalid price! Enter a valid number (e.g., 10.5).", icon="cancel")
                return

            if name:
                if new_name and new_name != name:
                    self.inventory[new_name] = self.inventory.pop(name)

                self.inventory[new_name]["price"] = new_price

                if new_image:
                    self.inventory[new_name]["image"] = new_image
                else:
                    # Retain old image if not changed
                    self.inventory[new_name]["image"] = self.inventory[new_name].get("image", "")

                self.save_inventory()
                self.refresh_inventory_display()
                edit_window.destroy()
                CTkMessagebox(title="Success", message=f"Equipment {new_name} updated successfully", icon="info")


        save_button = ctk.CTkButton(edit_window, text="Update", font=("Arial", 18), command=save_changes)
        save_button.pack(pady=20)

        # Trigger field update on open
        update_fileds()
    
    def create_remove_window(self):
        remove_window = ctk.CTkToplevel(self.root)
        remove_window.title("Remove Equipment")
        remove_window.geometry("300x300")
        remove_window.attributes("-topmost", True)
        
        # Center the window dynamically
        remove_window.update_idletasks()
        window_width, window_height = 300, 300
        screen_width = remove_window.winfo_screenwidth()
        screen_height = remove_window.winfo_screenheight()
        x_position = (screen_width // 2) - (window_width // 2)
        y_position = (screen_height // 2) - (window_height // 2)
        remove_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        # Dropdown Menu
        equipment_names = list(self.inventory.keys())
        selected_item = ctk.StringVar()
        dropdown = ctk.CTkComboBox(remove_window, values=equipment_names, variable=selected_item)
        dropdown.pack(pady=(100, 20))

        # Remove Button
        remove_button = ctk.CTkButton(remove_window, text="Remove", font=("Arial", 18), command=lambda: self.remove_equipment(selected_item.get(), remove_window))
        remove_button.pack(pady=20)
        
    
    def add_equipment(self, name, image_path, price, window):
        if not name or not image_path or not price.isdigit():
            CTkMessagebox(
                title="Invalid Input",
                message="Please fill all fields correctly!",
                icon="cancel"
            )
            return
        
        new_item = {
            "name": name,
            "image": image_path,
            "price": float(price),
            "quantity": 0
        }
        
        self.inventory[name.lower()] = new_item
        self.save_inventory()
        window.destroy()
        self.refresh_inventory_display()
        CTkMessagebox(
            title="Success",
            message=f"{name} added successfully!",
            icon="info"
        )


    def remove_equipment(self, item_name, remove_window):
        """Safely remove an item from the inventory"""
        # Confirmation Dialog
        confirm = CTkMessagebox(
            title="Confirm",
            message=f"Are you sure you want to remove '{item_name}'?",
            icon="question",
            option_1="Yes",
            option_2="No"
        ).get()
        if confirm != "Yes":
            return

        inventory_keys = {k.lower(): k for k in self.inventory.keys()}  # Map lowercase to original keys
        item_name_lower = item_name.lower()

        if item_name_lower in inventory_keys:
            original_name = inventory_keys[item_name_lower] # Get the actual key from the inventory
            del self.inventory[original_name]   # Remove item
            
            # Save updated inventory
            with open(self.file_paths["inventory"], "w") as file:
                json.dump(self.inventory, file, indent=4)

            self.refresh_inventory_display()
            CTkMessagebox(
                title="Success",
                message=f"{item_name} removed successfully!",
                icon="info"
            )
        else:
            CTkMessagebox(
                title="Error", 
                message=f"'{item_name}' not found in inventory.", 
                icon="cancel"
                )
        remove_window.destroy()
        
            
    def refresh_inventory_display(self):
        """Refresh the inventory display using the scrollable frame"""
        if hasattr(self, "scroll_frame"):
            for widget in self.scroll_frame.winfo_children():
                widget.destroy()
            self.populate_inventory()   # Reload inventory items
   

    def create_button(self, text, command, x=None, y=None, frame=None, width= 140, height=50):
        """Creates a CTkButton with predefined styling"""
        btn = ctk.CTkButton(
            frame or self.root,
            text=text,
            font=("Arial", 16, "bold"),
            fg_color=self.colors["btn"],
            command=command,
            width=width,
            height=height,
            corner_radius=10,
            border_color="white"
        )

        if x is not None and y is not None:
            btn.place(x=x, y=y)
        else:
            btn.pack(side="right", padx=10, pady=10)
        
        return btn
    

    def confirm_exit(self):
        """Ask for confirmation before exiting the application"""
        response = CTkMessagebox(
            title="Exit Confirmation", 
            message="Are you sure you want to exit?", 
            icon="question", 
            option_1="Yes", 
            option_2="No")
        
        if response.get() == "Yes":
            self.root.destroy()
        
        
    def update_quantity(self, item, qty_var, change):
        """Increase or decrease the quantity of an inventory item"""

        try:
            current_qty = int(qty_var.get())    # Ensure it's an integer
        except (ValueError, TypeError):
            CTkMessagebox(
                title="Error",
                message=f"Invalid quantity value for {item}. Resetting to 0",
                icon="cancel"
            )
            qty_var.set(0)
            return

        new_qty = max(0, current_qty + change)

        # Only update if quantity actually changes
        if new_qty == current_qty:
            return
        
        qty_var.set(new_qty)
        
        # Ensure item exists in inventory before updating
        if item in self.inventory:
            self.inventory[item]["quantity"] = new_qty
            self.save_inventory()

            # Update UI label if it exists
            if item in self.item_labels:
                self.item_labels[item].configure(text=f"Qty: {new_qty}")
        else:
            CTkMessagebox(
                title="Error",
                message=f"Item '{item}' not found in inventory",
                icon="cancel"
            )


    def export_history_to_excel(self):
        """Export history data to an Excel File formatted correctly"""
        now = datetime.datetime.now().strftime("%m-%d-%Y_%H-%M-%S")
        excel_file = os.path.join(self.file_paths["export"], f"history_{now}.xlsx")

        os.makedirs(self.file_paths["export"], exist_ok=True)   # Ensure export directory exists
        
        # Check if history file exists
        if not os.path.exists(self.file_paths["history"]):
            CTkMessagebox(
                title="Error", 
                message="No history data found to export", 
                icon="cancel")
            return
        
        # Load history data
        try:
            with open(self.file_paths["history"], "r") as file:
                history_data = json.load(file)
                if not history_data:
                    CTkMessagebox(
                        title="Error",
                        message="History file is empty. Nothing to export",
                        icon="cancel"
                    )
                    return
        except json.JSONDecodeError:
            CTkMessagebox(
                title="Error", 
                message="History file is corrupted or invalid", 
                icon="cancel")
            return

        # Create an Excel Workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Transaction History"

        # Set headers
        headers = ["Date", "Quantity", "Product", "Cost", "Total"]
        ws.append(headers)

        # Make headers bold
        for col_num, header in enumerate(headers, 1):
            ws.cell(row=1, column=col_num).font = openpyxl.styles.Font(bold=True)

        # Write history data
        row_num = 2
        for date, transactions in history_data.items():
            ws.append([date, "", "", "", ""])

            for entry in transactions:
                quantity = entry.get("quantity", 0)
                item_name = entry.get("item", "Unknown Item")
                fixed_price = self.inventory.get(entry["item"], {}).get("price", "N/A")
                total_cost = entry.get("total", "N/A")

                ws.append(["", quantity, item_name, f"₱ {fixed_price}", f"₱ {total_cost}"])
            
            row_num += len(transactions) + 1
            ws.append([""]) # Blank row for separation

        # Auto adjust columns widths
        for col in ws.columns:
            max_length = max((len(str(cell.value)) if cell.value else 0) for cell in col)
            ws.column_dimensions[col[0].column_letter].width = max_length + 2

        # Save the Excel File
        try:
            wb.save(excel_file)
            CTkMessagebox(
                title="Export Successful", 
                message=f"History exported to\n{excel_file}", 
                icon="info")
            os.startfile(self.file_paths["export"])   # Open the export directory
        except Exception as e:
            CTkMessagebox(
                title="Export Error", 
                message=f"Failed to save Excel file.\nError: {str(e)}", 
                icon="cancel")


    def create_scrollable_inventory(self):
        """Create a scrollable inventory grid with images, names, and buttons"""
        # Create a Scrollable Frame
        self.scroll_frame = ctk.CTkScrollableFrame(self.root, fg_color=self.colors["bg"])
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        inner_frame = self.scroll_frame._parent_canvas  # This access the actual inner frame

        # Configure the scroll frame
        for col in range(7):
            inner_frame.grid_columnconfigure(col, weight=1)
                
                    
    def populate_inventory(self):
        """Populate the inventory grid inside the scrollable frame"""

        def round_corners(image, size=(280, 280), radius=30):
            """Load an image (or use provided PIL image), resize it, and apply rounded corners"""
            if isinstance(image, str):  # If image is a file path
                img = Image.open(image).convert("RGBA")
            else:   # If image is already a PIL image (placeholder)
                img = image.convert("RGBA")

            img = img.resize(size, Image.LANCZOS)

            # Create mask with rounded corners
            mask = Image.new("L", size, 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle((0, 0, *size), radius=radius, fill=255)

            # Apply mask to the image
            rounded = ImageOps.fit(img, size, centering=(0.5, 0.5))
            rounded.putalpha(mask)

            return rounded

        columns = 5
        row, col = 0, 0

        # Center the grid using a parent frame
        center_frame = ctk.CTkFrame(self.scroll_frame, fg_color=self.colors["bg"])
        center_frame.pack(expand=True, fill="both")

        # Configure column weights for even spacing
        for i in range(columns):
            center_frame.grid_columnconfigure(i, weight=1)

        # Loop through inventory items
        # for index, (item, data) in enumerate(self.inventory.items()):
        #     row = index // columns
        #     col = index % columns

        for item, data in self.inventory.items():            
            # Handle cases where data is just an integer
            if isinstance(data, int):
                data = {"price": 100, "quantity": data}

            price = data.get("price", 100)
            quantity = data.get("quantity", 0)
            
            item_frame = ctk.CTkFrame(center_frame, fg_color="#3d3d3d", corner_radius=15)
            item_frame.grid(row=row, column=col, padx=15, pady=10, sticky="nsew")

            image_container = ctk.CTkFrame(item_frame, fg_color="#3d3d3d", corner_radius=15)
            image_container.pack(padx=10, pady=10)

            # Load Image
            # image_path = os.path.join("assets", f"{item.lower().replace(' ', '_')}.jpg")
            image_path = self.inventory[item].get("image", "")

            # Create a blank image (solid color) if no image is found
            placeholder = Image.new("RGB", (280, 280), color=(200, 200, 200))  # Light gray
            rounded_img = round_corners(image_path) if os.path.exists(image_path) else placeholder
            
            img = ctk.CTkImage(light_image=rounded_img, size=(280, 280))

            item_img = ctk.CTkLabel(item_frame, image=img, text="")
            item_img.image = img
            item_img.pack(padx=10, pady=10)

            # Item Name
            item_label = ctk.CTkLabel(image_container, text=item, font=("Arial", 30))
            item_label.pack(pady=10)
            
            # Quantity Display
            qty_var = ctk.IntVar(value=quantity)
            qty_label = ctk.CTkLabel(item_frame, textvariable=qty_var, font=("Arial", 20, "bold"))
            qty_label.pack(pady=5)
            
            # Price Display (Below Quantity)
            price_label = ctk.CTkLabel(item_frame, text=f"₱ {price}", font=("Arial", 25))
            price_label.pack(pady=5)

            # Buttons for Layout (Left: `+` & `-`, Right: "Add")
            btn_frame = ctk.CTkFrame(item_frame, fg_color="#3d3d3d")
            btn_frame.pack(pady=5)
            
            btn_minus = ctk.CTkButton(btn_frame, text="-", font=("Arial", 14, "bold"), fg_color=self.colors["btn"],
                                command=lambda i=item, q=qty_var: self.update_quantity(i, q, -1),
                                width=50, height=50)
            btn_minus.pack(side="left", padx=5, pady=5)

            btn_plus = ctk.CTkButton(btn_frame, text="+", font=("Arial", 14, "bold"), fg_color=self.colors["btn"],
                                command=lambda i=item, q=qty_var: self.update_quantity(i, q, 1),
                                width=50, height=50)
            btn_plus.pack(side="left", padx=5, pady=5)

            btn_add = ctk.CTkButton(btn_frame, text="Add", font=("Arial", 16, "bold"), fg_color="#2a9d8f",
                                command=lambda i=item, q=qty_var: self.add_amount(i, q),
                                width=100, height=50)
            btn_add.pack(side="right", padx=10, pady=5)
            
            self.quantity_vars[item] = qty_var

            # Manage Columns
            col += 1
            if col >= columns:
                col = 0
                row += 1


    def add_amount(self, item, qty_var):
        """Save the calculated amount (price x quantity) to JSON and log history"""
        quantity = qty_var.get()

        if quantity == 0:
            CTkMessagebox(title="Export Error", message="Please select at least 1 item", icon="cancel")
            return

        # Ensure price exists
        price = self.inventory[item].get("price", 100)
        total_amount = price * quantity

        # Load previous data or create a new one
        data = self.load_amount_data()

        # Ensure `total` and `entries` exist
        data.setdefault("total", 0)
        data.setdefault("entries", [])

        # Update total amount and history
        data["total"] += total_amount
        data["entries"].append({"item": item, "quantity": quantity, "total": total_amount})

        self.save_amount_data(data)

        # Update total label
        self.total_label.configure(text=f"Total: ₱ {data['total']}")

        # Log the purchase in history
        self.log_purchase(item, quantity, total_amount)

        CTkMessagebox(title="Success", message=f"Added {quantity} x {item} for ₱ {total_amount}. New Total: ₱ {data['total']}", icon="info")

        # Deduct stock instead of resetting to zero
        self.inventory[item]["quantity"] = max(0, self.inventory[item]["quantity"] - quantity)

        # Reset quantity after adding
        qty_var.set(0)
        # self.update_ui()

        # Saved updated inventory
        with open(self.file_paths["inventory"], "w") as file:
            json.dump(self.inventory, file, indent=4)


    def log_purchase(self, item, quantity, total_amount):
        """Log each purchase in history.json under the correct date"""
        today = datetime.datetime.now().strftime("%B %d, %Y")

        history_data = {}

        # Check if the history file exists and load existing data;
        if self.file_paths["history"].exists():
            try:
                with open(self.file_paths["history"], "r") as file:
                    history_data = json.load(file)
                    if not isinstance(history_data, dict):
                        raise ValueError("Invalid history file format")
            except (json.JSONDecodeError, ValueError):
                history_data = {}

        # Add new entry for today
        history_data.setdefault(today, []).append({
            "quantity": quantity,
            "item": item,
            "total": total_amount
        })

        # Save the updated history with error handling
        try:
            with open(self.file_paths["history"], "w") as file:
                json.dump(history_data, file, indent=4)
        except (OSError, IOError) as e:
            CTkMessagebox(
                title="Error",
                message=f"Failed to save history: {e}",
                icon="cancel"
            )
    
    
    def load_amount_data(self):
        """Load previous spending data from JSON"""
        if self.file_paths["amounts"]:
            try:
                with open(self.file_paths["amounts"], "r") as file:
                    data = json.load(file)
                    if not isinstance(data, dict) or "total" not in data or "entries" not in data:
                        raise ValueError("Invalid amount file format")
                    return data
            except (json.JSONDecodeError, ValueError):
                CTkMessagebox(
                    title="Error",
                    message="Amount file is corrupted. Resetting data",
                    icon="cancel"
                )
        
        # Return a default structure if file is missing or corrupted
        return {"total": 0, "entries": []}


    def save_amount_data(self, data):
        """Save spending data to JSON"""
        temp_file = self.file_paths["amounts"].with_suffix(".tmp")

        try:
            with temp_file.open("w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)

            temp_file.replace(self.file_paths["amounts"])   # Replace the original file with the temp file
        except (OSError, IOError) as e:
            CTkMessagebox(
                title="Error", 
                message=f"Failed to save data: {e}", 
                icon="cancel")


    def open_history_window(self):
        """Open a new window showing purchase history"""

        # Prevent multiple history windows
        if hasattr(self, "history_window") and self.history_window.winfo_exists():
            self.history_window.lift()
            self.history_window.focus_force()
            return

        # Load history data
        history_data = {}
        if os.path.exists(self.file_paths["history"]):
            try:
                with open(self.file_paths["history"], "r") as file:
                    history_data = json.load(file)
            except (json.JSONDecodeError, ValueError):
                CTkMessagebox(title="Error",
                              message="History file is corrupted.",
                              icon="cancel")
                return
        else:
            CTkMessagebox(
                title="Error", 
                message="No history data found", 
                icon="cancel")
            return

        # Create new window
        self.history_window = ctk.CTkToplevel(self.root)
        self.history_window.title("Transaction History")
        self.history_window.geometry("900x900")
        self.history_window.attributes("-topmost", True)
        self.history_window.configure(fg_color=self.colors["bg"])

        # Center the window dynamically
        self.history_window.update_idletasks()
        window_width, window_height = 900, 900
        screen_width = self.history_window.winfo_screenwidth()
        screen_height = self.history_window.winfo_screenheight()
        x_position = (screen_width // 2) - (window_width // 2)
        y_position = (screen_height // 2) - (window_height // 2)
        self.history_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        # Title
        title_label = ctk.CTkLabel(self.history_window, text="Transaction History", font=("Arial", 20, "bold"))
        title_label.pack(pady=10)

        # Scrollable CTkFrame
        scroll_frame = ctk.CTkScrollableFrame(self.history_window, fg_color="#3A3A3A")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Display purchase history (Empty after reset)
        if not history_data:
            empty_label = ctk.CTkLabel(scroll_frame, text="No transaction history available", font=("Arial", 16), text_color="white")
            empty_label.pack(pady=20)
        else:
            for  date, transactions in history_data.items():
                date_label = ctk.CTkLabel(scroll_frame, text=date, font=("Arial", 20, "bold"), fg_color="transparent")
                date_label.pack(pady=5)

                total = 0
                for entry in transactions:
                    text = f"{entry['quantity']}x → {entry['item']} (₱ {entry['total']})"
                    item_label = ctk.CTkLabel(scroll_frame, text=text, font=("Arial", 20), fg_color="transparent")
                    item_label.pack()
                    total += entry['total']
                
                total_label = ctk.CTkLabel(scroll_frame, text=f"Total: ₱ {total}", font=("Arial", 22, "bold"), fg_color="transparent")
                total_label.pack(pady=15)

                divider = ctk.CTkFrame(scroll_frame, fg_color="#555555", height=2)
                divider.pack(fill="x", padx=20, pady=10)
                    
        # Button Frame
        button_frame = ctk.CTkFrame(self.history_window, fg_color=self.colors["bg"])
        button_frame.pack(fill="x", pady=10)

        # Reset CTkButton
        reset_button = ctk.CTkButton(button_frame, text="Reset History", font=("Arial", 18, "bold"),
                                     fg_color=self.colors["btn"], command=lambda: self.reset_history(self.history_window),
                                     width=140, height=40)
        reset_button.pack(pady=10)


    def reset_history(self, history_window):
        """Manually reset the history.json file"""

        response = CTkMessagebox(
            title="Confirm Reset",
            message="Are you sure you want to reset the history?", 
            icon="question", 
            option_1="Yes", 
            option_2="No"
            ).get()
        if response != "Yes":
            return

        # Clear history file
        try:
            with open(self.file_paths["history"], "w") as file:
                json.dump({}, file, indent=4)

            # Reset stored total amount
            reset_data = {"total": 0, "entries": []}
            self.save_amount_data(reset_data)

            # Update total label if it exists
            if hasattr(self, "total_label"):
                self.total_label.configure(text="Total: ₱ 0")

            CTkMessagebox(
                title="Reset Successful", 
                message="History and Total have been cleared", 
                icon="info")

            # Clear all widgets in the history window before repopulating
            for widget in history_window.winfo_children():
                widget.destroy()

            # Repopulate the history window with an empty message
            empty_label = ctk.CTkLabel(history_window, text="No transaction history available", font=("Arial", 18), text_color="white")
            empty_label.pack(pady=20)
        except (OSError, IOError) as e:
            CTkMessagebox(
                title="Error",
                message=f"Failed to reset history: {e}",
                icon="cancel"
            )
                

    def populate_history_ui(self, history_window):
        """Repopulate the history window after resetting"""

        # Clear existing widgets in history window before repopulating
        for widget in history_window.winfo_children():
            widget.destroy()

        # Load history data
        history_window = {}
        if os.path.exists(self.file_paths["history"]):
            try:
                with open(self.file_paths["history"], "r") as file:
                    history_data = json.load(file)
            except (json.JSONDecodeError, ValueError):
                history_data = {}

        # Title
        title_label = ctk.CTkLabel(history_window, text="Transaction History", font=("Arial", 20, "bold"))
        title_label.pack(pady=10)

        # Scrollable CTkFrame
        scroll_frame = ctk.CTkScrollableFrame(history_window, fg_color="#3a3a3a")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
        # Display purchase history (Empty after reset)
        if not history_data:
            empty_label = ctk.CTkLabel(scroll_frame, text="No transaction history available", font=("Arial", 16), text_color="white")
            empty_label.pack(pady=20)
        else:
            for date, transactions in history_data.items():
                date_label = ctk.CTkLabel(scroll_frame, text=date, font=("Arial", 20, "bold"), fg_color="transparent", text_color="white")
                date_label.pack(pady=5)

                total = 0
                for entry in transactions:
                    text = f"{entry['quantity']}x → {entry['item']} (₱ {entry['total']})"
                    item_label = ctk.CTkLabel(scroll_frame, text=text, font=("Arial", 20), fg_color="transparent", text_color="white")
                    item_label.pack()
                    total += entry['total']

                total_label = ctk.CTkLabel(scroll_frame, text=f"Total: ₱ {total}", font=("Arial", 22, "bold"), fg_color="transparent", text_color="white")
                total_label.pack(pady=15)

                divider = ctk.CTkFrame(scroll_frame, fg_color="#555555", height=2)
                divider.pack(fill="x", padx=20, pady=10)

        # Button Frame
        button_frame = ctk.CTkFrame(self.history_window, fg_color=self.colors["bg"])
        button_frame.pack(fill="x", pady=10)
        
        # Reset CTkButton
        reset_button = ctk.CTkButton(button_frame, text="Reset History", font=("Arial", 18, "bold"),
                                     fg_color=self.colors["btn"], command=lambda: self.reset_history(history_window),
                                     width=140, height=40)
        reset_button.pack(pady=10)
        
        
    def reset_total(self):
        """Reset the total amount spent back to 0 in amounts.json"""

        response = CTkMessagebox(
            title="Confirm Reset", 
            message="Are you sure you want to reset the total amount?",
            icon="question",
            option_1="Yes", 
            option_2="No"
            ).get()

        if response == "Yes":
            try:
                # Reset total and clear entries
                reset_data = {"total": 0, "entries": []}
                self.save_amount_data(reset_data)

                # Update displayed total
                if hasattr(self, "total_label") and self.total_label:
                    self.total_label.configure(text="Total: ₱ 0")

                # Ensure file exists before resetting
                # self.load_amount_data()
                CTkMessagebox(title="Reset Successful", message="Total amount has been reset to ₱ 0.", icon="info")
            except Exception as e:
                CTkMessagebox(title="Error", message=f"Failed to reset total amount: {str(e)}", icon="cancel")
            

# # Run the application
# if __name__ == "__main__":
#     # Initialize the main application window
#     root = ctk.CTk()
#     app = InventoryManagement(root) # Create an instance of InventoryManagement
#     root.mainloop() # Run the application
