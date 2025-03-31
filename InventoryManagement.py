import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from PIL import Image, ImageDraw, ImageOps
import json
from pathlib import Path
import os
import datetime
import openpyxl

class InventoryManagement:
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
            "bg": "#2b2b2b",
            "btn": "#1f6aa5",
            "text": "#ffffff"
        }

        self.quantity_vars = {}

        # Define inventory directory
        # self.inventory_dir = os.path.join(os.getcwd(), "inventory")
        self.inventory_dir = Path.cwd() / "inventory"
        self.inventory_dir.mkdir(exist_ok=True) # Creates directory if it doesn't exist

        # Define file paths
        self.json_file = self.inventory_dir / "inventory.json"
        self.amount_file = self.inventory_dir / "amounts.json"
        self.history_file = self.inventory_dir / "history.json"
        self.export_dir = self.inventory_dir
        
        # Load or initialize inventory
        self.inventory = self.load_inventory()
      
        # Dictionary to store item labels for updating
        self.item_labels = {}

        # Build UI
        self.create_ui()
                
    def load_inventory(self):
        """Load inventory from JSON file or create a default one if it doesn't exist"""
        json_path = self.json_file

        if json_path.exists():
            with json_path.open("r") as file:
                try:
                    inventory = json.load(file)
                    # Ensure the inventory is always a dictionary
                    if not isinstance(inventory, dict):
                        raise ValueError("Invalid inventory format")
                    
                    # Ensure allitems have a quantity field
                    for item, data in inventory.items():
                        if isinstance(data, int):
                            inventory[item] = {"price": 100, "quantity": data} 
                        elif isinstance(data, dict) and "quantity" not in data:
                            inventory[item]["quantity"] = 0

                except (json.JSONDecodeError, ValueError):
                    CTkMessagebox(title="Error", message="Inventory file is corrupted or invalid. Resetting inventory", icon="cancel")
                    inventory = {}
        else:
            inventory = {}

        # Reset all quantities to 0 on startup
        for item in inventory.values():
            item["quantity"] = 0

        # Save the updated inventory with reset quantities
        self.save_inventory(inventory)

        return inventory


    def save_inventory(self, data=None):
        """Save inventory data to JSON file safely"""
        if data is None:
            data = self.inventory
        
        json_path = Path(self.json_file)

        try:
            json_path.write_text(json.dumps(data, indent=4))
        except (OSError, IOError) as e:
            CTkMessagebox(title="Error", message=f"Failed to save inventory: {e}", icon="cancel")

    def create_ui(self):
        """Create the user interface"""
        # Title CTkLabel
        title_label = ctk.CTkLabel(self.root, text="Inventory Management", 
                                   font=("Arial", 24, "bold"), text_color=self.colors["text"])
        title_label.pack(pady=20)

        # Load the saved total from JSON
        saved_data = self.load_amount_data()
        saved_total = saved_data.get("total", 0)
        
        # Total Amount CTkLabel (Top Left)
        self.total_label = ctk.CTkLabel(self.root, text=f"Total: ₱ {saved_total}", font=("Arial", 18, "bold"))
        self.total_label.place(x=20, y=20)

        # Reset CTkButton
        btn_reset_total = ctk.CTkButton(self.root, text="Reset Total", font=("Arial", 16),
                                    fg_color=self.colors["btn"], command=self.reset_total,
                                    width=140, height=40)
        btn_reset_total.place(x=200, y=15)

        # Create the scrollable inventory area
        self.create_scrollable_inventory()

        self.populate_inventory()

        # Create a frame for the buttons at the bottom right
        button_frame = ctk.CTkFrame(self.root, fg_color="#242424")
        button_frame.pack(side="bottom", anchor="se", padx=20, pady=20)

        # History CTkButton
        btn_history = ctk.CTkButton(self.root, text="View History", font=("Arial", 16), 
                                fg_color=self.colors["btn"], command=self.open_history_window,
                                width=140, height=50)
        btn_history.pack(pady=20)

        # Exit button
        exit_btn = ctk.CTkButton(button_frame, text="Exit", font=("Arial", 16, "bold"),
                            fg_color=self.colors["btn"], command=self.confirm_exit,
                            width=140, height=50, corner_radius=10, border_color="white")
        exit_btn.pack(side="right", padx=10, pady=10)

        # Export button
        export_btn = ctk.CTkButton(button_frame, text="Export History", font=("Arial", 16, "bold"),
                               fg_color=self.colors["btn"], command=self.export_history_to_excel,
                               width=180, height=50, corner_radius=10, border_color="white")
        export_btn.pack(side="right", padx=10, pady=10)

    def confirm_exit(self):
        """Ask for confirmation before exiting the application"""
        response = CTkMessagebox(title="Exit Confirmation", message="Are you sure you want to exit?", icon="question", option_1="Yes", option_2="No")
        if response.get() == "Yes":
            self.root.destroy()
        
    def update_quantity(self, item, qty_var, change):
        """Update the selected quantity"""
        current_qty = qty_var.get()
        new_qty = max(0, current_qty + change)

        # Only update if quantity actually changes
        if new_qty == current_qty:
            return
        
        qty_var.set(new_qty)
        self.inventory[item]["quantity"] = new_qty
        self.save_inventory()

        # If there's a UI label showing quantity, update it here
        if item in self.item_labels:
            self.item_labels[item].configure(text=f"Qty: {new_qty}")

    def export_history_to_excel(self):
        """Export history data to an excel File formatted correctly"""
        now = datetime.datetime.now().strftime("%m-%d-%Y_%H-%M-%S")
        excel_file = os.path.join(self.export_dir, f"history_{now}.xlsx")

        # Ensure export directory exists
        os.makedirs(self.export_dir, exist_ok=True)
        
        # Check if history file exists
        if not os.path.exists(self.history_file):
            CTkMessagebox(title="Error", message="No history data found to export", icon="cancel")
            return
        
        try:
            with open(self.history_file, "r") as file:
                history_data = json.load(file)
        except json.JSONDecodeError:
            CTkMessagebox(title="Error", message="History file is corrupted or invalid", icon="cancel")
            return

        # Create an Excel Workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Transaction History"

        # Set headers
        headers = ["Date", "Quantity", "Product", "Cost", "Total"]
        ws.append(headers)

        for col_num, header in enumerate(headers, 1):
            ws.cell(row=1, column=col_num).font = openpyxl.styles.Font(bold=True)

        # Write history data
        row_num = 2
        for date, transactions in history_data.items():
            ws.append([date, "", "", "", ""])

            for entry in transactions:
                fixed_price = self.inventory.get(entry["item"], {}).get("price", "N/A")
                ws.append(["", entry["quantity"], entry["item"], f"₱ {fixed_price}", f"₱ {entry['total']}"])
            
            row_num += len(transactions) + 1
            ws.append([""])

        # Auto adjust columns widths
        for col in ws.columns:
            max_length = max((len(str(cell.value)) if cell.value else 0) for cell in col)
            ws.column_dimensions[col[0].column_letter].width = max_length + 2

        # Save the Excel File
        try:
            wb.save(excel_file)
            CTkMessagebox(title="Export Successful", message=f"History exported to\n{excel_file}", icon="info")
            os.startfile(self.export_dir)
        except Exception as e:
            CTkMessagebox(title="Export Error", message=f"Failed to save Excel file.\nError: {str(e)}", icon="cancel")

    def create_scrollable_inventory(self):
        """Create a scrollable inventory grid with images, names, and buttons"""

        # Create a Scrollable Frame
        self.scroll_frame = ctk.CTkScrollableFrame(self.root, fg_color=self.colors["bg"])
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Configure the scroll frame
        for col in range(7):
            self.scroll_frame.grid_columnconfigure(0, weight=1)
                    
    def populate_inventory(self):
        """Populate the inventory grid inside the scrollable frame"""

        def round_corners(image, size=(280, 280), radius=30):
            """Load an image (or use provided PIL image), resize it, and apply rounded corners"""
            if isinstance(image, str):  # If image is a file path
                img = Image.open(image).convert("RGBA")
            else:  # If image is already a PIL image (placeholder)
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

        columns = 7
        row, col = 0, 0

        # Center the grid using a parent frame
        center_frame = ctk.CTkFrame(self.scroll_frame, fg_color=self.colors["bg"])
        center_frame.pack(padx=50)

        # Configure column weights for even spacing
        for i in range(columns):
            center_frame.grid_columnconfigure(i, weight=1)

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
            image_path = os.path.join("assets", f"{item.lower().replace(' ', '_')}.jpg")
            if os.path.exists(image_path):
                rounded_img = round_corners(image_path)
            else:
                # Create a blank image (solid color) if no image is found
                placeholder = Image.new("RGB", (280, 280), color=(200, 200, 200))  # Light gray
                rounded_img = round_corners(placeholder)  # Now correctly processes PIL images
            
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
        """Save thhe calculated amount (price x quantity) to JSON and log history"""
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
        with open(self.json_file, "w") as file:
            json.dump(self.inventory, file, indent=4)

    # def update_ui(self):
    #     """Refresh UI elements after inventory updates"""
    #     for item, label in self.item_labels.items():
    #         label.configure(text=f"{item}: {self.inventory[item]['quantity']}")

    #     self.total_label.configure(text=f"Total: ₱ {self.calculate_total()}")

    # def calculate_total(self):
    #     """Calculate the total price of all items in inventory"""
    #     total = sum(item["quantity"] * item.get("price", 0) for item in self.inventory.values())
    #     return total

    def log_purchase(self, item, quantity, total_amount):
        """Log each purchase in history.json under the correct date"""
        today = datetime.datetime.now().strftime("%B %d, %Y")

        # Load existing history or create new
        history_data = {}
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r") as file:
                    history_data = json.load(file)
            except (json.JSONDecodeError, ValueError):
                history_data = {}

        # Add new entry for today
        history_data.setdefault(today, []).append({
            "quantity": quantity,
            "item": item,
            "total": total_amount
        })

        # Save updated history
        with open(self.history_file, "w") as file:
            json.dump(history_data, file, indent=4)
    
    def load_amount_data(self):
        """Load previous spending data from JSON"""
        if os.path.exists(self.amount_file):
            try:
                with open(self.amount_file, "r") as file:
                    return json.load(file)
            except (json.JSONDecodeError, ValueError):
                pass
        
        # Create default JSON structrue if file doesn't exist
        return {"total": 0, "entries": []}

    def save_amount_data(self, data):
        """Save spending data to JSON"""
        temp_file = self.amount_file.with_suffix(".tmp")

        try:
            with temp_file.open("w") as file:
                json.dump(data, file, indent=4)
            # os.replace(temp_file, self.amount_file)
            temp_file.replace(self.amount_file)
        except (OSError, IOError) as e:
            CTkMessagebox(title="Error", message=f"Failed to save data: {e}", icon="cancel")

    def open_history_window(self):
        """Open a new window showing purchase history"""

        # Prevent multiple history windows
        if hasattr(self, "history_window") and self.history_window.winfo_exists():
            self.history_window.lift()
            self.history_window.focus_force()
            return

        # Load history data
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as file:
                history_data = json.load(file)
        else:
            CTkMessagebox(title="Error", message="No history data found", icon="cancel")
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
        response = CTkMessagebox(title="Confirm Reset", message="Are you sure you want to reset the history?", icon="question", option_1="Yes", option_2="No")
        if response.get() == "No":
            return

        # Clear history file
        with open(self.history_file, "w") as file:
            json.dump({}, file, indent=4)

        # Reset stored total amount
        reset_data = {"total": 0, "entries": []}
        self.save_amount_data(reset_data)

        # Update total label if it exists
        if hasattr(self, "total_label"):
            self.total_label.configure(text="Total: ₱ 0")

        CTkMessagebox(title="Reset Successful", message="History and Total have been cleared", icon="info")

        # Clear all widgets in the history window before repopulating
        for widget in history_window.winfo_children():
            widget.destroy()
                
        self.populate_history_ui(history_window)

    def populate_history_ui(self, history_window):
        """Repopulate the history window after resetting"""

        # Load history data
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as file:
                history_data = json.load(file)
        else:
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
        response = CTkMessagebox(title="Confirm Reset", message="Are you sure you want to reset the total amount?", icon="question", option_1="Yes", option_2="No")

        if response.get() == "Yes":
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
            
# Run the application
if __name__ == "__main__":
    root = ctk.CTk()
    app = InventoryManagement(root)
    root.mainloop()