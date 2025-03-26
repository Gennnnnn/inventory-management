import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import json
import os
import tkinter.messagebox as msgbox
import datetime
import openpyxl

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
        
        self.quantity_vars = {}

        # Define inventory directory
        self.inventory_dir = os.path.join(os.getcwd(), "inventory")

        # Ensure directory exists
        if not os.path.exists(self.inventory_dir):
            os.makedirs(self.inventory_dir)
                    
        # Define file paths
        self.json_file = os.path.join(self.inventory_dir, "inventory.json")
        self.amount_file = os.path.join(self.inventory_dir, "amounts.json")
        self.history_file = os.path.join(self.inventory_dir, "history.json")
        self.export_dir = self.inventory_dir
        
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
                inventory = json.load(file)
            
            for item, data in inventory.items():
                if isinstance(data, int):
                    inventory[item] = {"price": 100, "quantity": data}
                elif "quantity" not in data:
                    inventory[item]["quantity"] = 0

            self.save_inventory(inventory)
            return inventory
        
        else:
            default_inventory = {
                "Hammer": {"price": 500, "quantity": 0},
                "Screwdriver": {"price": 300, "quantity": 0},
                "Saw": {"price": 700, "quantity": 0},
                "Wood Planks": {"price": 200, "quantity": 0},
                "Nails (Box)": {"price": 50, "quantity": 0},
                "Varnish Can": {"price": 150, "quantity": 0}
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

        # Load the saved total from JSON
        saved_data = self.load_amount_data()
        saved_total = saved_data["total"]
        
        # Total Amount Label (Top Left)
        self.total_label = tk.Label(self.root, text=f"Total: ₱ {saved_total}", font=("Arial", 18, "bold"), bg=self.BG_COLOR, fg="#333")
        self.total_label.place(x=20, y=20)

        # Reset Button
        btn_reset_total = tk.Button(self.root, text="Reset Total", font=("Arial", 16), bg="#ce2a22", fg="#fff",
                                    command=self.reset_total,
                                    width=10, height=1)
        btn_reset_total.place(x=200, y=15)

        # Create the scrollable inventory area
        self.create_scrollable_inventory()
        self.populate_inventory()

        # Create a frame for the buttons at the bottom right
        button_frame = tk.Frame(self.root, bg=self.BG_COLOR)
        button_frame.pack(side="bottom", anchor="se", padx=20, pady=20)

        # History Button
        btn_history = tk.Button(self.root, text="View History", font=("Arial", 16), bg="#424242", fg="#fff",
                                command=self.open_history_window,
                                width=15, height=2)
        btn_history.pack(pady=20)

        # Exit button
        exit_btn = tk.Button(button_frame, text="Exit", font=("Arial", 16, "bold"),
                            bg="#ce2a22", fg="#fff", command=self.confirm_exit,
                            width=10, height=2, borderwidth=2)
        exit_btn.pack(side="right", padx=10, pady=10)

        # Export button
        export_btn = tk.Button(button_frame, text="Export History", font=("Arial", 16, "bold"),
                               bg="#424242", fg="#fff", command=self.export_history_to_excel,
                               width=15, height=2, borderwidth=2)
        export_btn.pack(side="right", padx=10, pady=10)

    def confirm_exit(self):
        """Ask for confirmation before exiting the application"""
        if msgbox.askyesno("Exit Confirmation", "Are you sure you want to exit?"):
            self.root.destroy()
        
    def update_quantity(self, item, qty_var, change):
        """Update the selected quantity"""
        new_qty = max(0, qty_var.get() + change)
        qty_var.set(new_qty)
        self.inventory[item]["quantity"] = new_qty

        self.save_inventory()
    
    def export_history_to_excel(self):
        """Export history data to an excel File formatted correctly"""
        now = datetime.datetime.now().strftime("%m-%d-%Y_%H-%M-%S")
        excel_file = os.path.join(self.export_dir, f"history_{now}.xlsx")

        # Load history data
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)
        
        if not os.path.exists(self.history_file):
            msgbox.showerror("Error", "No history data found to export")
            return
        
        with open(self.history_file, "r") as file:
            history_data = json.load(file)

        # Create an Excel Workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Transaction History"

        # Set headers
        ws.append(["Date", "Quantity", "Product", "Cost", "Total"])

        # Write history data
        for date, transactions in history_data.items():
            ws.append([date, "", "", "", ""])

            for entry in transactions:
                fixed_price = self.inventory.get(entry["item"], {}).get("price", "N/A")
                ws.append(["", entry["quantity"], entry["item"], f"₱ {fixed_price}", f"₱ {entry['total']}"])
            
            ws.append([""])

        # Auto adjust columns widths
        for col in ws.columns:
            max_length = 0
            col_letter = col[0].column_letter
            for cell in col:
                try:
                    max_length = max(max_length, len(str(cell.value)))
                except:
                    pass
            ws.column_dimensions[col_letter].width = max_length + 2

        # Save the Excel File
        wb.save(excel_file)

        # Show success message
        msgbox.showinfo("Export Successful", f"History exported to:\n{excel_file}")

        os.startfile(self.export_dir)
    
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
        columns = 4
        row, col = 0, 0

        # Center the grid using a parent frame
        center_frame = tk.Frame(self.scroll_frame, bg=self.BG_COLOR)
        center_frame.pack(padx=110)

        # Configure column weights for even spacing
        for i in range(columns):
            center_frame.grid_columnconfigure(i, weight=1)

        for item, data in self.inventory.items():            
            if isinstance(data, int):
                data = {"price": 100, "quantity": data}

            price = data["price"]
            quantity = data["quantity"]
            
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

            item_label = tk.Label(item_frame, text=f"{item}", font=("Arial", 30), bg=self.BG_COLOR)
            item_label.pack()
            
            # Quantity Display
            qty_var = tk.IntVar(value=quantity)
            qty_label = tk.Label(item_frame, textvariable=qty_var, font=("Arial", 16, "bold"), bg=self.BG_COLOR)
            qty_label.pack()
            
            # Price Display (Below Quantity)
            price_label = tk.Label(item_frame, text=f"₱  {price}", font=("Arial", 14, "bold"), bg=self.BG_COLOR, fg="#228B22")
            price_label.pack()

            # Buttons for Layout (Left: `+` & `-`, Right: "Add")
            btn_frame = tk.Frame(item_frame, bg=self.BG_COLOR)
            btn_frame.pack()
            
            # "-" Button
            btn_minus = tk.Button(btn_frame, text="-", font=("Arial", 14, "bold"), bg=self.BTN_COLOR, fg="#fff",
                                  command=lambda i=item, q=qty_var: self.update_quantity(i, q, -1),
                                  width=2, height=1, borderwidth=1)
            btn_minus.pack(side="left", padx=5, pady=5)

            btn_plus = tk.Button(btn_frame, text="+", font=("Arial", 14, "bold"), bg=self.BTN_COLOR, fg="#fff",
                                  command=lambda i=item, q=qty_var: self.update_quantity(i, q, 1),
                                  width=2, height=1, borderwidth=1)
            btn_plus.pack(side="left", padx=5, pady=5)

            btn_add = tk.Button(btn_frame, text="Add", font=("Arial", 16, "bold"), bg="#2a9d8f", fg="#fff",
                                  command=lambda i=item, q=qty_var: self.add_amount(i, q),
                                  width=8, height=1, borderwidth=1)
            btn_add.pack(side="right", padx=10, pady=5)
            
            self.quantity_vars[item] = qty_var

            col += 1
            if col >= columns:
                col = 0
                row += 1
                
    def add_amount(self, item, qty_var):
        """Save thhe calculated amount (price x quantity) to JSON and log history"""
        quantity = qty_var.get()
        if quantity == 0:
            msgbox.showerror("Invalid Input", "Please select at least 1 item.")
            return

        price = self.inventory[item]["price"]
        total_amount = price * quantity

        # Load previous data or create a new one
        data = self.load_amount_data()
        data["total"] += total_amount
        data["entries"].append({"item": item, "quantity": quantity, "total": total_amount})

        self.save_amount_data(data)

        # Save to history.json
        self.total_label.config(text=f"Total: ₱ {data['total']}")
        self.log_purchase(item, quantity, total_amount)

        msgbox.showinfo("Success", f"Added {quantity} x {item} for ₱ {total_amount}. New Total: ₱ {data['total']}")

        # Reset quantity after adding
        qty_var.set(0)
        self.inventory[item]["quantity"] = 0

    def log_purchase(self, item, quantity, total_amount):
        """Log each purchase in history.json under the correct date"""
        today = datetime.datetime.now().strftime("%B %d, %Y")

        # Load existing history or create new
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as file:
                history_data = json.load(file)
        else:
            history_data = {}

        # Add new entry for today
        if today not in history_data:
            history_data[today] = []

        history_data[today].append({
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
            with open(self.amount_file, "r") as file:
                return json.load(file)
        
        # Create default JSON structrue if file doesn't exist
        default_data = {"total": 0, "entries": []}
        self.save_amount_data(default_data)
        return default_data

    def save_amount_data(self, data):
        """Save spending data to JSON"""
        with open(self.amount_file, "w") as file:
            json.dump(data, file, indent=4)

    def open_history_window(self):
        """Open a new window showing purchase history"""

        # Load history data
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as file:
                history_data = json.load(file)
        else:
            msgbox.showerror("Error", "No history data found.")
            return

        # Create new window
        history_window = tk.Toplevel(self.root)
        history_window.title("Transaction History")
        history_window.geometry("600x600")

        # Center the window dynamically
        history_window.update_idletasks()
        window_width = 600
        window_height = 600
        screen_width = history_window.winfo_screenwidth()
        screen_height = history_window.winfo_screenheight()
        x_position = (screen_width // 2) - (window_width // 2)
        y_position = (screen_height // 2) - (window_height // 2)
        history_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        history_window.config(bg="#efebe2")

        # Title
        title_label = tk.Label(history_window, text="Transaction History", font=("Arial", 20, "bold"), bg="#efebe2")
        title_label.pack(pady=10)

        # Scrollable Frame
        canvas = tk.Canvas(history_window, bg="#efebe2")
        scrollbar = tk.Scrollbar(history_window, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="#efebe2")

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        window = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Display purchase history
        for  date, transactions in history_data.items():
            date_label = tk.Label(scroll_frame, text=date, font=("Arial", 16, "bold"), bg="#efebe2", fg="#333",
                                  justify="center", width=46)
            date_label.pack(pady=5)

            total = 0
            for entry in transactions:
                text = f"{entry['quantity']}x → {entry['item']} (₱ {entry['total']})"
                item_label = tk.Label(scroll_frame, text=text, font=("Arial", 14), bg="#efebe2",
                                      justify="center", width=46)
                item_label.pack(padx=2)

                total += entry['total']
            
            total_label = tk.Label(scroll_frame, text=f"Total: ₱ {total}", font=("Arial", 14, "bold"), bg="#efebe2", fg="#333",
                                   justify="center", width=46)
            total_label.pack(pady=5)
                    
        # Reset Button
        reset_button = tk.Button(scroll_frame, text="Reset History", font=("Arial", 14, "bold"), bg="#ce2a22", fg="#fff",
                                 command=lambda: self.reset_history(history_window))
        reset_button.pack(padx=240, pady=10, anchor="center")

    def reset_history(self, history_window):
        """Manually reset the history.json file"""
        confirm = msgbox.askyesno("Confirm Reset", "Are you sure you want to reset the history?")

        if confirm:
            with open("C:\\inventory\\history.json", "w") as file:
                json.dump({}, file, indent=4)

            reset_data = {"total": 0, "entries": []}
            self.save_amount_data(reset_data)
            self.total_label.config(text="Total: ₱ 0")
            
            msgbox.showinfo("Reset successful", "History and Total have been cleared.")

            for widget in history_window.winfo_children():
                widget.destroy()
                
            self.populate_history_ui(history_window)

        # history_window.destroy()
        history_window.lift()
        history_window.focus_force()
    
    def populate_history_ui(self, history_window):
        """Repopulate the history window after resetting"""

        # Load history data
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as file:
                history_data = json.load(file)
        else:
            history_data = {}

        # Title
        title_label = tk.Label(history_window, text="Transaction History", font=("Arial", 20, "bold"), bg="#efebe2")
        title_label.pack(pady=10)

        # Scrollable Frame
        canvas = tk.Canvas(history_window, bg="#efebe2")
        scrollbar = tk.Scrollbar(history_window, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="#efebe2")

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Display purchase history (Empty after reset)
        for date, transactions in history_data.items():
            date_label = tk.Label(scroll_frame, text=date, font=("Arial", 16, "bold"), bg="#efebe2", fg="#333",
                                justify="center", width=50)
            date_label.pack(pady=5)

            total = 0
            for entry in transactions:
                text = f"{entry['quantity']}x → {entry['item']} (₱ {entry['total']})"
                item_label = tk.Label(scroll_frame, text=text, font=("Arial", 14), bg="#efebe2",
                                    justify="center", width=50)
                item_label.pack(pady=2)
                total += entry['total']

            total_label = tk.Label(scroll_frame, text=f"Total: ₱ {total}", font=("Arial", 14, "bold"), bg="#efebe2", fg="#333",
                                justify="center", width=50)
            total_label.pack(pady=5)

        # Reset Button
        reset_button = tk.Button(scroll_frame, text="Reset History", font=("Arial", 14, "bold"), bg="#ce2a22", fg="#fff",
                                 command=lambda: self.reset_history(history_window))
        reset_button.pack(padx=240, pady=10, anchor="center")
        
    def reset_total(self):
        """Reset the total amount spent back to 0 in amounts.json"""
        confirm = msgbox.askyesno("Confirm Reset", "Are you sure you want to reset the total amount?")

        if confirm:
            # Reset total and clear entries
            reset_data = {"total": 0, "entries": []}
            self.save_amount_data(reset_data)

            self.total_label.config(text="Total: ₱ 0")

            msgbox.showinfo("Reset Successful", "Total amount has been reset to ₱ 0.")
            
# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryManagement(root)
    root.mainloop()