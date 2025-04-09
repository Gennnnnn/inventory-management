# 📦 Furniture Inventory Management System

A touchscreen-friendly inventory management system built with **Python** and **CustomTkinter**, connected to **Firebase** for real-time syncing (with polling), image-based product display, and simple cashier features.

---

## 🖥️ Features

✅ Fullscreen GUI for kiosk use  
✅ Add, Edit, or Remove inventory items with image and price  
✅ Quantity adjustments with dynamic total amount tracking  
✅ Transaction history with export options  
✅ Firebase integration with polling to auto-sync updates  
✅ Supports image uploading and organized storage  
✅ Daily history tracking and reset

---

## 📁 Project Structure

```
project/
│
├── assets/                  # Uploaded item images
├── inventory/               # JSON storage
│   ├── inventory.json
│   ├── amounts.json
│   └── history.json
│
├── firebase_config.py       # Firebase sync logic and polling
├── InventoryManagement.py   # GUI logic using CustomTkinter
├── main.py                  # Entry point of the application
├── serviceAccountKey.json   # Firebase credentials (DO NOT share publicly)
└── README.md
```

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Gennnnnn/inventory-management.git
cd inventory-management
```

### 2. Install Dependencies

```bash
pip install customtkinter
pip install firebase-admin

```

---

## 🔑 Add Firebase Credentials

1. Go to [Firebase Console](https://console.firebase.google.com/).
2. Select your project > **Project Settings > Service Accounts**
3. Click **"Generate new private key"**
4. Save the file as `serviceAccountKey.json` in the project root.

---

## 🔗 Create Firebase Realtime Database

- In Firebase console, go to **Build > Realtime Database** and click **"Create Database"**.
- Choose **test mode** for development (or apply rules later).

Your Firebase database URL will look like:

```
https://your-project-id-default-rtdb.firebaseio.com/
```

Replace it in `firebase_config.py` if needed.

---

## ▶️ Running the App

From your terminal or IDE:

```bash
python main.py
```

This will:

- Start a background polling thread to sync with Firebase every few seconds.
- Launch the fullscreen CustomTkinter GUI.

---

## ✨ Usage Guide

### 🟢 Adding Items:

- Click **“Add”** button
- Fill in **name, image**, and **price**
- Upload an image via the file picker

### ✏️ Editing Items:

- Click **“Edit”**
- Select item from dropdown
- Update name, price, or image

### 🗑️ Removing Items:

- Click **“Remove”**
- Select item to delete from the dropdown

### 💰 Making Transactions:

- Adjust quantity using + / - buttons
- Press **“Add”** to log the purchase
- View total at top-left

### 📜 Viewing History:

- Click **“History”** to view daily logs
- Press **“Export”** to save as Excel
- Use **“Reset History”** to start fresh

---

## 🛠️ Notes & Tips

- Make sure `assets/` and `inventory/` folders exist, or the app will create them.
- All inventory changes are synced both **locally (JSON)** and to **Firebase**.
- The JSON files act as a local backup in case of internet failure.

---

## 📌 Troubleshooting

### 🔴 Invalid JWT Signature

- Regenerate your Firebase service account key.
- Check your system time and make sure it’s synced.

### 🔴 Polling Doesn’t Update UI

- Ensure the polling thread is running.
- Make sure `gui_update_callback()` is registered in `main.py`.
